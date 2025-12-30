"""
Block Executor - Executes blocks from workflow YAML

This module provides the core execution engine for running workflow blocks.
It handles:
- Sequential and parallel block execution
- Directory state persistence across commands
- Environment variable persistence across commands
- Real-time output streaming
- Command interpolation with configuration variables

Architecture:
- CommandPreparator: Handles command preparation and interpolation
- ProcessExecutor: Manages subprocess execution and output streaming
- StateManager: Tracks and persists directory and environment state
- RemoteExecutor: Handles SSH remote command execution
- LoopExpander: Expands for-loops into individual blocks
- BlockExecutor: Main orchestrator class
"""

import os
import subprocess
import threading
from typing import Dict, Any, List, Tuple
from datetime import datetime
from .colors import Colors
from .command_preparator import CommandPreparator
from .process_executor import ProcessExecutor
from .state_manager import StateManager
from .remote_executor import RemoteExecutor
from .loop_expander import LoopExpander


# ============================================================================
# MAIN BLOCK EXECUTOR
# ============================================================================

class BlockExecutor:
    """
    Main orchestrator class for running workflow blocks.
    
    This class coordinates all aspects of workflow execution by delegating
    to specialized components:
    - CommandPreparator: Prepares commands for execution
    - ProcessExecutor: Manages subprocess execution
    - StateManager: Tracks directory and environment state
    - RemoteExecutor: Handles SSH remote execution
    - LoopExpander: Expands for-loops
    
    Responsibilities:
    - Orchestrate block execution (sequential and parallel)
    - Manage execution results and timing
    - Generate execution summaries
    - Coordinate state persistence across blocks
    """
    
    def __init__(self, config_loader):
        """
        Initialize the block executor and all helper components.
        
        Args:
            config_loader: ConfigLoader instance for variable interpolation
        """
        self.config_loader = config_loader
        self.results = []  # Store execution results for summary
        
        # Initialize helper components
        self.state_manager = StateManager()
        self.command_preparator = CommandPreparator(config_loader)
        self.process_executor = ProcessExecutor(self.state_manager.environment)
        self.remote_executor = RemoteExecutor(config_loader)
        self.loop_expander = LoopExpander(config_loader)
    
    # ========================================================================
    # COMMAND EXECUTION
    # ========================================================================

    
    def execute_command(self, command: str, block_name: str) -> Tuple[bool, str, str]:
        """
        Execute a shell command with full state tracking.
        
        This is the core execution method that:
        1. Prepares the command (interpolation, path resolution)
        2. Executes it with real-time output streaming
        3. Captures directory and environment changes
        4. Returns execution results
        
        Args:
            command: Raw command string from workflow YAML
            block_name: Display name for this command
            
        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        # Prepare the command for execution using CommandPreparator
        prepared_command = self.command_preparator.prepare_command(
            command,
            self.state_manager.current_directory
        )
        
        # Pre-calculate target directory if this is a 'cd' command
        precalculated_target_dir = self.command_preparator.precalculate_target_directory(
            prepared_command,
            self.state_manager.current_directory
        )
        
        # Display execution information
        self._print_execution_header(block_name, prepared_command)
        
        try:
            # Update ProcessExecutor with current environment
            self.process_executor.environment = self.state_manager.environment
            
            # Start the subprocess with appropriate shell
            process = self.process_executor.start_subprocess(prepared_command)
            
            # Stream output in real-time and capture for later processing
            stdout_full, stderr_full = self.process_executor.stream_process_output(process)
            
            # Wait for process to complete and get return code
            returncode = process.wait()
            success = returncode == 0
            
            # Process state changes (directory and environment variables)
            cleaned_stdout = self.state_manager.process_state_changes(
                stdout_full,
                command,
                success,
                precalculated_target_dir
            )
            
            # Show stderr if command failed
            if stderr_full and not success:
                print(Colors.colorize(f"  Error: {stderr_full.strip()}", Colors.RED))
            
            return success, cleaned_stdout, stderr_full
            
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out"
            print(Colors.colorize(f"  Error: {error_msg}", Colors.RED))
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Command execution failed: {e}"
            print(Colors.colorize(f"  Error: {error_msg}", Colors.RED))
            return False, "", error_msg
    
    def _print_execution_header(self, block_name: str, command: str):
        """
        Print colored header with execution information.
        
        Args:
            block_name: Name of the block being executed
            command: Full command string being executed
        """
        print(Colors.colorize(f"  Executing: {block_name}", Colors.CYAN))
        print(Colors.colorize(f"  Command: {command}", Colors.BLUE))
        print(Colors.colorize(
            f"  Working Directory: {self.state_manager.current_directory}",
            Colors.MAGENTA
        ))
    
    # ========================================================================
    # REMOTE EXECUTION
    # ========================================================================
    
    def execute_remote_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a remote SSH command block.
        
        A remote block contains:
        - run-remotely: Dictionary with connection details
          - ip: Remote host IP address
          - user: SSH username
          - pass: SSH password (optional, uses key-based auth if not provided)
          - run: Command to execute remotely
          - log-into: (Optional) Log file path for output capture
        - name: Display name (optional)
        - description: Description for documentation (optional)
        
        Args:
            block: Dictionary containing remote block configuration
            
        Returns:
            Dictionary with execution results
        """
        remote_config = block.get('run-remotely', {})
        
        # Extract remote execution parameters
        ip = remote_config.get('ip', '')
        user = remote_config.get('user', '')
        password = remote_config.get('pass', '')
        command = remote_config.get('run', '')
        log_file = remote_config.get('log-into', '')
        
        # Interpolate variables in all fields
        ip = self.config_loader.interpolate(str(ip))
        user = self.config_loader.interpolate(str(user))
        password = self.config_loader.interpolate(str(password))
        command = self.config_loader.interpolate(str(command))
        if log_file:
            log_file = self.config_loader.interpolate(str(log_file))
        
        # Generate block name
        name = block.get('name', f"Remote: {user}@{ip}: {command[:30]}...")
        description = block.get('description', '')
        
        # Print block header
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_CYAN))
        print(Colors.colorize(f"Block: {name}", Colors.BOLD_CYAN))
        if description:
            print(Colors.colorize(f"Description: {description}", Colors.CYAN))
        print(Colors.colorize(f"  Remote Host: {user}@{ip}", Colors.MAGENTA))
        print(Colors.colorize(f"  Command: {command}", Colors.BLUE))
        if log_file:
            print(Colors.colorize(f"  Log File: {log_file}", Colors.YELLOW))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_CYAN))
        
        # Execute remote command using RemoteExecutor
        start_time = datetime.now()
        
        if log_file:
            # Use remotely.py for log file capture
            success, stdout, stderr = self.remote_executor.execute_with_log_file(
                user, ip, password, command, log_file
            )
        else:
            # Execute directly with SSHLogStreamer for real-time output
            success, stdout, stderr = self.remote_executor.execute_with_streaming(
                user, ip, password, command
            )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Package results
        result = {
            'name': name,
            'description': description,
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'duration': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        # Print status
        status_color = Colors.BOLD_GREEN if success else Colors.BOLD_RED
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(Colors.colorize(f"  Status: {status} (Duration: {duration:.2f}s)", status_color))
        
        # Reload configurations from storage directory after each block execution
        # This allows workflows to update storage YAMLs mid-execution
        self.config_loader.reload_configs()
        
        return result
    
    # ========================================================================
    # BLOCK EXECUTION
    # ========================================================================
    
    def execute_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow block (local or remote).
        
        A block can be either:
        - Local execution: Contains 'run' field
        - Remote execution: Contains 'run-remotely' field
        
        Local block contains:
        - run: The command to execute (required)
        - name: Display name (optional, defaults to truncated command)
        - description: Description for documentation (optional)
        
        Remote block contains:
        - run-remotely: Dictionary with connection details
        - name: Display name (optional)
        - description: Description for documentation (optional)
        
        Args:
            block: Dictionary containing block configuration
            
        Returns:
            Dictionary with execution results including:
            - name: Block name
            - description: Block description
            - success: Whether execution succeeded
            - stdout: Standard output
            - stderr: Standard error
            - duration: Execution time in seconds
            - start_time: ISO format start timestamp
            - end_time: ISO format end timestamp
        """
        # Check if this is a remote execution block
        if 'run-remotely' in block:
            return self.execute_remote_block(block)
        
        # Extract block metadata for local execution
        command = block.get('run', '')
        name = block.get('name', command[:50] + '...' if len(command) > 50 else command)
        description = block.get('description', '')
        
        # Print block header
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_CYAN))
        if name:
            print(Colors.colorize(f"Block: {name}", Colors.BOLD_CYAN))
        if description:
            print(Colors.colorize(f"Description: {description}", Colors.CYAN))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_CYAN))
        
        # Execute command and measure duration
        start_time = datetime.now()
        success, stdout, stderr = self.execute_command(command, name)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Package results
        result = {
            'name': name,
            'description': description,
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'duration': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        # Print status with color coding
        status_color = Colors.BOLD_GREEN if success else Colors.BOLD_RED
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(Colors.colorize(f"  Status: {status} (Duration: {duration:.2f}s)", status_color))
        
        # Reload configurations from storage directory after each block execution
        # This allows workflows to update storage YAMLs mid-execution
        self.config_loader.reload_configs()
        
        return result
    
    # ========================================================================
    # PARALLEL EXECUTION
    # ========================================================================
    
    def execute_parallel_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple blocks in parallel using threading.
        
        All blocks are started simultaneously in separate threads and
        executed concurrently. Results are collected after all threads complete.
        
        Args:
            blocks: List of block dictionaries to execute in parallel
            
        Returns:
            List of execution result dictionaries
        """
        results = []
        threads = []
        
        # Helper function to execute a block and store its result
        def execute_and_store(block: Dict[str, Any], result_list: List[Dict[str, Any]]):
            result = self.execute_block(block)
            result_list.append(result)
        
        
        # Start all blocks in separate threads
        print(Colors.colorize(f"\n{'~'*60}", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"PARALLEL EXECUTION: Starting {len(blocks)} tasks", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"{'~'*60}", Colors.BOLD_YELLOW))
        
        for block in blocks:
            thread = threading.Thread(target=execute_and_store, args=(block, results))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print(Colors.colorize(f"\n{'~'*60}", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"PARALLEL EXECUTION: All {len(blocks)} tasks completed", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"{'~'*60}", Colors.BOLD_YELLOW))
        
        return results
    
    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================
    
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """
        Execute the entire workflow from YAML data.
        
        Processes the workflow's 'blocks' list sequentially, handling both:
        - Regular blocks: Executed one at a time
        - Parallel blocks: Multiple blocks executed concurrently
        
        Args:
            workflow_data: Parsed YAML workflow data containing 'blocks' list
            
        Returns:
            True if all blocks succeeded, False if any failed
        """
        blocks = workflow_data.get('blocks', [])
        
        # Validate workflow has content
        if not blocks:
            print(Colors.colorize("No blocks found in workflow", Colors.YELLOW))
            return True
        
        # Print workflow header
        print(Colors.colorize(f"\n{'#'*60}", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"# WORKFLOW EXECUTION STARTED", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"# Total items: {len(blocks)}", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"{'#'*60}", Colors.BOLD_MAGENTA))
        
        all_success = True
        
        # Process each item in the workflow
        for item in blocks:
            # Handle for-loop block
            if 'for' in item:
                loop_config = item['for']
                # Config reload happens inside loop_expander.expand_for_loop before expansion
                expanded_blocks = self.loop_expander.expand_for_loop(loop_config)
                
                # Execute each expanded block sequentially
                for expanded_block in expanded_blocks:
                    result = self.execute_block(expanded_block)
                    self.results.append(result)
                    
                    if not result['success']:
                        all_success = False
                    
                    # Note: Config reload already happens inside execute_block()
            
            # Handle parallel execution block
            elif 'parallel' in item:
                parallel_blocks = item['parallel']
                
                # Check if parallel block contains a for-loop
                if isinstance(parallel_blocks, dict) and 'for' in parallel_blocks:
                    # Expand the for-loop first using LoopExpander
                    # Config reload happens inside loop_expander.expand_for_loop before expansion
                    loop_config = parallel_blocks['for']
                    parallel_blocks = self.loop_expander.expand_for_loop(loop_config)
                
                # Validate parallel block structure
                if not isinstance(parallel_blocks, list):
                    print("Error: 'parallel' must contain a list of blocks")
                    all_success = False
                    continue
                
                # Execute blocks in parallel
                parallel_results = self.execute_parallel_blocks(parallel_blocks)
                self.results.extend(parallel_results)
                
                # Check if any parallel block failed
                for result in parallel_results:
                    if not result['success']:
                        all_success = False
            
            # Handle regular sequential block (local or remote)
            elif 'run' in item or 'run-remotely' in item:
                result = self.execute_block(item)
                self.results.append(result)
                
                if not result['success']:
                    all_success = False
            
            # Handle malformed blocks
            else:
                print(Colors.colorize(
                    f"Warning: Unrecognized block structure (missing 'run', 'run-remotely', or 'for' field): {item}",
                    Colors.YELLOW
                ))
        
        # Print workflow footer
        print(Colors.colorize(f"\n{'#'*60}", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"# WORKFLOW EXECUTION COMPLETED", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"{'#'*60}", Colors.BOLD_MAGENTA))
        
        # Print execution summary
        self._print_summary()
        
        return all_success
    
    def _print_summary(self):
        """
        Print a summary of workflow execution results.
        
        Displays:
        - Total blocks executed
        - Success/failure counts
        - Total execution time
        - List of failed blocks (if any) with error messages
        """
        if not self.results:
            return
        
        # Print summary header
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_CYAN))
        print(Colors.colorize(f"EXECUTION SUMMARY", Colors.BOLD_CYAN))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_CYAN))
        
        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        failed = total - successful
        total_duration = sum(r['duration'] for r in self.results)
        
        # Print statistics
        print(Colors.colorize(f"Total blocks executed: {total}", Colors.CYAN))
        print(Colors.colorize(f"Successful: {successful}", Colors.GREEN))
        print(Colors.colorize(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN))
        print(Colors.colorize(f"Total duration: {total_duration:.2f}s", Colors.CYAN))
        
        # If there were failures, list them with error details
        if failed > 0:
            print(Colors.colorize(f"\nFailed blocks:", Colors.BOLD_RED))
            for result in self.results:
                if not result['success']:
                    print(Colors.colorize(f"  - {result['name']}", Colors.RED))
                    if result['stderr']:
                        # Truncate long error messages
                        error_preview = result['stderr'][:100]
                        print(Colors.colorize(f"    Error: {error_preview}", Colors.RED))

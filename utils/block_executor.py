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
          - pass: SSH password
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
        Expand a for-loop into individual blocks by iterating over a list.
        
        Supports syntax:
        for:
          individual: item_name
          in: ${config.list_path}
          run: command with ${item_name}
          
        Args:
            loop_config: Dictionary containing for-loop configuration
            
        Returns:
            List of expanded block dictionaries
        """
        # Reload configs before expanding loop to ensure fresh list data
        # This allows workflows to modify the list before the loop executes
        self.config_loader.reload_configs()
        
        individual_var = loop_config.get('individual')
        list_path = loop_config.get('in', '')
        
        if not individual_var or not list_path:
            print(Colors.colorize("Error: for-loop missing 'individual' or 'in' field", Colors.BOLD_RED))
            return []
        
        # Interpolate the list path to get the actual list
        interpolated_path = self.config_loader.interpolate(list_path)
        
        # Get the list from config using dot notation
        list_items = self.config_loader.get_value(list_path.replace('${', '').replace('}', ''))
        
        if not isinstance(list_items, list):
            print(Colors.colorize(f"Error: '{list_path}' does not reference a list", Colors.BOLD_RED))
            return []
        
        expanded_blocks = []
        
        # Iterate over each item in the list
        for item in list_items:
            # Handle for-loops with blocks array (multiple sub-blocks)
            if 'blocks' in loop_config:
                # Process each block in the blocks array
                blocks_array = loop_config['blocks']
                for block_template in blocks_array:
                    # Substitute variables in this block
                    substituted_block = {}
                    for key, value in block_template.items():
                        if isinstance(value, str):
                            if isinstance(item, dict):
                                for field_name, field_value in item.items():
                                    value = value.replace(
                                        f"${{{individual_var}.{field_name}}}",
                                        str(field_value)
                                    )
                            else:
                                value = value.replace(f"${{{individual_var}}}", str(item))
                            substituted_block[key] = value
                        elif isinstance(value, dict):
                            # Handle nested structures like for loops or run-remotely
                            if key == 'for':
                                # This is a nested for-loop, need to substitute the 'in' path
                                nested_for = dict(value)
                                nested_in_path = nested_for.get('in', '')
                                if isinstance(item, dict):
                                    for field_name, field_value in item.items():
                                        nested_in_path = nested_in_path.replace(
                                            f"${{{individual_var}.{field_name}}}",
                                            str(field_value)
                                        )
                                else:
                                    nested_in_path = nested_in_path.replace(f"${{{individual_var}}}", str(item))
                                nested_for['in'] = nested_in_path
                                substituted_block[key] = nested_for
                            else:
                                substituted_block[key] = self._substitute_in_dict(value, individual_var, item)
                        else:
                            substituted_block[key] = value
                    
                    expanded_blocks.append(substituted_block)
            # Handle nested for-loops (legacy syntax without blocks array)
            elif 'for' in loop_config:
                # If outer loop has a 'run' command, add it first as a separate block
                # This ensures outer run executes before nested loop iterations
                if 'run' in loop_config:
                    outer_run_block = {}
                    outer_run = loop_config['run']
                    if isinstance(item, dict):
                        for field_name, field_value in item.items():
                            outer_run = outer_run.replace(
                                f"${{{individual_var}.{field_name}}}",
                                str(field_value)
                            )
                    else:
                        outer_run = outer_run.replace(f"${{{individual_var}}}", str(item))
                    outer_run_block['run'] = outer_run
                    expanded_blocks.append(outer_run_block)
                
                # This is a nested loop - process outer item first, then expand inner loop
                nested_loop_config = loop_config['for']
                
                # Get the nested list - could be a path or direct value from outer item
                nested_in_path = nested_loop_config.get('in', '')
                nested_list = None
                
                # Check if nested_in_path references a field in the current item (dict)
                if isinstance(item, dict):
                    # Try to extract field name from ${individual_var.field} pattern
                    import re
                    pattern = f"\\${{{individual_var}\\.([^}}]+)\\}}"
                    match = re.search(pattern, nested_in_path)
                    if match:
                        field_name = match.group(1)
                        if field_name in item:
                            # Direct access to the nested list from current item
                            nested_list = item[field_name]
                
                # If we found a direct list, create a temporary config
                if nested_list is not None and isinstance(nested_list, list):
                    # Create expanded blocks directly from the nested list
                    nested_individual = nested_loop_config.get('individual')
                    nested_blocks = []
                    
                    for nested_item in nested_list:
                        nested_block = {}
                        for key, value in nested_loop_config.items():
                            if key in ['individual', 'in', 'for']:
                                continue
                            
                            if isinstance(value, str):
                                if isinstance(nested_item, dict):
                                    substituted = value
                                    for nf, nv in nested_item.items():
                                        substituted = substituted.replace(f"${{{nested_individual}.{nf}}}", str(nv))
                                    nested_block[key] = substituted
                                else:
                                    nested_block[key] = value.replace(f"${{{nested_individual}}}", str(nested_item))
                            elif isinstance(value, dict):
                                nested_block[key] = self._substitute_in_dict(value, nested_individual, nested_item)
                        nested_blocks.append(nested_block)
                else:
                    # Path-based nested loop - substitute and resolve
                    if isinstance(item, dict):
                        for field_name, field_value in item.items():
                            nested_in_path = nested_in_path.replace(
                                f"${{{individual_var}.{field_name}}}",
                                str(field_value)
                            )
                    else:
                        nested_in_path = nested_in_path.replace(f"${{{individual_var}}}", str(item))
                    
                    # Update nested loop config with substituted path
                    nested_loop_config_copy = dict(nested_loop_config)
                    nested_loop_config_copy['in'] = nested_in_path
                    
                    # Recursively expand nested loop
                    nested_blocks = self._expand_for_loop(nested_loop_config_copy)
                
                # For each nested block, also substitute the outer variable
                for nested_block in nested_blocks:
                    final_block = {}
                    for key, value in nested_block.items():
                        if isinstance(value, str):
                            if isinstance(item, dict):
                                for field_name, field_value in item.items():
                                    value = value.replace(
                                        f"${{{individual_var}.{field_name}}}",
                                        str(field_value)
                                    )
                            else:
                                value = value.replace(f"${{{individual_var}}}", str(item))
                            final_block[key] = value
                        elif isinstance(value, dict):
                            final_block[key] = self._substitute_in_dict(value, individual_var, item)
                        else:
                            final_block[key] = value
                    
                    expanded_blocks.append(final_block)
            else:
                # No nested loop - simple expansion
                block = {}
                
                # Process each key in the loop config
                for key, value in loop_config.items():
                    if key in ['individual', 'in']:
                        continue  # Skip loop control keys
                    
                    # Substitute the individual variable in the value
                    if isinstance(value, str):
                        # Handle both simple strings and dicts
                        if isinstance(item, dict):
                            # Item is a dict - replace ${individual_var.field} patterns
                            substituted_value = value
                            for field_name, field_value in item.items():
                                substituted_value = substituted_value.replace(
                                    f"${{{individual_var}.{field_name}}}",
                                    str(field_value)
                                )
                            block[key] = substituted_value
                        else:
                            # Item is a simple value - replace ${individual_var}
                            block[key] = value.replace(f"${{{individual_var}}}", str(item))
                    elif isinstance(value, dict):
                        # Handle nested dictionaries (like run-remotely config)
                        block[key] = self._substitute_in_dict(value, individual_var, item)
            
                expanded_blocks.append(block)
        
        return expanded_blocks
    
    def _substitute_in_dict(self, data: Dict[str, Any], var_name: str, var_value: Any) -> Dict[str, Any]:
        """
        Recursively substitute variable references in a dictionary.
        
        Args:
            data: Dictionary to process
            var_name: Variable name to substitute
            var_value: Value to substitute (can be dict or simple value)
            
        Returns:
            Dictionary with substitutions applied
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                if isinstance(var_value, dict):
                    # Replace ${var_name.field} patterns
                    substituted = value
                    for field_name, field_val in var_value.items():
                        substituted = substituted.replace(
                            f"${{{var_name}.{field_name}}}",
                            str(field_val)
                        )
                    result[key] = substituted
                else:
                    # Replace ${var_name}
                    result[key] = value.replace(f"${{{var_name}}}", str(var_value))
            elif isinstance(value, dict):
                result[key] = self._substitute_in_dict(value, var_name, var_value)
            elif isinstance(value, list):
                result[key] = [self._substitute_in_dict(item, var_name, var_value) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        
        return result
    
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

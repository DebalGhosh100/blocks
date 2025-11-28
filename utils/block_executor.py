"""
Block Executor - Executes blocks from workflow YAML

This module provides the core execution engine for running workflow blocks.
It handles:
- Sequential and parallel block execution
- Directory state persistence across commands
- Environment variable persistence across commands
- Real-time output streaming
- Command interpolation with configuration variables
"""

import os
import subprocess
import threading
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from .colors import Colors


class BlockExecutor:
    """
    Main executor class for running workflow blocks.
    
    Maintains stateful execution context including:
    - Current working directory
    - Environment variables
    - Execution results and timing
    """
    
    def __init__(self, config_loader):
        """
        Initialize the block executor.
        
        Args:
            config_loader: ConfigLoader instance for variable interpolation
        """
        self.config_loader = config_loader
        self.results = []  # Store execution results for summary
        self.current_directory = os.getcwd()  # Track working directory changes
        self.environment = os.environ.copy()  # Track environment variable changes
    
    def _precalculate_target_directory(self, command: str) -> Optional[str]:
        """
        Pre-calculate the target directory for 'cd' commands.
        
        This handles compound commands like "cd dir && command" by extracting
        just the directory path before shell operators (&&, ||, ;, |).
        
        Args:
            command: The interpolated command string
            
        Returns:
            Absolute normalized path to target directory, or None if not a cd command
        """
        if not command.strip().startswith('cd '):
            return None
        
        # Split command into 'cd' and everything after
        cd_parts = command.strip().split(None, 1)
        if len(cd_parts) <= 1:
            return None
        
        # Extract the directory path (everything after 'cd' but before operators)
        target_dir = cd_parts[1].strip()
        
        # Split by shell operators to get just the directory path
        # Handles: &&, ||, ;, |
        dir_match = re.split(r'\s*(?:&&|\|\||[;|])\s*', target_dir, maxsplit=1)
        if dir_match:
            target_dir = dir_match[0].strip()
        
        # Resolve relative paths to absolute paths
        if not os.path.isabs(target_dir):
            target_dir = os.path.join(self.current_directory, target_dir)
        
        # Normalize to resolve .. and . in paths
        return os.path.normpath(target_dir)
    
    def _prepare_command(self, command: str) -> str:
        """
        Prepare command for execution by interpolating variables and fixing paths.
        
        Args:
            command: Raw command string from YAML
            
        Returns:
            Fully prepared command string ready for execution
        """
        # Step 1: Interpolate configuration variables (${var.path} -> actual values)
        interpolated_command = self.config_loader.interpolate(command)
        
        # Step 2: Replace remotely.py with absolute path if framework directory is set
        framework_dir = os.environ.get('BLOCKS_FRAMEWORK_DIR')
        if framework_dir:
            interpolated_command = interpolated_command.replace(
                'remotely.py',
                os.path.join(framework_dir, 'remotely.py')
            )
        
        # Step 3: Prepend 'cd' to current directory to ensure correct working directory
        # This maintains state between commands
        interpolated_command = f"cd {self.current_directory} && {interpolated_command}"
        
        return interpolated_command
    
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
        # Prepare the command for execution
        interpolated_command = self._prepare_command(command)
        
        # Pre-calculate target directory if this is a 'cd' command
        precalculated_target_dir = self._precalculate_target_directory(interpolated_command)
        
        # Display execution information
        self._print_execution_header(block_name, interpolated_command)
        
        try:
            # Start the subprocess with appropriate shell
            process = self._start_subprocess(interpolated_command)
            
            # Stream output in real-time and capture for later processing
            stdout_full, stderr_full = self._stream_process_output(process)
            
            # Wait for process to complete and get return code
            returncode = process.wait()
            success = returncode == 0
            
            # Process state changes (directory and environment variables)
            cleaned_stdout = self._process_state_changes(
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
        print(Colors.colorize(f"  Working Directory: {self.current_directory}", Colors.MAGENTA))
    
    def _start_subprocess(self, command: str) -> subprocess.Popen:
        """
        Start a subprocess with appropriate shell for the current platform.
        
        For Windows: Uses PowerShell with PWD capture
        For Unix: Uses Bash with PWD and environment capture
        
        Args:
            command: Prepared command string
            
        Returns:
            subprocess.Popen instance
        """
        if os.name == 'nt':
            # Windows: Use PowerShell for better command support
            # Append command to print working directory after execution
            pwd_command = f"{command}; if ($?) {{ Get-Location | Select-Object -ExpandProperty Path }}"
            return subprocess.Popen(
                ['powershell.exe', '-Command', pwd_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
        else:
            # Unix: Use bash with environment and PWD capture
            # Special markers (__BLOCKS_PWD__, __BLOCKS_ENV__) separate output sections
            # Ensure command ends with newline before appending tracking code
            command_normalized = command.rstrip() + '\n'
            env_capture_command = (
                f"{command_normalized}"
                f"if [ $? -eq 0 ]; then "
                f"echo '__BLOCKS_PWD__'; pwd; "
                f"echo '__BLOCKS_ENV__'; export -p; "
                f"fi"
            )
            return subprocess.Popen(
                env_capture_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                executable='/bin/bash',
                env=self.environment  # Use persistent environment
            )
    
    def _should_filter_line(self, line: str) -> bool:
        """
        Determine if a line should be filtered from output display.
        
        Filters out internal markers and environment variable declarations
        to keep output clean for users.
        
        Args:
            line: Line of output to check
            
        Returns:
            True if line should be filtered (not displayed), False otherwise
        """
        stripped = line.strip()
        return (
            stripped in ['__BLOCKS_PWD__', '__BLOCKS_ENV__'] or
            stripped.startswith('declare -x ')
        )
    
    def _stream_process_output(self, process: subprocess.Popen) -> Tuple[str, str]:
        """
        Stream process output in real-time while capturing for later use.
        
        This function:
        1. Reads output as it's produced (real-time streaming)
        2. Filters internal markers from display
        3. Captures all output for later processing
        
        Args:
            process: Running subprocess instance
            
        Returns:
            Tuple of (stdout_full: str, stderr_full: str)
        """
        stdout_lines = []
        stderr_lines = []
        
        if os.name != 'nt':
            # Unix: Use select() for efficient multiplexed I/O
            import select
            
            while True:
                # Check if process has finished
                if process.poll() is not None:
                    # Read any remaining buffered output
                    remaining_out = process.stdout.read()
                    remaining_err = process.stderr.read()
                    
                    if remaining_out:
                        for line in remaining_out.splitlines(keepends=True):
                            if not self._should_filter_line(line):
                                print(f"  {line.rstrip()}")
                            stdout_lines.append(line)
                    
                    if remaining_err:
                        for line in remaining_err.splitlines(keepends=True):
                            if line.strip():
                                print(f"  {line.rstrip()}")
                            stderr_lines.append(line)
                    break
                
                # Wait for data on stdout or stderr (with 0.1s timeout)
                readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
                
                # Read from whichever stream has data
                for stream in readable:
                    line = stream.readline()
                    if line:
                        # Filter internal markers from display
                        if not self._should_filter_line(line):
                            print(f"  {line.rstrip()}")
                        
                        # Store all output for processing
                        if stream == process.stdout:
                            stdout_lines.append(line)
                        else:
                            stderr_lines.append(line)
        else:
            # Windows: Simpler line-by-line reading (no select() available)
            while True:
                line = process.stdout.readline()
                if line:
                    if not self._should_filter_line(line):
                        print(f"  {line.rstrip()}")
                    stdout_lines.append(line)
                elif process.poll() is not None:
                    break
            
            # Read stderr after process completes
            stderr_output = process.stderr.read()
            if stderr_output:
                for line in stderr_output.splitlines(keepends=True):
                    if line.strip():
                        print(f"  {line.rstrip()}")
                    stderr_lines.append(line)
        
        # Combine all captured lines
        return ''.join(stdout_lines), ''.join(stderr_lines)
    
    def _process_state_changes(
        self,
        stdout: str,
        original_command: str,
        success: bool,
        precalculated_dir: Optional[str]
    ) -> str:
        """
        Process state changes from command execution.
        
        Extracts and applies:
        - Working directory changes (from PWD)
        - Environment variable changes (from export -p)
        
        Args:
            stdout: Full stdout from command execution
            original_command: Original command string (before preparation)
            success: Whether command executed successfully
            precalculated_dir: Pre-calculated target directory (for cd commands)
            
        Returns:
            Cleaned stdout with internal markers removed
        """
        # If no PWD marker, return stdout as-is
        if '__BLOCKS_PWD__' not in stdout:
            return stdout
        
        # Split output at PWD marker
        parts = stdout.split('__BLOCKS_PWD__')
        cleaned_stdout = parts[0]  # Everything before marker is actual output
        
        if len(parts) <= 1:
            return cleaned_stdout
        
        remainder = parts[1]
        
        # Check if we also have environment capture
        if '__BLOCKS_ENV__' in remainder:
            env_parts = remainder.split('__BLOCKS_ENV__')
            pwd_section = env_parts[0].strip()
            
            # Update directory if command succeeded
            if success:
                self._update_directory_from_pwd(pwd_section, original_command, precalculated_dir)
            
            # Update environment variables if captured
            if success and len(env_parts) > 1:
                env_output = env_parts[1]
                self._update_environment_from_export(env_output)
        else:
            # Only PWD capture (no environment)
            pwd_output = remainder.strip().split('\n')[-1]
            if success:
                self._update_directory_from_pwd_simple(pwd_output, original_command, precalculated_dir)
        
        return cleaned_stdout
    
    def _update_directory_from_pwd(
        self,
        pwd_section: str,
        original_command: str,
        precalculated_dir: Optional[str]
    ):
        """
        Update current directory from PWD output.
        
        Always prefers actual PWD output over pre-calculated paths for accuracy.
        
        Args:
            pwd_section: Section of output containing PWD
            original_command: Original command (before preparation)
            precalculated_dir: Pre-calculated directory (fallback)
        """
        # Try to extract actual PWD from output
        pwd_detected = False
        for line in pwd_section.split('\n'):
            line = line.strip()
            if line and os.path.isdir(line):
                old_dir = self.current_directory
                self.current_directory = line
                pwd_detected = True
                if old_dir != self.current_directory:
                    print(Colors.colorize(
                        f"  Changed directory to: {self.current_directory}",
                        Colors.GREEN
                    ))
                break
        
        # Fallback to pre-calculated directory if PWD detection failed
        if not pwd_detected and original_command.strip().startswith('cd ') and precalculated_dir:
            old_dir = self.current_directory
            self.current_directory = precalculated_dir
            if old_dir != self.current_directory:
                print(Colors.colorize(
                    f"  Changed directory to: {self.current_directory}",
                    Colors.GREEN
                ))
    
    def _update_directory_from_pwd_simple(
        self,
        pwd_output: str,
        original_command: str,
        precalculated_dir: Optional[str]
    ):
        """
        Update directory from simple PWD output (Windows or fallback).
        
        Args:
            pwd_output: PWD output string
            original_command: Original command
            precalculated_dir: Pre-calculated directory (fallback)
        """
        if pwd_output and os.path.isdir(pwd_output):
            # Use actual PWD output
            old_dir = self.current_directory
            self.current_directory = pwd_output
            if old_dir != self.current_directory:
                print(Colors.colorize(
                    f"  Changed directory to: {self.current_directory}",
                    Colors.GREEN
                ))
        elif original_command.strip().startswith('cd ') and precalculated_dir:
            # Fallback to pre-calculated directory
            old_dir = self.current_directory
            self.current_directory = precalculated_dir
            if old_dir != self.current_directory:
                print(Colors.colorize(
                    f"  Changed directory to: {self.current_directory}",
                    Colors.GREEN
                ))
    
    def _update_environment_from_export(self, export_output: str):
        """
        Parse 'export -p' output and update persistent environment variables.
        
        This captures environment changes from commands like 'source' or 'export'
        and maintains them across subsequent commands.
        
        Handles various formats:
        - declare -x VAR="value"
        - declare -x VAR='value'
        - declare -x VAR=value
        - export VAR="value"
        
        Args:
            export_output: Output from 'export -p' command
        """
        # Regex pattern to match environment variable declarations
        # Captures: VAR_NAME and value (with or without quotes)
        pattern = r'(?:declare -x |export )([A-Za-z_][A-Za-z0-9_]*)=(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'
        
        for line in export_output.split('\n'):
            match = re.match(pattern, line)
            if match:
                var_name = match.group(1)
                # Extract value from whichever capture group matched
                var_value = match.group(2) or match.group(3) or match.group(4) or ''
                
                # Update our persistent environment
                self.environment[var_name] = var_value
    
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
        
        # Execute remote command
        start_time = datetime.now()
        
        if log_file:
            # Use remotely.py for log file capture
            success, stdout, stderr = self._execute_remote_with_log(
                user, ip, password, command, log_file
            )
        else:
            # Execute directly with SSHLogStreamer for real-time output
            success, stdout, stderr = self._execute_remote_streaming(
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
    
    def _execute_remote_with_log(
        self,
        user: str,
        ip: str,
        password: str,
        command: str,
        log_file: str
    ) -> Tuple[bool, str, str]:
        """
        Execute remote command using remotely.py subprocess.
        
        Args:
            user: SSH username
            ip: Remote host IP
            password: SSH password
            command: Command to execute
            log_file: Path to log file
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        import sys
        from pathlib import Path
        
        # Get remotely.py path from framework directory
        framework_dir = os.environ.get('BLOCKS_FRAMEWORK_DIR', os.path.dirname(os.path.dirname(__file__)))
        remotely_script = str(Path(framework_dir) / 'remotely.py')
        
        # Build remotely.py command
        ssh_url = f"{user}@{ip}"
        remotely_cmd = [
            sys.executable,  # Use same Python interpreter
            remotely_script,
            ssh_url,
            password,
            command,
            log_file
        ]
        
        try:
            # Execute remotely.py as subprocess
            process = subprocess.Popen(
                remotely_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(f"  {line.rstrip()}")
            
            # Wait for completion
            process.wait()
            
            # Read any stderr
            stderr_output = process.stderr.read()
            
            success = process.returncode == 0
            return success, f"Log written to {log_file}", stderr_output
            
        except Exception as e:
            error_msg = f"Failed to execute remotely.py: {e}"
            print(Colors.colorize(f"  Error: {error_msg}", Colors.RED))
            return False, "", error_msg
    
    def _execute_remote_streaming(
        self,
        user: str,
        ip: str,
        password: str,
        command: str
    ) -> Tuple[bool, str, str]:
        """
        Execute remote command with real-time streaming (no log file).
        
        Args:
            user: SSH username
            ip: Remote host IP
            password: SSH password
            command: Command to execute
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        from .ssh_log_streamer import SSHLogStreamer
        
        # Create SSH streamer without log file
        ssh_url = f"{user}@{ip}"
        
        # Create temporary log file for capture
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp:
            temp_log = tmp.name
        
        try:
            # Use SSHLogStreamer
            streamer = SSHLogStreamer(
                ssh_url=ssh_url,
                password=password,
                command=command,
                log_file=temp_log,
                workflow_dir=os.getcwd()
            )
            
            # Connect
            if not streamer.connect():
                return False, "", "Failed to connect to remote host"
            
            # Stream logs (will print to console)
            success = streamer.stream_logs()
            
            # Read captured output
            with open(temp_log, 'r') as f:
                output = f.read()
            
            # Cleanup
            streamer.close()
            os.unlink(temp_log)
            
            return success, output, ""
            
        except Exception as e:
            error_msg = f"Remote execution failed: {e}"
            print(Colors.colorize(f"  Error: {error_msg}", Colors.RED))
            # Cleanup temp file
            if os.path.exists(temp_log):
                os.unlink(temp_log)
            return False, "", error_msg
    
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
    
    def _expand_for_loop(self, loop_config: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            # Handle nested for-loops
            if 'for' in loop_config:
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
                    
                    # Add run command from outer loop if exists
                    if 'run' in loop_config and 'run' not in final_block:
                        outer_run = loop_config['run']
                        if isinstance(item, dict):
                            for field_name, field_value in item.items():
                                outer_run = outer_run.replace(
                                    f"${{{individual_var}.{field_name}}}",
                                    str(field_value)
                                )
                        else:
                            outer_run = outer_run.replace(f"${{{individual_var}}}", str(item))
                        final_block['run'] = outer_run
                    
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
    
    def execute_parallel_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple blocks concurrently using threads.
        
        This allows independent tasks to run simultaneously, improving
        performance for I/O-bound operations (downloads, remote commands, etc.).
        
        Note: Due to Python's GIL, CPU-bound tasks won't see speedup.
        
        For remote execution blocks in parallel, the 'log-into' field is mandatory
        to prevent output interleaving.
        
        Args:
            blocks: List of block dictionaries to execute in parallel
            
        Returns:
            List of execution results in the same order as input blocks
        """
        # Validate remote blocks have log-into field
        for i, block in enumerate(blocks):
            if 'run-remotely' in block:
                remote_config = block.get('run-remotely', {})
                if not remote_config.get('log-into'):
                    error_msg = f"Parallel remote execution block #{i+1} missing required 'log-into' field"
                    print(Colors.colorize(f"Error: {error_msg}", Colors.BOLD_RED))
                    # Return error result for this block
                    return [{
                        'name': f"Parallel block #{i+1}",
                        'description': '',
                        'success': False,
                        'stdout': '',
                        'stderr': error_msg,
                        'duration': 0,
                        'start_time': datetime.now().isoformat(),
                        'end_time': datetime.now().isoformat()
                    }]
        
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"PARALLEL EXECUTION - {len(blocks)} blocks", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_YELLOW))
        
        # Pre-allocate results list to maintain order
        results = [None] * len(blocks)
        threads = []
        
        def execute_and_store(index: int, block: Dict[str, Any]):
            """
            Wrapper function to execute a block and store its result.
            
            Args:
                index: Position in results list
                block: Block to execute
            """
            results[index] = self.execute_block(block)
        
        # Launch all threads
        for i, block in enumerate(blocks):
            thread = threading.Thread(
                target=execute_and_store,
                args=(i, block),
                daemon=False  # Ensure threads complete before program exits
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"PARALLEL EXECUTION COMPLETED", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_YELLOW))
        
        return results
    
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
                expanded_blocks = self._expand_for_loop(loop_config)
                
                # Execute each expanded block sequentially
                for expanded_block in expanded_blocks:
                    result = self.execute_block(expanded_block)
                    self.results.append(result)
                    
                    if not result['success']:
                        all_success = False
            
            # Handle parallel execution block
            elif 'parallel' in item:
                parallel_blocks = item['parallel']
                
                # Check if parallel block contains a for-loop
                if isinstance(parallel_blocks, dict) and 'for' in parallel_blocks:
                    # Expand the for-loop first
                    loop_config = parallel_blocks['for']
                    parallel_blocks = self._expand_for_loop(loop_config)
                
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

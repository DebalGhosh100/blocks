"""
Block Executor - Executes blocks from workflow YAML
"""

import os
import subprocess
import threading
from typing import Dict, Any, List, Tuple
from datetime import datetime
from .colors import Colors


class BlockExecutor:
    """Executes blocks from workflow YAML"""
    
    def __init__(self, config_loader):
        self.config_loader = config_loader
        self.results = []
        self.current_directory = os.getcwd()  # Track current working directory
    
    def execute_command(self, command: str, block_name: str) -> Tuple[bool, str, str]:
        """
        Execute a shell command and return success status, stdout, stderr
        """
        # Interpolate variables in command
        interpolated_command = self.config_loader.interpolate(command)
        
        # Pre-calculate target directory for cd commands
        precalculated_target_dir = None
        if interpolated_command.strip().startswith('cd '):
            # Extract the directory path
            cd_parts = interpolated_command.strip().split(None, 1)
            if len(cd_parts) > 1:
                target_dir = cd_parts[1].strip()
                # Resolve the target directory relative to current directory
                if not os.path.isabs(target_dir):
                    target_dir = os.path.join(self.current_directory, target_dir)
                # Normalize the path to resolve .. and .
                precalculated_target_dir = os.path.normpath(target_dir)
        
        # Replace remotely.py with full path if framework directory is available
        framework_dir = os.environ.get('BLOCKS_FRAMEWORK_DIR')
        if framework_dir:
            # Replace standalone remotely.py references with full path
            interpolated_command = interpolated_command.replace(
                'remotely.py',
                os.path.join(framework_dir, 'remotely.py')
            )
        
        # Prepend cd to current directory for all commands to ensure proper working directory context
        interpolated_command = f"cd {self.current_directory} && {interpolated_command}"
        
        print(Colors.colorize(f"  Executing: {block_name}", Colors.CYAN))
        print(Colors.colorize(f"  Command: {interpolated_command}", Colors.BLUE))
        print(Colors.colorize(f"  Working Directory: {self.current_directory}", Colors.MAGENTA))
        
        try:
            # Execute command with real-time output streaming
            if os.name == 'nt':
                # Use PowerShell for better command support
                # Add command to print working directory at the end
                pwd_command = f"{interpolated_command}; if ($?) {{ Get-Location | Select-Object -ExpandProperty Path }}"
                process = subprocess.Popen(
                    ['powershell.exe', '-Command', pwd_command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
            else:
                # Use bash on Unix-like systems
                # Add command to print working directory at the end
                # Use a special marker to separate output from pwd
                pwd_command = f"{interpolated_command}; if [ $? -eq 0 ]; then echo '__BLOCKS_PWD__'; pwd; fi"
                process = subprocess.Popen(
                    pwd_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    executable='/bin/bash'
                )
            
            # Stream output in real-time from both stdout and stderr
            import select
            stdout_lines = []
            stderr_lines = []
            
            # For Unix-like systems, use select to read from both streams
            if os.name != 'nt':
                while True:
                    # Check if process is still running
                    if process.poll() is not None:
                        # Process ended, read remaining output
                        remaining_out = process.stdout.read()
                        remaining_err = process.stderr.read()
                        if remaining_out:
                            for line in remaining_out.splitlines(keepends=True):
                                if line.strip() and line.strip() != '__BLOCKS_PWD__':
                                    print(f"  {line.rstrip()}")
                                stdout_lines.append(line)
                        if remaining_err:
                            for line in remaining_err.splitlines(keepends=True):
                                if line.strip():
                                    print(f"  {line.rstrip()}")
                                stderr_lines.append(line)
                        break
                    
                    # Use select to check which streams have data
                    readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
                    
                    for stream in readable:
                        line = stream.readline()
                        if line:
                            # Don't print the __BLOCKS_PWD__ marker
                            if line.strip() != '__BLOCKS_PWD__':
                                print(f"  {line.rstrip()}")
                            
                            if stream == process.stdout:
                                stdout_lines.append(line)
                            else:
                                stderr_lines.append(line)
            else:
                # For Windows, read stdout line by line (stderr handling is limited)
                while True:
                    line = process.stdout.readline()
                    if line:
                        if line.strip() != '__BLOCKS_PWD__':
                            print(f"  {line.rstrip()}")
                        stdout_lines.append(line)
                    elif process.poll() is not None:
                        break
                
                # Read any remaining stderr
                stderr_output = process.stderr.read()
                if stderr_output:
                    for line in stderr_output.splitlines(keepends=True):
                        if line.strip():
                            print(f"  {line.rstrip()}")
                        stderr_lines.append(line)
            
            # Get return code
            returncode = process.wait()
            success = returncode == 0
            
            # Combine output
            stdout_full = ''.join(stdout_lines)
            stderr_full = ''.join(stderr_lines)
            
            # Store the cleaned stdout
            cleaned_stdout = stdout_full
            
            # Remove the __BLOCKS_PWD__ marker and pwd output from display
            if '__BLOCKS_PWD__' in stdout_full:
                output_parts = stdout_full.split('__BLOCKS_PWD__')
                cleaned_stdout = output_parts[0]
            
            # For explicit cd commands, use the pre-calculated target directory
            if success and command.strip().startswith('cd ') and precalculated_target_dir:
                old_dir = self.current_directory
                self.current_directory = precalculated_target_dir
                if old_dir != self.current_directory:
                    print(Colors.colorize(f"  Changed directory to: {self.current_directory}", Colors.GREEN))
            # For non-cd commands, detect directory changes from PWD output
            elif success and '__BLOCKS_PWD__' in stdout_full:
                # Split output to get the PWD
                output_parts = stdout_full.split('__BLOCKS_PWD__')
                if len(output_parts) > 1:
                    # Get the last line after the marker (the pwd output)
                    pwd_output = output_parts[1].strip().split('\n')[-1]
                    if pwd_output and os.path.isdir(pwd_output):
                        old_dir = self.current_directory
                        self.current_directory = pwd_output
                        if old_dir != self.current_directory:
                            print(Colors.colorize(f"  Changed directory to: {self.current_directory}", Colors.GREEN))
            
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
    
    def execute_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single block"""
        command = block.get('run', '')
        name = block.get('name', command[:50] + '...' if len(command) > 50 else command)
        description = block.get('description', '')
        
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_CYAN))
        if name:
            print(Colors.colorize(f"Block: {name}", Colors.BOLD_CYAN))
        if description:
            print(Colors.colorize(f"Description: {description}", Colors.CYAN))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_CYAN))
        
        start_time = datetime.now()
        success, stdout, stderr = self.execute_command(command, name)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
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
        
        status_color = Colors.BOLD_GREEN if success else Colors.BOLD_RED
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(Colors.colorize(f"  Status: {status} (Duration: {duration:.2f}s)", status_color))
        
        return result
    
    def execute_parallel_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple blocks in parallel using threads"""
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"PARALLEL EXECUTION - {len(blocks)} blocks", Colors.BOLD_YELLOW))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_YELLOW))
        
        results = [None] * len(blocks)
        threads = []
        
        def execute_and_store(index: int, block: Dict[str, Any]):
            """Wrapper to execute block and store result"""
            results[index] = self.execute_block(block)
        
        # Start all threads
        for i, block in enumerate(blocks):
            thread = threading.Thread(
                target=execute_and_store,
                args=(i, block),
                daemon=False
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
        """Execute the entire workflow"""
        blocks = workflow_data.get('blocks', [])
        
        if not blocks:
            print(Colors.colorize("No blocks found in workflow", Colors.YELLOW))
            return True
        
        print(Colors.colorize(f"\n{'#'*60}", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"# WORKFLOW EXECUTION STARTED", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"# Total items: {len(blocks)}", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"{'#'*60}", Colors.BOLD_MAGENTA))
        
        all_success = True
        
        for item in blocks:
            # Check if this is a parallel block
            if 'parallel' in item:
                parallel_blocks = item['parallel']
                if not isinstance(parallel_blocks, list):
                    print("Error: 'parallel' must contain a list of blocks")
                    all_success = False
                    continue
                
                # Execute parallel blocks
                parallel_results = self.execute_parallel_blocks(parallel_blocks)
                self.results.extend(parallel_results)
                
                # Check if any parallel block failed
                for result in parallel_results:
                    if not result['success']:
                        all_success = False
            
            # Regular sequential block
            elif 'run' in item:
                result = self.execute_block(item)
                self.results.append(result)
                
                if not result['success']:
                    all_success = False
            
            else:
                print(Colors.colorize(f"Warning: Unrecognized block structure (missing 'run' field): {item}", Colors.YELLOW))
        
        print(Colors.colorize(f"\n{'#'*60}", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"# WORKFLOW EXECUTION COMPLETED", Colors.BOLD_MAGENTA))
        print(Colors.colorize(f"{'#'*60}", Colors.BOLD_MAGENTA))
        
        # Print summary
        self._print_summary()
        
        return all_success
    
    def _print_summary(self):
        """Print execution summary"""
        if not self.results:
            return
        
        print(Colors.colorize(f"\n{'='*60}", Colors.BOLD_CYAN))
        print(Colors.colorize(f"EXECUTION SUMMARY", Colors.BOLD_CYAN))
        print(Colors.colorize(f"{'='*60}", Colors.BOLD_CYAN))
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        failed = total - successful
        total_duration = sum(r['duration'] for r in self.results)
        
        print(Colors.colorize(f"Total blocks executed: {total}", Colors.CYAN))
        print(Colors.colorize(f"Successful: {successful}", Colors.GREEN))
        print(Colors.colorize(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN))
        print(Colors.colorize(f"Total duration: {total_duration:.2f}s", Colors.CYAN))
        
        if failed > 0:
            print(Colors.colorize(f"\nFailed blocks:", Colors.BOLD_RED))
            for result in self.results:
                if not result['success']:
                    print(Colors.colorize(f"  - {result['name']}", Colors.RED))
                    if result['stderr']:
                        print(Colors.colorize(f"    Error: {result['stderr'][:100]}", Colors.RED))

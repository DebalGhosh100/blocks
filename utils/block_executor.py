"""
Block Executor - Executes blocks from workflow YAML
"""

import os
import subprocess
import threading
from typing import Dict, Any, List, Tuple
from datetime import datetime


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
        
        # Check if command contains 'cd' to update current directory tracking
        # Extract target directory from cd command
        if interpolated_command.strip().startswith('cd '):
            # Extract the directory path
            cd_parts = interpolated_command.strip().split(None, 1)
            if len(cd_parts) > 1:
                target_dir = cd_parts[1].strip()
                # Resolve the target directory relative to current directory
                if not os.path.isabs(target_dir):
                    target_dir = os.path.join(self.current_directory, target_dir)
                # Normalize the path
                target_dir = os.path.normpath(target_dir)
        
        # Replace remotely.py with full path if framework directory is available
        framework_dir = os.environ.get('BLOCKS_FRAMEWORK_DIR')
        if framework_dir:
            # Replace standalone remotely.py references with full path
            interpolated_command = interpolated_command.replace(
                'remotely.py',
                os.path.join(framework_dir, 'remotely.py')
            )
        
        # Prepend cd to current directory for all non-cd commands
        if not interpolated_command.strip().startswith('cd '):
            interpolated_command = f"cd {self.current_directory} && {interpolated_command}"
        
        print(f"  Executing: {block_name}")
        print(f"  Command: {interpolated_command}")
        print(f"  Working Directory: {self.current_directory}")
        
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
            
            # Extract the final working directory from output if command succeeded
            if success and '__BLOCKS_PWD__' in stdout_full:
                # Split output to get the PWD
                output_parts = stdout_full.split('__BLOCKS_PWD__')
                if len(output_parts) > 1:
                    # Get the last line after the marker (the pwd output)
                    pwd_output = output_parts[1].strip().split('\n')[-1]
                    if pwd_output and os.path.isdir(pwd_output):
                        old_dir = self.current_directory
                        self.current_directory = pwd_output
                        if old_dir != self.current_directory:
                            print(f"  Changed directory to: {self.current_directory}")
                # Remove the marker and pwd from stdout for display
                cleaned_stdout = output_parts[0]
            
            # For explicit cd commands, also update directory
            if success and command.strip().startswith('cd '):
                cd_parts = self.config_loader.interpolate(command).strip().split(None, 1)
                if len(cd_parts) > 1:
                    target_dir = cd_parts[1].strip()
                    if not os.path.isabs(target_dir):
                        target_dir = os.path.join(self.current_directory, target_dir)
                    target_dir = os.path.normpath(target_dir)
                    # Only update if not already set by PWD detection
                    if '__BLOCKS_PWD__' not in stdout_full:
                        self.current_directory = target_dir
                        print(f"  Changed directory to: {self.current_directory}")
            
            # Show stderr if command failed
            if stderr_full and not success:
                print(f"  Error: {stderr_full.strip()}")
            
            return success, cleaned_stdout, stderr_full
            
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out"
            print(f"  Error: {error_msg}")
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Command execution failed: {e}"
            print(f"  Error: {error_msg}")
            return False, "", error_msg
    
    def execute_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single block"""
        command = block.get('run', '')
        name = block.get('name', command[:50] + '...' if len(command) > 50 else command)
        description = block.get('description', '')
        
        print(f"\n{'='*60}")
        if name:
            print(f"Block: {name}")
        if description:
            print(f"Description: {description}")
        print(f"{'='*60}")
        
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
        
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  Status: {status} (Duration: {duration:.2f}s)")
        
        return result
    
    def execute_parallel_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple blocks in parallel using threads"""
        print(f"\n{'='*60}")
        print(f"PARALLEL EXECUTION - {len(blocks)} blocks")
        print(f"{'='*60}")
        
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
        
        print(f"\n{'='*60}")
        print(f"PARALLEL EXECUTION COMPLETED")
        print(f"{'='*60}")
        
        return results
    
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Execute the entire workflow"""
        blocks = workflow_data.get('blocks', [])
        
        if not blocks:
            print("No blocks found in workflow")
            return True
        
        print(f"\n{'#'*60}")
        print(f"# WORKFLOW EXECUTION STARTED")
        print(f"# Total items: {len(blocks)}")
        print(f"{'#'*60}")
        
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
                print(f"Warning: Unrecognized block structure (missing 'run' field): {item}")
        
        print(f"\n{'#'*60}")
        print(f"# WORKFLOW EXECUTION COMPLETED")
        print(f"{'#'*60}")
        
        # Print summary
        self._print_summary()
        
        return all_success
    
    def _print_summary(self):
        """Print execution summary"""
        if not self.results:
            return
        
        print(f"\n{'='*60}")
        print(f"EXECUTION SUMMARY")
        print(f"{'='*60}")
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        failed = total - successful
        total_duration = sum(r['duration'] for r in self.results)
        
        print(f"Total blocks executed: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total duration: {total_duration:.2f}s")
        
        if failed > 0:
            print(f"\nFailed blocks:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['name']}")
                    if result['stderr']:
                        print(f"    Error: {result['stderr'][:100]}")

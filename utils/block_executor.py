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
    
    def execute_command(self, command: str, block_name: str) -> Tuple[bool, str, str]:
        """
        Execute a shell command and return success status, stdout, stderr
        """
        # Interpolate variables in command
        interpolated_command = self.config_loader.interpolate(command)
        
        print(f"  Executing: {block_name}")
        print(f"  Command: {interpolated_command}")
        
        try:
            # Execute command using PowerShell on Windows
            if os.name == 'nt':
                # Use PowerShell for better command support
                result = subprocess.run(
                    ['powershell.exe', '-Command', interpolated_command],
                    capture_output=True,
                    text=True,
                    timeout=None
                )
            else:
                # Use bash on Unix-like systems
                result = subprocess.run(
                    interpolated_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=None,
                    executable='/bin/bash'
                )
            
            success = result.returncode == 0
            
            if result.stdout:
                print(f"  Output: {result.stdout.strip()}")
            if result.stderr and not success:
                print(f"  Error: {result.stderr.strip()}")
            
            return success, result.stdout, result.stderr
            
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

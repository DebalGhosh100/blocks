"""
Remote Executor - Handles SSH remote command execution

This module provides remote execution functionality including:
- SSH command execution via remotely.py
- Log file creation for remote output
- Streaming remote execution support
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple
from .colors import Colors


class RemoteExecutor:
    """
    Handles SSH remote command execution.
    
    Responsibilities:
    - Execute commands on remote hosts via SSH
    - Handle log file creation for remote output
    - Support both logged and streaming remote execution
    """
    
    def __init__(self, config_loader):
        """
        Initialize the remote executor.
        
        Args:
            config_loader: ConfigLoader instance for variable interpolation
        """
        self.config_loader = config_loader
    
    def execute_with_log_file(
        self,
        user: str,
        ip: str,
        password: str,
        command: str,
        log_file: str
    ) -> Tuple[bool, str, str]:
        """
        Execute remote command using remotely.py subprocess.
        
        This method launches remotely.py as a subprocess to handle
        the SSH connection and log file creation.
        
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
        
        # Get remotely.py path from framework directory
        framework_dir = os.environ.get('BLOCKS_FRAMEWORK_DIR', os.path.dirname(os.path.dirname(__file__)))
        remotely_script = str(Path(framework_dir) / 'remotely.py')
        
        # Build remotely.py command
        ssh_url = f"{user}@{ip}"
        remotely_cmd = [
            sys.executable,  # Use same Python interpreter
            remotely_script,
            ssh_url,
            command,
            log_file
        ]
        
        # Add password as optional flag if provided
        if password:
            remotely_cmd.extend(['-p', password])
        
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
    
    def execute_with_streaming(
        self,
        user: str,
        ip: str,
        password: str,
        command: str
    ) -> Tuple[bool, str, str]:
        """
        Execute remote command with real-time streaming (no log file).
        
        Uses SSHLogStreamer directly to execute the command and
        stream output to console in real-time.
        
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
            
            # Connect to remote host
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

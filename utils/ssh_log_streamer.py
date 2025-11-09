"""
SSH Log Streamer - Class for SSH connection and log streaming
"""

import os
import threading
import paramiko
from pathlib import Path
from datetime import datetime


class SSHLogStreamer:
    """Handles SSH connection and log streaming"""
    
    def __init__(self, ssh_url, password, command, log_file, workflow_dir=None):
        self.ssh_url = ssh_url
        self.password = password
        self.command = command
        self.workflow_dir = workflow_dir or Path.cwd()
        self.log_file = self._resolve_log_path(log_file)
        self.client = None
        
    def _resolve_log_path(self, log_file):
        """Resolve relative or absolute path for log file"""
        path = Path(log_file)
        
        # Convert to absolute path if relative
        if not path.is_absolute():
            # Resolve relative to workflow directory, not current working directory
            path = Path(self.workflow_dir) / path
            
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def _parse_ssh_url(self):
        """Parse SSH URL to extract user and host
        Supports formats: user@host, ssh://user@host, host
        """
        url = self.ssh_url
        
        # Remove ssh:// prefix if present
        if url.startswith('ssh://'):
            url = url[6:]
        
        # Parse user@host
        if '@' in url:
            user, host = url.split('@', 1)
        else:
            # Default to current user or 'root'
            user = os.getenv('USER', 'root')
            host = url
        
        # Remove port if specified (host:port)
        if ':' in host:
            host, port = host.split(':', 1)
            port = int(port)
        else:
            port = 22
            
        return user, host, port
    
    def connect(self):
        """Establish SSH connection"""
        user, host, port = self._parse_ssh_url()
        
        print(f"Connecting to {user}@{host}:{port}...")
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.client.connect(
                hostname=host,
                port=port,
                username=user,
                password=self.password,
                timeout=10
            )
            print(f"Successfully connected to {host}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _prepare_command_with_sudo(self):
        """Prepare command by injecting password for sudo commands"""
        command = self.command
        
        # Check if command contains sudo
        if 'sudo' in command:
            # Wrap sudo commands to use -S flag (read password from stdin)
            # This allows non-interactive sudo execution
            # Replace 'sudo' with 'echo password | sudo -S'
            command = command.replace('sudo ', f"echo '{self.password}' | sudo -S ")
        
        return command
    
    def stream_logs(self):
        """Execute command and stream output to log file in real-time"""
        if not self.client:
            print("Not connected to SSH server")
            return False
        
        try:
            # Prepare command with sudo password injection if needed
            prepared_command = self._prepare_command_with_sudo()
            
            # Write header to log file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== SSH Log Stream Started ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Host: {self.ssh_url}\n")
                f.write(f"Command: {self.command}\n")
                f.write(f"{'=' * 50}\n\n")
            
            print(f"Executing command: {self.command}")
            print(f"Streaming logs to: {self.log_file}")
            
            # Execute command and get stdout/stderr streams
            stdin, stdout, stderr = self.client.exec_command(
                prepared_command,
                get_pty=True  # Get pseudo-terminal for better output handling
            )
            
            # Get the channel for reading
            channel = stdout.channel
            
            # Thread for reading output (both stdout and stderr from pty)
            def read_output():
                with open(self.log_file, 'ab') as f:  # Binary mode for immediate writing
                    current_line = b''
                    
                    while True:
                        # Check if channel is ready to read
                        if channel.recv_ready():
                            # Read available data (up to 1024 bytes at a time)
                            data = channel.recv(1024)
                            if not data:
                                break
                            
                            # Process data character by character to handle \r properly
                            for byte in data:
                                char = bytes([byte])
                                
                                if char == b'\r':
                                    # Carriage return - write current line and reset
                                    # This handles progress bars that overwrite lines
                                    if current_line:
                                        f.write(current_line + b'\n')
                                        f.flush()
                                        current_line = b''
                                elif char == b'\n':
                                    # Newline - write current line
                                    f.write(current_line + b'\n')
                                    f.flush()
                                    current_line = b''
                                else:
                                    # Regular character - add to current line
                                    current_line += char
                        
                        # Check if there's data on stderr (when not using pty)
                        elif channel.recv_stderr_ready():
                            data = channel.recv_stderr(1024)
                            if data:
                                f.write(b'[STDERR] ' + data)
                                f.flush()
                        
                        # Check if channel is closed
                        elif channel.exit_status_ready():
                            # Read any remaining data
                            while channel.recv_ready():
                                data = channel.recv(1024)
                                if data:
                                    f.write(data)
                            # Write any remaining partial line
                            if current_line:
                                f.write(current_line + b'\n')
                            f.flush()
                            break
            
            # Start thread for streaming
            output_thread = threading.Thread(target=read_output, daemon=True)
            output_thread.start()
            
            # Wait for command to complete
            output_thread.join()
            
            # Get exit status
            exit_status = channel.recv_exit_status()
            
            # Write footer to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 50}\n")
                f.write(f"Command completed with exit status: {exit_status}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"=== SSH Log Stream Ended ===\n")
            
            print(f"\nCommand completed with exit status: {exit_status}")
            print(f"Logs saved to: {self.log_file}")
            
            return exit_status == 0
            
        except Exception as e:
            error_msg = f"\nError during command execution: {e}\n"
            print(error_msg)
            
            # Log the error
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(error_msg)
            
            return False
    
    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print("SSH connection closed")

"""
SSH Log Streamer - Class for SSH connection and log streaming
"""

import os
import threading
import paramiko
from pathlib import Path
from datetime import datetime
from .colors import Colors


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
        
        print(Colors.colorize(f"Connecting to {user}@{host}:{port}...", Colors.CYAN))
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # When no password is provided, try to manually authenticate with "none" method first
            # This is needed for servers that allow passwordless authentication
            if not self.password:
                try:
                    # Create transport and try "none" authentication
                    transport = paramiko.Transport((host, port))
                    transport.connect(username=user)
                    # Try "none" authentication
                    transport.auth_none(user)
                    # If we get here, "none" auth succeeded
                    self.client._transport = transport
                    print(Colors.colorize(f"Successfully connected to {host} (passwordless)", Colors.GREEN))
                    return True
                except paramiko.ssh_exception.BadAuthenticationType as e:
                    # "none" auth not allowed, fall back to normal connection
                    transport.close()
                except:
                    # Any other error, fall back to normal connection
                    try:
                        transport.close()
                    except:
                        pass
            
            # Standard connection with keys/password
            connect_params = {
                'hostname': host,
                'port': port,
                'username': user,
                'timeout': 10,
                'look_for_keys': not self.password,
                'allow_agent': not self.password,
                'gss_auth': False,
                'gss_kex': False
            }
            
            if self.password:
                connect_params['password'] = self.password
            
            self.client.connect(**connect_params)
            print(Colors.colorize(f"Successfully connected to {host}", Colors.GREEN))
            return True
        except paramiko.ssh_exception.AuthenticationException as e:
            if self.password:
                print(Colors.colorize(f"Connection failed: Authentication failed (incorrect password)", Colors.RED))
            else:
                print(Colors.colorize(f"Connection failed: No valid SSH keys found or not authorized on remote host", Colors.RED))
                print(Colors.colorize(f"  Attempted: Passwordless auth, SSH keys from ~/.ssh/, and SSH agent", Colors.YELLOW))
                print(Colors.colorize(f"  Hint: Ensure SSH keys are set up or the server allows passwordless access", Colors.YELLOW))
                print(Colors.colorize(f"  Or provide a password using the 'pass' field in your workflow", Colors.YELLOW))
            return False
        except Exception as e:
            print(Colors.colorize(f"Connection failed: {e}", Colors.RED))
            return False
    
    def _prepare_command_with_sudo(self):
        """Prepare command by injecting password for sudo commands"""
        command = self.command
        
        # Check if command contains sudo and password is provided
        if 'sudo' in command and self.password:
            # Wrap sudo commands to use -S flag (read password from stdin)
            # This allows non-interactive sudo execution
            # Replace 'sudo' with 'echo password | sudo -S'
            command = command.replace('sudo ', f"echo '{self.password}' | sudo -S ")
        
        return command
    
    def _read_and_stream_output(self, channel, log_file):
        """
        Read output from SSH channel and stream to log file in real-time.
        
        Handles carriage returns for progress bars and writes output incrementally.
        
        Args:
            channel: Paramiko channel object
            log_file: Path to log file for writing output
        """
        with open(log_file, 'ab') as f:  # Binary mode for immediate writing
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
    
    def stream_logs(self):
        """Execute command and stream output to log file in real-time"""
        if not self.client:
            print(Colors.colorize("Not connected to SSH server", Colors.RED))
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
            
            print(Colors.colorize(f"Executing command: {self.command}", Colors.CYAN))
            print(Colors.colorize(f"Streaming logs to: {self.log_file}", Colors.BLUE))
            
            # Execute command and get stdout/stderr streams
            stdin, stdout, stderr = self.client.exec_command(
                prepared_command,
                get_pty=True  # Get pseudo-terminal for better output handling
            )
            
            # Get the channel for reading
            channel = stdout.channel
            
            # Start thread for streaming output
            output_thread = threading.Thread(
                target=self._read_and_stream_output,
                args=(channel, self.log_file),
                daemon=True
            )
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
            
            status_color = Colors.GREEN if exit_status == 0 else Colors.RED
            print(Colors.colorize(f"\nCommand completed with exit status: {exit_status}", status_color))
            print(Colors.colorize(f"Logs saved to: {self.log_file}", Colors.BLUE))
            
            return exit_status == 0
            
        except Exception as e:
            error_msg = f"\nError during command execution: {e}\n"
            print(Colors.colorize(error_msg, Colors.RED))
            
            # Log the error
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(error_msg)
            
            return False
    
    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print(Colors.colorize("SSH connection closed", Colors.CYAN))

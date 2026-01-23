"""
Process Executor - Manages subprocess execution and output streaming

This module provides subprocess execution functionality including:
- Platform-specific subprocess creation (PowerShell/Bash)
- Real-time output streaming
- Output filtering for internal markers
- Stdout/stderr capture
"""

import os
import subprocess
from typing import Dict, Tuple


class ProcessExecutor:
    """
    Manages subprocess execution and output streaming.
    
    Responsibilities:
    - Start subprocesses with appropriate shell (PowerShell/Bash)
    - Stream output in real-time
    - Filter internal markers from output
    - Capture stdout/stderr for processing
    """
    
    def __init__(self, environment: Dict[str, str]):
        """
        Initialize the process executor.
        
        Args:
            environment: Environment variables to use for subprocess
        """
        self.environment = environment
    
    def start_subprocess(self, command: str) -> subprocess.Popen:
        """
        Start a subprocess with appropriate shell for the current platform.
        
        Windows: Uses PowerShell with PWD capture
        Unix: Uses Bash with PWD and environment capture
        
        The command is augmented with markers to capture state changes:
        - __BLOCKS_PWD__: Marks the start of PWD output
        - __BLOCKS_ENV__: Marks the start of environment export
        
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
    
    def should_filter_line(self, line: str) -> bool:
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
    
    def stream_process_output(self, process: subprocess.Popen) -> Tuple[str, str]:
        """
        Stream process output in real-time while capturing for later use.
        
        This function:
        1. Reads output as it's produced (real-time streaming)
        2. Filters internal markers from display
        3. Captures all output for later processing
        
        Platform-specific implementation:
        - Unix: Uses select() for efficient multiplexed I/O
        - Windows: Simple line-by-line reading (select() not available)
        
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
                            if not self.should_filter_line(line):
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
                        if not self.should_filter_line(line):
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
                    if not self.should_filter_line(line):
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

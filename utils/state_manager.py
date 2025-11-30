"""
State Manager - Manages persistent state across command executions

This module provides state management functionality including:
- Current working directory tracking
- Environment variable tracking
- PWD output parsing
- Environment export parsing
"""

import os
import re
from typing import Dict, Optional
from .colors import Colors


class StateManager:
    """
    Manages persistent state across command executions.
    
    Responsibilities:
    - Track current working directory
    - Track environment variables
    - Parse and apply state changes from command output
    - Handle PWD and environment export parsing
    """
    
    def __init__(self, initial_directory: str = None, initial_environment: Dict[str, str] = None):
        """
        Initialize the state manager.
        
        Args:
            initial_directory: Starting working directory (default: current directory)
            initial_environment: Starting environment variables (default: copy of os.environ)
        """
        self.current_directory = initial_directory or os.getcwd()
        self.environment = initial_environment or os.environ.copy()
    
    def update_directory(self, new_directory: str, display_change: bool = True):
        """
        Update the current working directory.
        
        Args:
            new_directory: New directory path
            display_change: Whether to print directory change message
        """
        old_dir = self.current_directory
        self.current_directory = new_directory
        
        if display_change and old_dir != new_directory:
            print(Colors.colorize(
                f"  Changed directory to: {self.current_directory}",
                Colors.GREEN
            ))
    
    def update_environment_variable(self, var_name: str, var_value: str):
        """
        Update a single environment variable.
        
        Args:
            var_name: Variable name
            var_value: Variable value
        """
        self.environment[var_name] = var_value
    
    def parse_and_apply_pwd(
        self,
        pwd_section: str,
        original_command: str,
        precalculated_dir: Optional[str]
    ):
        """
        Parse PWD output and update current directory.
        
        Tries to extract the actual PWD from command output.
        Falls back to pre-calculated directory if PWD detection fails.
        
        Args:
            pwd_section: Section of output containing PWD
            original_command: Original command (before preparation)
            precalculated_dir: Pre-calculated directory (fallback)
        """
        # Try to extract actual PWD from output
        pwd_detected = False
        for line in pwd_section.split('\n'):
            line = line.strip()
            # Verify it's a valid directory path
            if line and os.path.isdir(line):
                self.update_directory(line)
                pwd_detected = True
                break
        
        # Fallback to pre-calculated directory if PWD detection failed
        if not pwd_detected and original_command.strip().startswith('cd ') and precalculated_dir:
            self.update_directory(precalculated_dir)
    
    def parse_and_apply_pwd_simple(
        self,
        pwd_output: str,
        original_command: str,
        precalculated_dir: Optional[str]
    ):
        """
        Parse simple PWD output and update directory (Windows or fallback).
        
        Args:
            pwd_output: PWD output string
            original_command: Original command
            precalculated_dir: Pre-calculated directory (fallback)
        """
        # Try to use actual PWD output
        if pwd_output and os.path.isdir(pwd_output):
            self.update_directory(pwd_output)
        # Fallback to pre-calculated directory
        elif original_command.strip().startswith('cd ') and precalculated_dir:
            self.update_directory(precalculated_dir)
    
    def parse_and_apply_environment(self, export_output: str):
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
                self.update_environment_variable(var_name, var_value)
    
    def process_state_changes(
        self,
        stdout: str,
        original_command: str,
        success: bool,
        precalculated_dir: Optional[str]
    ) -> str:
        """
        Process state changes from command execution output.
        
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
        # If no PWD marker, return stdout as-is (no state changes captured)
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
            # Both PWD and environment captured
            env_parts = remainder.split('__BLOCKS_ENV__')
            pwd_section = env_parts[0].strip()
            
            # Update directory if command succeeded
            if success:
                self.parse_and_apply_pwd(pwd_section, original_command, precalculated_dir)
            
            # Update environment variables if captured and command succeeded
            if success and len(env_parts) > 1:
                env_output = env_parts[1]
                self.parse_and_apply_environment(env_output)
        else:
            # Only PWD capture (no environment)
            pwd_output = remainder.strip().split('\n')[-1]
            if success:
                self.parse_and_apply_pwd_simple(pwd_output, original_command, precalculated_dir)
        
        return cleaned_stdout

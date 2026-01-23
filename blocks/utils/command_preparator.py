"""
Command Preparator - Handles command preparation and interpolation

This module provides command preparation functionality including:
- Configuration variable interpolation
- Framework script path resolution
- Working directory prepending
- Target directory pre-calculation for cd commands
"""

import os
import re
from typing import Optional


class CommandPreparator:
    """
    Handles command preparation, interpolation, and path resolution.
    
    Responsibilities:
    - Interpolate configuration variables (${var.path} -> value)
    - Resolve remotely.py script paths
    - Pre-calculate target directories for cd commands
    - Handle compound commands with shell operators
    """
    
    def __init__(self, config_loader):
        """
        Initialize the command preparator.
        
        Args:
            config_loader: ConfigLoader instance for variable interpolation
        """
        self.config_loader = config_loader
    
    def interpolate_command(self, command: str) -> str:
        """
        Interpolate configuration variables in command.
        
        Replaces ${var.path} patterns with actual values from config.
        
        Args:
            command: Raw command string from YAML
            
        Returns:
            Command with all variables interpolated
        """
        return self.config_loader.interpolate(command)
    
    def resolve_remotely_path(self, command: str) -> str:
        """
        Replace 'remotely.py' with absolute path to framework script.
        
        This allows workflows to reference remotely.py without needing
        to know its absolute location.
        
        Args:
            command: Command string that may contain 'remotely.py'
            
        Returns:
            Command with remotely.py resolved to absolute path
        """
        framework_dir = os.environ.get('BLOCKS_FRAMEWORK_DIR')
        if framework_dir:
            remotely_path = os.path.join(framework_dir, 'remotely.py')
            return command.replace('remotely.py', remotely_path)
        return command
    
    def prepend_working_directory(self, command: str, current_dir: str) -> str:
        """
        Prepend 'cd' to current directory to maintain state.
        
        This ensures each command starts from the correct working directory,
        maintaining directory state across multiple command executions.
        
        Args:
            command: Command to execute
            current_dir: Current working directory path
            
        Returns:
            Command with working directory change prepended
        """
        return f"cd {current_dir} && {command}"
    
    def prepare_command(self, command: str, current_dir: str) -> str:
        """
        Fully prepare a command for execution.
        
        Applies all preparation steps:
        1. Interpolate configuration variables
        2. Resolve framework script paths
        3. Prepend working directory
        
        Args:
            command: Raw command from YAML
            current_dir: Current working directory
            
        Returns:
            Fully prepared command ready for execution
        """
        # Step 1: Interpolate variables
        prepared = self.interpolate_command(command)
        
        # Step 2: Resolve framework paths
        prepared = self.resolve_remotely_path(prepared)
        
        # Step 3: Prepend working directory
        prepared = self.prepend_working_directory(prepared, current_dir)
        
        return prepared
    
    def precalculate_target_directory(self, command: str, current_dir: str) -> Optional[str]:
        """
        Pre-calculate the target directory for 'cd' commands.
        
        Extracts the directory path from cd commands, handling:
        - Simple cd: "cd /path"
        - Compound cd: "cd /path && command"
        - Shell operators: &&, ||, ;, |
        - Relative paths: .., ., ./subdir
        
        Args:
            command: The interpolated command string
            current_dir: Current working directory for relative path resolution
            
        Returns:
            Absolute normalized path to target directory, or None if not a cd command
        """
        # Only process cd commands
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
            target_dir = os.path.join(current_dir, target_dir)
        
        # Normalize to resolve .. and . in paths
        return os.path.normpath(target_dir)

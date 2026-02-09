"""
Configuration Loader - Loads and manages configuration from parameters directory
"""

import yaml
import re
from pathlib import Path
from typing import Any, Set
from .colors import Colors


class ConfigLoader:
    """Loads and manages configuration from parameters directory"""
    
    def __init__(self, parameters_dir: str = "parameters"):
        self.parameters_dir = Path(parameters_dir)
        self.config = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all YAML files from parameters directory"""
        if not self.parameters_dir.exists():
            print(Colors.colorize(f"Warning: Parameters directory '{self.parameters_dir}' not found", Colors.YELLOW))
            return
        
        for yaml_file in self.parameters_dir.glob("*.yaml"):
            config_name = yaml_file.stem
            with open(yaml_file, 'r', encoding='utf-8') as f:
                self.config[config_name] = yaml.safe_load(f)
        
        for yml_file in self.parameters_dir.glob("*.yml"):
            config_name = yml_file.stem
            with open(yml_file, 'r', encoding='utf-8') as f:
                self.config[config_name] = yaml.safe_load(f)
        
        # Recursively interpolate variables within the loaded configs
        self._interpolate_configs()
    
    def _interpolate_configs(self):
        """
        Recursively interpolate all variables within loaded config dictionaries.
        
        This allows parameters YAML files to reference other values within parameters files
        using ${config.path.to.value} syntax. For example:
        
        In parameters/config.yaml:
        STAR-trigger:
          linux-python-3-10: python3 /path/to/script.py
        
        linux-machines:
          - trigger: ${config.STAR-trigger.linux-python-3-10}
        
        Handles:
        - Nested dictionaries and lists
        - Multiple passes to resolve dependencies
        - Circular reference detection
        """
        max_iterations = 10  # Prevent infinite loops
        
        for iteration in range(max_iterations):
            has_changes = False
            self.config = self._recursive_interpolate(self.config, set())
            
            # Check if any interpolation occurred in this iteration
            temp_config = self._recursive_interpolate(self.config, set())
            if temp_config == self.config:
                break  # No more changes, we're done
            
            has_changes = True
        
        if has_changes:
            # Final pass to ensure all variables are resolved
            self.config = self._recursive_interpolate(self.config, set())
    
    def _recursive_interpolate(self, obj: Any, visited_paths: Set[str], current_path: str = "") -> Any:
        """
        Recursively interpolate variables in nested data structures.
        
        Args:
            obj: Object to interpolate (dict, list, str, or other)
            visited_paths: Set of variable paths being interpolated (for circular detection)
            current_path: Current path in the config tree (for circular detection)
            
        Returns:
            Object with all variables interpolated
        """
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                result[key] = self._recursive_interpolate(value, visited_paths.copy(), new_path)
            return result
        
        elif isinstance(obj, list):
            return [self._recursive_interpolate(item, visited_paths.copy(), f"{current_path}[{i}]") 
                    for i, item in enumerate(obj)]
        
        elif isinstance(obj, str):
            # Check if string contains variables to interpolate
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, obj)
            
            if not matches:
                return obj  # No variables to interpolate
            
            # Interpolate each variable found
            result = obj
            for var_path in matches:
                # Detect circular references
                if var_path in visited_paths:
                    print(Colors.colorize(
                        f"Warning: Circular reference detected for '{var_path}' at path '{current_path}'",
                        Colors.YELLOW
                    ))
                    continue
                
                try:
                    # Add to visited paths before resolving
                    new_visited = visited_paths.copy()
                    new_visited.add(var_path)
                    
                    # Get the value
                    value = self.get_value(var_path)
                    
                    # If the value is still a string with variables, recursively interpolate it
                    if isinstance(value, str):
                        value = self._recursive_interpolate(value, new_visited, var_path)
                    
                    # Replace the variable in the result string
                    result = result.replace(f"${{{var_path}}}", str(value))
                    
                except KeyError:
                    # Variable not found, leave it as-is
                    pass
            
            return result
        
        else:
            # For other types (int, bool, None, etc.), return as-is
            return obj
    
    def reload_configs(self):
        """Reload all YAML files from parameters directory.
        
        This method is called after each run block execution to pick up
        any changes made to parameters YAML files during workflow execution.
        This allows workflows to dynamically update configurations mid-execution.
        """
        self.config = {}  # Clear existing config
        self._load_all_configs()  # Reload all files (includes interpolation)
    
    def get_value(self, path: str) -> Any:
        """
        Get value from config using dot notation
        Example: machines.arlh.ip -> config['machines']['arlh']['ip']
        """
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                raise KeyError(f"Configuration path '{path}' not found")
        
        return value
    
    def interpolate(self, text: str) -> str:
        """
        Replace ${variable.path} with actual values from config
        Example: ${machines.arlh.ip} -> 172.22.32.116
        """
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_path = match.group(1)
            try:
                value = self.get_value(var_path)
                return str(value)
            except KeyError as e:
                print(Colors.colorize(f"Warning: {e}", Colors.YELLOW))
                return match.group(0)  # Return original if not found
        
        return re.sub(pattern, replace_var, text)

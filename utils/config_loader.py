"""
Configuration Loader - Loads and manages configuration from storage directory
"""

import yaml
import re
from pathlib import Path
from typing import Any


class ConfigLoader:
    """Loads and manages configuration from storage directory"""
    
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.config = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all YAML files from storage directory"""
        if not self.storage_dir.exists():
            print(f"Warning: Storage directory '{self.storage_dir}' not found")
            return
        
        for yaml_file in self.storage_dir.glob("*.yaml"):
            config_name = yaml_file.stem
            with open(yaml_file, 'r', encoding='utf-8') as f:
                self.config[config_name] = yaml.safe_load(f)
        
        for yml_file in self.storage_dir.glob("*.yml"):
            config_name = yml_file.stem
            with open(yml_file, 'r', encoding='utf-8') as f:
                self.config[config_name] = yaml.safe_load(f)
    
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
                print(f"Warning: {e}")
                return match.group(0)  # Return original if not found
        
        return re.sub(pattern, replace_var, text)

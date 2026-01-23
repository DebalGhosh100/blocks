"""
Loop Expander - Expands for-loops into individual executable blocks

This module provides loop expansion functionality including:
- For-loop parsing and expansion
- Variable substitution in templates
- Nested loop handling
- Support for lists of strings and dictionaries
"""

import re
from typing import Dict, Any, List, Optional
from .colors import Colors


class LoopExpander:
    """
    Expands for-loops into individual executable blocks.
    
    Responsibilities:
    - Parse for-loop configurations
    - Iterate over lists (strings, dicts, nested lists)
    - Substitute loop variables in block templates
    - Handle nested for-loops
    - Support parallel loop execution
    """
    
    def __init__(self, config_loader):
        """
        Initialize the loop expander.
        
        Args:
            config_loader: ConfigLoader instance for variable interpolation
        """
        self.config_loader = config_loader
    
    def expand_for_loop(self, loop_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Expand a for-loop into individual blocks by iterating over a list.
        
        Supports syntax:
        for:
          individual: item_name
          in: ${config.list_path}
          run: command with ${item_name}
          
        Also supports:
        - Loops over dictionaries: ${item_name.field}
        - Nested loops
        - Multiple blocks per iteration
        
        Args:
            loop_config: Dictionary containing for-loop configuration
            
        Returns:
            List of expanded block dictionaries
        """
        # Reload configs before expanding loop to ensure fresh list data
        # This allows workflows to modify the list before the loop executes
        self.config_loader.reload_configs()
        
        individual_var = loop_config.get('individual')
        list_path = loop_config.get('in', '')
        
        # Validate required fields
        if not individual_var or not list_path:
            print(Colors.colorize("Error: for-loop missing 'individual' or 'in' field", Colors.BOLD_RED))
            return []
        
        # Get the list from config using dot notation
        list_items = self._get_list_items(list_path)
        
        if list_items is None:
            return []
        
        # Expand based on loop structure
        if 'blocks' in loop_config:
            # Multiple sub-blocks per iteration
            return self._expand_multi_block_loop(loop_config, list_items, individual_var)
        elif 'for' in loop_config:
            # Nested for-loop
            return self._expand_nested_loop(loop_config, list_items, individual_var)
        else:
            # Simple single-command loop
            return self._expand_simple_loop(loop_config, list_items, individual_var)
    
    def _get_list_items(self, list_path: str) -> Optional[List[Any]]:
        """
        Get list items from configuration path.
        
        Args:
            list_path: Configuration path like ${config.list_path}
            
        Returns:
            List of items, or None if path doesn't reference a list
        """
        try:
            # Remove ${} wrapper if present
            clean_path = list_path.replace('${', '').replace('}', '')
            list_items = self.config_loader.get_value(clean_path)
            
            if not isinstance(list_items, list):
                print(Colors.colorize(f"Error: '{list_path}' does not reference a list", Colors.BOLD_RED))
                return None
            
            return list_items
        except Exception as e:
            print(Colors.colorize(f"Error getting list items: {e}", Colors.BOLD_RED))
            return None
    
    def _substitute_string_value(self, value: str, individual_var: str, item: Any) -> str:
        """
        Substitute loop variable in a string value.
        
        Handles both simple items and dictionary items:
        - Simple: ${individual_var} -> item
        - Dict: ${individual_var.field} -> item['field']
        
        Args:
            value: String containing substitution patterns
            individual_var: Loop variable name
            item: Current loop item (string or dict)
            
        Returns:
            String with substitutions applied
        """
        if isinstance(item, dict):
            # Item is a dict - replace ${individual_var.field} patterns
            substituted = value
            for field_name, field_value in item.items():
                pattern = f"${{{individual_var}.{field_name}}}"
                substituted = substituted.replace(pattern, str(field_value))
            return substituted
        else:
            # Item is a simple value - replace ${individual_var}
            return value.replace(f"${{{individual_var}}}", str(item))
    
    def _substitute_in_dict(self, data: Dict[str, Any], var_name: str, var_value: Any) -> Dict[str, Any]:
        """
        Recursively substitute variable references in a dictionary.
        
        Args:
            data: Dictionary to process
            var_name: Variable name to substitute
            var_value: Value to substitute (can be dict or simple value)
            
        Returns:
            Dictionary with substitutions applied
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._substitute_string_value(value, var_name, var_value)
            elif isinstance(value, dict):
                result[key] = self._substitute_in_dict(value, var_name, var_value)
            elif isinstance(value, list):
                result[key] = [
                    self._substitute_in_dict(item, var_name, var_value) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def _expand_simple_loop(
        self,
        loop_config: Dict[str, Any],
        list_items: List[Any],
        individual_var: str
    ) -> List[Dict[str, Any]]:
        """
        Expand a simple for-loop (single command per iteration).
        
        Args:
            loop_config: Loop configuration
            list_items: List of items to iterate over
            individual_var: Loop variable name
            
        Returns:
            List of expanded blocks
        """
        expanded_blocks = []
        
        for item in list_items:
            block = {}
            
            # Process each key in the loop config (except control keys)
            for key, value in loop_config.items():
                if key in ['individual', 'in']:
                    continue  # Skip loop control keys
                
                # Substitute the individual variable in the value
                if isinstance(value, str):
                    block[key] = self._substitute_string_value(value, individual_var, item)
                elif isinstance(value, dict):
                    # Handle nested dictionaries (like run-remotely config)
                    block[key] = self._substitute_in_dict(value, individual_var, item)
                else:
                    block[key] = value
            
            expanded_blocks.append(block)
        
        return expanded_blocks
    
    def _expand_multi_block_loop(
        self,
        loop_config: Dict[str, Any],
        list_items: List[Any],
        individual_var: str
    ) -> List[Dict[str, Any]]:
        """
        Expand a for-loop with multiple blocks per iteration.
        
        Example:
        for:
          individual: server
          in: ${servers}
          blocks:
            - run: echo ${server.name}
            - run: ping ${server.ip}
        
        Args:
            loop_config: Loop configuration
            list_items: List of items to iterate over
            individual_var: Loop variable name
            
        Returns:
            List of expanded blocks
        """
        expanded_blocks = []
        blocks_array = loop_config['blocks']
        
        for item in list_items:
            # Process each block template in the blocks array
            for block_template in blocks_array:
                substituted_block = {}
                
                for key, value in block_template.items():
                    if isinstance(value, str):
                        substituted_block[key] = self._substitute_string_value(value, individual_var, item)
                    elif isinstance(value, dict):
                        # Handle nested structures like for loops or run-remotely
                        if key == 'for':
                            # Nested for-loop - substitute the 'in' path
                            nested_for = dict(value)
                            nested_in_path = nested_for.get('in', '')
                            nested_in_path = self._substitute_string_value(nested_in_path, individual_var, item)
                            nested_for['in'] = nested_in_path
                            substituted_block[key] = nested_for
                        else:
                            substituted_block[key] = self._substitute_in_dict(value, individual_var, item)
                    else:
                        substituted_block[key] = value
                
                expanded_blocks.append(substituted_block)
        
        return expanded_blocks
    
    def _expand_nested_loop(
        self,
        loop_config: Dict[str, Any],
        list_items: List[Any],
        individual_var: str
    ) -> List[Dict[str, Any]]:
        """
        Expand a nested for-loop (for inside for).
        
        Example:
        for:
          individual: project
          in: ${projects}
          run: mkdir ${project.name}
          for:
            individual: subdir
            in: ${project.subdirs}
            run: mkdir ${project.name}/${subdir}
        
        Args:
            loop_config: Loop configuration
            list_items: List of items to iterate over (outer loop)
            individual_var: Loop variable name (outer loop)
            
        Returns:
            List of expanded blocks
        """
        expanded_blocks = []
        nested_loop_config = loop_config['for']
        
        for item in list_items:
            # If outer loop has a 'run' command, add it first
            if 'run' in loop_config:
                outer_run_block = {
                    'run': self._substitute_string_value(loop_config['run'], individual_var, item)
                }
                expanded_blocks.append(outer_run_block)
            
            # Get and expand the nested loop
            nested_blocks = self._expand_nested_loop_items(
                nested_loop_config,
                individual_var,
                item
            )
            
            # Substitute outer variable in nested blocks
            for nested_block in nested_blocks:
                final_block = {}
                for key, value in nested_block.items():
                    if isinstance(value, str):
                        final_block[key] = self._substitute_string_value(value, individual_var, item)
                    elif isinstance(value, dict):
                        final_block[key] = self._substitute_in_dict(value, individual_var, item)
                    else:
                        final_block[key] = value
                
                expanded_blocks.append(final_block)
        
        return expanded_blocks
    
    def _expand_nested_loop_items(
        self,
        nested_loop_config: Dict[str, Any],
        outer_var: str,
        outer_item: Any
    ) -> List[Dict[str, Any]]:
        """
        Expand the inner loop of a nested for-loop.
        
        Args:
            nested_loop_config: Nested loop configuration
            outer_var: Outer loop variable name
            outer_item: Current outer loop item
            
        Returns:
            List of expanded blocks from inner loop
        """
        nested_in_path = nested_loop_config.get('in', '')
        nested_individual = nested_loop_config.get('individual')
        
        # Check if nested_in_path references a field in the current item
        nested_list = self._get_nested_list_from_item(nested_in_path, outer_var, outer_item)
        
        if nested_list is not None:
            # Direct list from outer item - expand directly
            return self._expand_nested_direct_list(nested_loop_config, nested_list, nested_individual)
        else:
            # Path-based nested loop - substitute and resolve
            substituted_path = self._substitute_string_value(nested_in_path, outer_var, outer_item)
            nested_loop_config_copy = dict(nested_loop_config)
            nested_loop_config_copy['in'] = substituted_path
            
            # Recursively expand nested loop
            return self.expand_for_loop(nested_loop_config_copy)
    
    def _get_nested_list_from_item(
        self,
        nested_in_path: str,
        outer_var: str,
        outer_item: Any
    ) -> Optional[List[Any]]:
        """
        Try to extract nested list directly from outer loop item.
        
        Args:
            nested_in_path: Path like ${outer_var.field}
            outer_var: Outer loop variable name
            outer_item: Current outer loop item (must be dict)
            
        Returns:
            List if found, None otherwise
        """
        if not isinstance(outer_item, dict):
            return None
        
        # Try to extract field name from ${outer_var.field} pattern
        pattern = f"\\${{{outer_var}\\.([^}}]+)\\}}"
        match = re.search(pattern, nested_in_path)
        
        if match:
            field_name = match.group(1)
            if field_name in outer_item:
                nested_list = outer_item[field_name]
                if isinstance(nested_list, list):
                    return nested_list
        
        return None
    
    def _expand_nested_direct_list(
        self,
        nested_loop_config: Dict[str, Any],
        nested_list: List[Any],
        nested_individual: str
    ) -> List[Dict[str, Any]]:
        """
        Expand nested loop with a direct list.
        
        Args:
            nested_loop_config: Nested loop configuration
            nested_list: List to iterate over
            nested_individual: Nested loop variable name
            
        Returns:
            List of expanded blocks
        """
        nested_blocks = []
        
        for nested_item in nested_list:
            nested_block = {}
            
            for key, value in nested_loop_config.items():
                if key in ['individual', 'in', 'for']:
                    continue
                
                if isinstance(value, str):
                    nested_block[key] = self._substitute_string_value(value, nested_individual, nested_item)
                elif isinstance(value, dict):
                    nested_block[key] = self._substitute_in_dict(value, nested_individual, nested_item)
                else:
                    nested_block[key] = value
            
            nested_blocks.append(nested_block)
        
        return nested_blocks

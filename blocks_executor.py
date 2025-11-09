#!/usr/bin/env python3
"""
Blocks Executor - Execute YAML-defined workflows with sequential and parallel blocks
"""

import sys
import os
import yaml
from pathlib import Path

# Import from utils package
from utils import ConfigLoader, BlockExecutor


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Execute YAML-defined workflows with sequential and parallel blocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blocks_executor.py main.yaml
  python blocks_executor.py workflow.yaml --storage config
        """
    )
    
    parser.add_argument(
        'workflow_file',
        help='Path to workflow YAML file'
    )
    parser.add_argument(
        '--storage',
        default='storage',
        help='Directory containing configuration YAML files (default: storage)'
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Check if workflow file exists
    workflow_path = Path(args.workflow_file)
    if not workflow_path.exists():
        print(f"Error: Workflow file '{args.workflow_file}' not found")
        sys.exit(1)
    
    # Store the directory where the workflow file resides
    # This is used by remotely.py to resolve relative log paths correctly
    workflow_dir = workflow_path.parent.resolve()
    os.environ['BLOCKS_WORKFLOW_DIR'] = str(workflow_dir)
    
    # Change to the workflow directory so all relative paths work correctly
    original_cwd = Path.cwd()
    os.chdir(workflow_dir)
    
    try:
        # Load workflow YAML
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_data = yaml.safe_load(f)
        
        # Initialize config loader
        config_loader = ConfigLoader(args.storage)
        
        # Initialize executor
        executor = BlockExecutor(config_loader)
        
        # Execute workflow
        success = executor.execute_workflow(workflow_data)
        
        # Exit with appropriate status
        sys.exit(0 if success else 1)
        
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        os.chdir(original_cwd)  # Restore original directory
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        os.chdir(original_cwd)  # Restore original directory
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        os.chdir(original_cwd)  # Restore original directory
        sys.exit(1)


if __name__ == '__main__':
    main()

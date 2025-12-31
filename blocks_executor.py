#!/usr/bin/env python3
"""
Blocks Executor - Execute YAML-defined workflows with sequential and parallel blocks
"""

import sys
import os
import yaml
from pathlib import Path

# Import from utils package
from utils import ConfigLoader, BlockExecutor, Colors


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
        print(Colors.colorize(f"Error: Workflow file '{args.workflow_file}' not found", Colors.BOLD_RED))
        sys.exit(1)
    
    # Store the directory where the workflow file resides
    # This is used by remotely.py to resolve relative log paths correctly
    workflow_dir = workflow_path.parent.resolve()
    os.environ['BLOCKS_WORKFLOW_DIR'] = str(workflow_dir)
    
    # Store the framework directory (where blocks_executor.py is located)
    # This allows workflows to reference remotely.py and other framework scripts
    framework_dir = Path(__file__).parent.resolve()
    os.environ['BLOCKS_FRAMEWORK_DIR'] = str(framework_dir)
    
    # Add framework directory to PATH so scripts like remotely.py can be found
    current_path = os.environ.get('PATH', '')
    os.environ['PATH'] = f"{framework_dir}{os.pathsep}{current_path}"
    
    # Resolve paths to absolute before changing directory
    # Storage path should be resolved from current directory, not workflow directory
    workflow_path_absolute = workflow_path.resolve()
    storage_path_absolute = Path(args.storage).resolve()
    
    # Change to the workflow directory so all relative paths work correctly
    original_cwd = Path.cwd()
    os.chdir(workflow_dir)
    
    try:
        # Load workflow YAML (use absolute path since we changed directory)
        with open(workflow_path_absolute, 'r', encoding='utf-8') as f:
            workflow_data = yaml.safe_load(f)
        
        # Initialize config loader with absolute storage path
        config_loader = ConfigLoader(str(storage_path_absolute))
        
        # Initialize executor
        executor = BlockExecutor(config_loader)
        
        # Execute workflow
        success = executor.execute_workflow(workflow_data)
        
        # Exit with appropriate status
        sys.exit(0 if success else 1)
        
    except yaml.YAMLError as e:
        error_msg = str(e)
        print(Colors.colorize(f"Error parsing YAML file: {error_msg}", Colors.BOLD_RED))
        
        # Provide helpful hint for common YAML quoting issues
        if "mapping values are not allowed here" in error_msg:
            print(Colors.colorize("\n💡 Tip: This error often occurs when colons (:) appear in unquoted strings.", Colors.YELLOW))
            print(Colors.colorize("    Try wrapping your command in quotes:", Colors.YELLOW))
            print(Colors.colorize('    ✓ Correct:   run: "echo \\"text: value\\" >> file.txt"', Colors.GREEN))
            print(Colors.colorize('    ✓ Correct:   run: \'echo "text: value" >> file.txt\'', Colors.GREEN))
            print(Colors.colorize('    ✗ Incorrect: run: echo "text: value" >> file.txt', Colors.RED))
        
        os.chdir(original_cwd)  # Restore original directory
        sys.exit(1)
    except KeyboardInterrupt:
        print(Colors.colorize("\n\nWorkflow interrupted by user", Colors.YELLOW))
        os.chdir(original_cwd)  # Restore original directory
        sys.exit(130)
    except Exception as e:
        print(Colors.colorize(f"Unexpected error: {e}", Colors.BOLD_RED))
        import traceback
        traceback.print_exc()
        os.chdir(original_cwd)  # Restore original directory
        sys.exit(1)


if __name__ == '__main__':
    main()

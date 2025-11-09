# Example 1: Basic Sequential Execution

## Overview
This example demonstrates the simplest use case of Blocks - executing commands sequentially (one after another) in a defined order.

## What This Example Demonstrates
- ✅ Basic sequential block execution
- ✅ Simple shell commands
- ✅ Multi-command execution within a single block
- ✅ File creation and cleanup

## Prerequisites
- Python 3.x installed
- Blocks framework installed

## Directory Structure
```
01-basic-sequential/
├── main.yaml           # Workflow definition
├── storage/            # Configuration directory
│   └── config.yaml     # Placeholder config (not used in this example)
└── README.md           # This file
```

## How to Run

### Option 1: Clone Just This Example
```bash
# Clone the entire repository
git clone https://github.com/DebalGhosh100/blocks.git

# Navigate to this example
cd blocks/examples/01-basic-sequential

# Copy the framework files (if not already in parent directory)
# You need: blocks_executor.py, remotely.py, utils/, requirements.txt

# Run the workflow
python3 ../../blocks_executor.py main.yaml
```

### Option 2: Run with One-Command Execution
```bash
# From the example directory with main.yaml and storage/ present
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

## Expected Output
The workflow will:
1. Print system information (date, hostname)
2. List files in the current directory
3. Display environment variables
4. Create a test file with content "Hello from Blocks!"
5. Display the test file content
6. Clean up by removing the test file

## Workflow Breakdown

### Block 1: Print System Information
```yaml
- name: "Print System Information"
  description: "Display current date and hostname"
  run: "echo 'Current Date:' && date && echo 'Hostname:' && hostname"
```
Executes multiple commands using `&&` to chain them sequentially.

### Block 2: List Current Directory
```yaml
- name: "List Current Directory"
  description: "Show files in current directory"
  run: "ls -la"
```
Simple single command execution.

### Block 3: Display Environment Variables
```yaml
- name: "Display Environment Variables"
  description: "Show important environment variables"
  run: "echo 'User:' $USER && echo 'Home:' $HOME && echo 'Path:' $PATH"
```
Access environment variables using `$VARIABLE_NAME` syntax.

### Block 4: Create Test File
```yaml
- name: "Create Test File"
  description: "Create a simple test file"
  run: "echo 'Hello from Blocks!' > test_output.txt && cat test_output.txt"
```
Creates a file and displays its content.

### Block 5: Cleanup
```yaml
- name: "Cleanup"
  description: "Remove test file"
  run: "rm -f test_output.txt && echo 'Cleanup complete!'"
```
Removes the test file created earlier.

## Key Takeaways
- All blocks execute in the order they are defined
- Each block waits for the previous one to complete
- Commands can be chained using `&&` for sequential execution within a block
- The `name` and `description` fields are optional but improve readability

## Next Steps
- Try modifying the commands to suit your needs
- Add more blocks to the workflow
- Explore the next example: **02-parallel-execution**

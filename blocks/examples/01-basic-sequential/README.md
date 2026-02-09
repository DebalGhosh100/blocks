# Example 1: Basic Sequential Execution

## Overview
This example demonstrates the simplest use case of Blocks - executing commands sequentially (one after another) in a defined order.

## What This Example Demonstrates
- ✅ Basic sequential block execution
- ✅ Path persistence using persist-paths blocks
- ✅ Simple shell commands
- ✅ Multi-command execution within a single block
- ✅ File creation and cleanup
- ✅ Variable interpolation with persisted paths

## Prerequisites
- Python 3.x installed
- Blocks framework installed

## Directory Structure
```
01-basic-sequential/
├── main.yaml           # Workflow definition
├── parameters/            # Configuration directory
│   └── config.yaml     # Placeholder config (not used in this example)
└── README.md           # This file
```

## How to Run

```bash
# Clone this specific example and navigate to it
git clone --depth 1 --filter=blob:none --sparse https://github.com/DebalGhosh100/blocks.git && cd blocks && git sparse-checkout set examples/01-basic-sequential && cd examples/01-basic-sequential

# Run with one-command execution
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

**What this does:**
1. Clones only this example directory (sparse checkout)
2. Downloads the Blocks framework automatically
3. Installs dependencies (paramiko, pyyaml)
4. Executes the workflow
5. Cleans up framework files after completion

## Expected Output
The workflow will:
1. Persist project paths to parameters/paths.yaml
2. Print system information (date, hostname)
3. List files in the current directory
4. Display environment variables and the persisted project directory path
5. Create a test file with content "Hello from Blocks!"
6. Display the test file content
7. Clean up by removing the test file

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

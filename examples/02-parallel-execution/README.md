# Example 2: Parallel Execution

## Overview
This example demonstrates how to execute multiple tasks simultaneously using the `parallel:` keyword. All tasks in a parallel block run concurrently, and the workflow waits for all of them to complete before proceeding.

## What This Example Demonstrates
- ✅ Parallel block execution with multiple concurrent tasks
- ✅ Sequential blocks before and after parallel execution
- ✅ Multi-line commands with loops
- ✅ File creation from parallel tasks
- ✅ Verification of parallel task completion

## Prerequisites
- Python 3.x installed
- Blocks framework installed

## Directory Structure
```
02-parallel-execution/
├── main.yaml           # Workflow with parallel blocks
├── storage/            # Configuration directory
│   └── config.yaml     # Placeholder config
└── README.md           # This file
```

## How to Run

### Option 1: From the Example Directory
```bash
# Navigate to this example
cd blocks/examples/02-parallel-execution

# Run the workflow
python3 ../../blocks_executor.py main.yaml
```

### Option 2: Run with One-Command Execution
```bash
# From this directory
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

## Expected Output
The workflow will:
1. **Setup**: Create `parallel_outputs/` directory
2. **Parallel Execution**: Run 4 tasks simultaneously:
   - Task 1: Count from 1 to 5 (takes ~5 seconds)
   - Task 2: Print letters A to E (takes ~5 seconds)
   - Task 3: Gather system information (takes ~2 seconds)
   - Task 4: Create test files (takes ~3 seconds)
3. **Verify**: Check all parallel tasks completed successfully
4. **Cleanup**: Remove the output directory

**Total execution time**: ~5 seconds (not 15+ seconds) because tasks run in parallel!

## Workflow Breakdown

### Block 1: Setup (Sequential)
```yaml
- name: "Setup"
  description: "Create output directory for parallel tasks"
  run: "mkdir -p parallel_outputs && echo 'Setup complete'"
```
Runs first, creating the output directory needed by parallel tasks.

### Block 2: Parallel Execution
```yaml
- parallel:
    - name: "Task 1 - Count to 5"
      run: |
        for i in 1 2 3 4 5; do
          echo "Task 1: Count $i"
          sleep 1
        done
        echo "Task 1: Complete!" > parallel_outputs/task1.txt
```

All four tasks start simultaneously and run concurrently. The framework:
- Spawns separate threads for each task
- Monitors their progress independently
- Waits for ALL tasks to complete before moving to the next sequential block

### Block 3: Verify Results (Sequential)
```yaml
- name: "Verify Results"
  description: "Check that all parallel tasks completed successfully"
  run: |
    echo "Verifying parallel execution results..."
    ls -la parallel_outputs/
```
Runs AFTER all parallel tasks complete, verifying their outputs.

### Block 4: Cleanup (Sequential)
```yaml
- name: "Cleanup"
  description: "Remove output directory"
  run: "rm -rf parallel_outputs && echo 'Cleanup complete!'"
```
Final cleanup step.

## Execution Timeline

```
Time 0s:  [Setup] ────────────────────────────► (completes)
          
Time 1s:  [Task 1] ─────────────────────────────────────────► (5s)
          [Task 2] ─────────────────────────────────────────► (5s)
          [Task 3] ───────────────────────► (2s)
          [Task 4] ─────────────────────────────► (3s)
          (All run simultaneously)
          
Time 6s:  [Verify] ────────────────────────────► (completes)
          
Time 7s:  [Cleanup] ───────────────────────────► (completes)

Total: ~7 seconds (vs ~15+ seconds if run sequentially)
```

## When to Use Parallel Execution

✅ **Good Use Cases:**
- Downloading multiple files from different sources
- Running tests on multiple servers
- Processing independent data chunks
- Deploying to multiple environments simultaneously
- Backing up multiple databases

❌ **When NOT to Use:**
- Tasks that depend on each other's output
- Tasks that modify the same files
- Tasks that compete for limited resources (e.g., all hitting the same API)

## Key Takeaways
- Parallel blocks dramatically reduce total execution time
- All tasks in a parallel block must complete before the workflow continues
- Each parallel task runs in its own thread with independent execution context
- Use parallel execution for independent tasks that don't interfere with each other

## Next Steps
- Try adding more tasks to the parallel block
- Experiment with different timing to see parallel speedup
- Explore the next example: **03-variable-interpolation**

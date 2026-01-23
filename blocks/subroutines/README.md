# Cocoon Subroutines

This directory contains subroutine versions of Cocoon scripts designed to be called from within other scripts while preserving the calling environment.

## run_blocks.sh - Subroutine Version

### Overview

This is a modified version of the main `run_blocks.sh` script that allows you to:
- Pass `TEMP_DIR` and `WORKFLOW_FILE` as script parameters
- Preserve existing `TEMP_DIR` and `WORKFLOW_FILE` environment variables
- Restore the original environment after execution

### Key Differences from Main Script

| Feature | Main Script | Subroutine Script |
|---------|-------------|-------------------|
| `TEMP_DIR` | Fixed as `.blocks_temp` | Passed as parameter 1 |
| `WORKFLOW_FILE` | Passed as parameter 1 | Passed as parameter 2 |
| `STORAGE_DIR` | Passed as parameter 2 | Passed as parameter 3 |
| Environment Preservation | No | Yes - saves and restores variables |

### Usage

#### Basic Syntax

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s <temp_dir> <workflow_file> [storage_dir]
```

#### Parameters

1. **`temp_dir`** (required) - Temporary directory for cloning the framework
2. **`workflow_file`** (required) - Path to your workflow YAML file
3. **`storage_dir`** (optional) - Path to configuration storage directory (default: `storage`)

### Examples

#### Example 1: Basic Usage with Custom Temp Directory

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .my_temp main.yaml
```

This will:
- Clone the framework into `.my_temp/` directory
- Execute `main.yaml` workflow
- Use default `storage/` directory for configs
- Clean up `.my_temp/` after completion
- Restore original `TEMP_DIR` and `WORKFLOW_FILE` environment variables

#### Example 2: Full Custom Parameters

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .blocks_build build.yaml config
```

This will:
- Clone framework into `.blocks_build/` directory
- Execute `build.yaml` workflow
- Use `config/` directory for configurations
- Clean up `.blocks_build/` after completion
- Restore environment variables

#### Example 3: Use in Parent Script

```bash
#!/bin/bash
# parent_script.sh - Your main automation script

# Set environment variables for your script
export TEMP_DIR="/tmp/my_app"
export WORKFLOW_FILE="my_app.yaml"

echo "Parent script starting..."
echo "TEMP_DIR: $TEMP_DIR"
echo "WORKFLOW_FILE: $WORKFLOW_FILE"

# Call Cocoon subroutine with its own parameters
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .cocoon_temp deploy.yaml production_config

# After subroutine completes, your original environment is restored
echo "Parent script continuing..."
echo "TEMP_DIR: $TEMP_DIR"  # Still "/tmp/my_app"
echo "WORKFLOW_FILE: $WORKFLOW_FILE"  # Still "my_app.yaml"
```

#### Example 4: Multiple Sequential Calls

```bash
#!/bin/bash
# Run multiple workflows without environment conflicts

# Run first workflow
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .temp1 setup.yaml

# Run second workflow with different parameters
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .temp2 build.yaml build_config

# Run third workflow
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .temp3 deploy.yaml deploy_config
```

### Use Cases

#### 1. CI/CD Pipeline Integration

```bash
#!/bin/bash
# ci_pipeline.sh

# Build stage
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .build_temp build.yaml

# Test stage
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .test_temp test.yaml

# Deploy stage
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .deploy_temp deploy.yaml
```

#### 2. Multi-Environment Deployments

```bash
#!/bin/bash
# deploy_all_envs.sh

environments=("dev" "staging" "production")

for env in "${environments[@]}"; do
    echo "Deploying to $env..."
    curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s ".temp_$env" "deploy.yaml" "config_$env"
done
```

#### 3. Nested Automation Workflows

```bash
#!/bin/bash
# master_automation.sh

export TEMP_DIR="/tmp/master"
export WORKFLOW_FILE="master.yaml"

# Pre-processing
echo "Running pre-processing..."
./preprocess.sh

# Call Cocoon workflow (environment preserved)
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .cocoon_work workflow.yaml

# Post-processing (original environment still intact)
echo "Running post-processing..."
./postprocess.sh
```

### Environment Preservation Details

The subroutine script automatically:

1. **Saves** existing environment variables before execution:
   ```bash
   SAVED_TEMP_DIR="${TEMP_DIR}"
   SAVED_WORKFLOW_FILE="${WORKFLOW_FILE}"
   ```

2. **Uses** parameter values during execution:
   ```bash
   TEMP_DIR="${1:-.blocks_temp}"
   WORKFLOW_FILE="${2:-main.yaml}"
   ```

3. **Restores** original values after completion:
   ```bash
   TEMP_DIR="${SAVED_TEMP_DIR}"
   WORKFLOW_FILE="${SAVED_WORKFLOW_FILE}"
   ```

### Comparison with Main Script

**When to use the main script:**
- Standalone workflow execution
- Simple one-off automation tasks
- Interactive command-line usage

**When to use the subroutine script:**
- Called from within another script
- Part of larger automation pipeline
- Need to preserve calling environment
- Multiple sequential workflow executions
- CI/CD integration

### Notes

- All three parameters are positional - provide them in order
- The script still cleans up the temporary directory after execution
- Error handling: Script exits on any error (`set -e`)
- Works with the same repository URL as the main script
- Compatible with all Cocoon workflow features

### Troubleshooting

**Issue:** "Repository already exists" error  
**Solution:** Use a unique `temp_dir` for each call or ensure cleanup completed

**Issue:** "Workflow file not found" error  
**Solution:** Ensure workflow file exists in parent directory relative to where script runs

**Issue:** Environment variables not restored  
**Solution:** Check if script completed successfully (no errors during execution)

### Related Documentation

- [Main run_blocks.sh Documentation](../README.md)
- [Cocoon Workflow Documentation](../README.md#writing-workflow-yaml-files)
- [Configuration Management](../README.md#configuration-management)

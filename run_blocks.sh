#!/bin/bash
# Blocks Executor - One-Command Installation and Execution Script
# This script clones the repository, installs dependencies, executes the workflow, and cleans up
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s my_workflow.yaml
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s my_workflow.yaml my_storage

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/DebalGhosh100/blocks.git"
TEMP_DIR=".blocks_temp"
WORKFLOW_FILE="${1:-main.yaml}"
STORAGE_DIR="${2:-storage}"

echo "============================================"
echo "Blocks Executor - One-Command Execution"
echo "============================================"

# Step 1: Clone repository
echo "[1/5] Cloning repository..."
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

# Step 2: Install dependencies
echo "[2/5] Installing dependencies..."
pip3 install -q -r requirements.txt

# Step 3: Execute workflow
echo "[3/5] Executing workflow..."
echo "Workflow file: $WORKFLOW_FILE"
echo "Storage directory: $STORAGE_DIR"
python3 blocks_executor.py "../$WORKFLOW_FILE" --storage "../$STORAGE_DIR"

# Step 4: Return to original directory
echo "[4/5] Returning to project directory..."
cd ..

# Step 5: Cleanup
echo "[5/5] Cleaning up framework files..."
rm -rf "$TEMP_DIR"

echo "============================================"
echo "Execution complete! Framework cleaned up."
echo "============================================"

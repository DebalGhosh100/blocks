#!/bin/bash
# Blocks Executor - One-Command Installation and Execution Script
# This script clones the repository, installs dependencies, executes the workflow, and cleans up
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s my_workflow.yaml
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s my_workflow.yaml my_parameters

set -e  # Exit on any error

# Set up alias for evaporate
alias evaporate='curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/evaporate/evaporate.sh | bash -s --'

# Configuration
REPO_URL="https://github.com/DebalGhosh100/blocks.git"
TEMP_DIR=".blocks_temp"
WORKFLOW_FILE="${1:-main.yaml}"
PARAMETERS_DIR="${2:-parameters}"

# Colors for terminal output
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}Cocoon - One-Command Execution${NC}"
echo -e "${CYAN}============================================${NC}"

# Step 1: Clone repository
echo -e "${YELLOW}[1/5] Cloning repository...${NC}"
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

# Step 2: Install dependencies
echo -e "${YELLOW}[2/5] Installing dependencies...${NC}"
pip3 install -q -r requirements.txt --break-system-packages

# Step 3: Execute workflow
echo -e "${YELLOW}[3/5] Executing workflow...${NC}"
echo -e "Workflow file: $WORKFLOW_FILE"
echo -e "Parameters directory: $PARAMETERS_DIR"
python3 blocks_executor.py "../$WORKFLOW_FILE" --parameters "../$PARAMETERS_DIR"

# Step 4: Return to original directory
echo -e "${YELLOW}[4/5] Returning to project directory...${NC}"
cd ..

# Step 5: Cleanup
echo -e "${YELLOW}[5/5] Cleaning up framework files...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Execution complete! Framework cleaned up.${NC}"
echo -e "${GREEN}============================================${NC}"

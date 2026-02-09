#!/bin/bash
# Blocks Executor Subroutine - Execute workflows as a subroutine within another script
# This script preserves existing TEMP_DIR and WORKFLOW_FILE environment variables
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subro utines/run_blocks.sh | bash -s <temp_dir> <workflow_file> [parameters_dir]
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s .my_temp main.yaml parameters

set -e  # Exit on any error

# Store existing environment variables if they exist
SAVED_TEMP_DIR="${TEMP_DIR}"
SAVED_WORKFLOW_FILE="${WORKFLOW_FILE}"

# Configuration - Take from script parameters
REPO_URL="https://github.com/DebalGhosh100/blocks.git"
TEMP_DIR="${1:-.blocks_temp}"
WORKFLOW_FILE="${2:-main.yaml}"
PARAMETERS_DIR="${3:-parameters}"

# Colors for terminal output
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}Cocoon Subroutine - One-Command Execution${NC}"
echo -e "${CYAN}============================================${NC}"

# Step 1: Clone repository
echo -e "${YELLOW}[1/5] Cloning repository...${NC}"
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

# Step 2: Install dependencies
echo -e "${YELLOW}[2/5] Installing dependencies...${NC}"
pip3 install -r requirements.txt --break-system-packages

# Step 3: Execute workflow
echo -e "${YELLOW}[3/5] Executing workflow...${NC}"
echo -e "Workflow file: $WORKFLOW_FILE"
echo -e "Parameters directory: $PARAMETERS_DIR"
python3 -u blocks_executor.py "../$WORKFLOW_FILE" --parameters "../$PARAMETERS_DIR"

# Step 4: Return to original directory
echo -e "${YELLOW}[4/5] Returning to project directory...${NC}"
cd ..

# Step 5: Cleanup
echo -e "${YELLOW}[5/5] Cleaning up framework files...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Execution complete! Framework cleaned up.${NC}"
echo -e "${GREEN}============================================${NC}"

# Restore original environment variables
TEMP_DIR="${SAVED_TEMP_DIR}"
WORKFLOW_FILE="${SAVED_WORKFLOW_FILE}"

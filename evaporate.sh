#!/bin/bash

# Evaporate - Clone, Execute, Cleanup Pattern for Cocoon Workflows
# This script clones a specific branch from a repository, executes its workflow, and cleans up
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/evaporate.sh | bash -s -- <branch> <repo_url> [files_to_exclude...]
#   
# Arguments:
#   $1 - Branch name (required) - The branch containing the workflow to execute
#   $2 - Repository URL (required) - The git repository to clone
#   $3+ - Additional files/folders to remove (optional) - Space-separated list
#
# Example:
#   curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/evaporate.sh | bash -s -- \
#     flash-os-img-link-into-multiple-machines \
#     https://github.com/intel-sandbox/yocto.qa-automation.git \
#     .git .gitattributes README.md

set -e  # Exit on any error

# Check if minimum required parameters are provided
if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 <branch> <repository_url> [files_to_exclude...]"
    echo ""
    echo "Example:"
    echo "  $0 my-workflow https://github.com/user/repo.git .git README.md"
    exit 1
fi

# Parse parameters
BRANCH="$1"
REPO_URL="$2"
shift 2  # Remove first two arguments, remaining args are files to exclude
EXCLUDE_FILES=("$@")

# Default files/folders to exclude (will be removed after cloning)
DEFAULT_EXCLUDES=(".git" ".gitattributes")

# Temporary directory for cloning
TEMP_CLONE_DIR=".temp_workflow_clone_$$"

# Colors for terminal output
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}Evaporate - Cocoon Workflow Execution${NC}"
echo -e "${CYAN}============================================${NC}"

# Step 1: Clone the workflow repository
echo -e "${YELLOW}[1/6] Cloning workflow repository...${NC}"
echo -e "Branch: ${CYAN}$BRANCH${NC}"
echo -e "Repository: ${CYAN}$REPO_URL${NC}"

if ! git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$TEMP_CLONE_DIR" 2>&1; then
    echo -e "${RED}Error: Failed to clone repository branch '$BRANCH'${NC}"
    echo -e "${RED}Please verify the branch name and repository URL${NC}"
    exit 1
fi

# Step 2: Copy workflow files to current directory
echo -e "${YELLOW}[2/6] Copying workflow files...${NC}"
# Copy all files including hidden ones (except . and ..)
cp -r "$TEMP_CLONE_DIR"/. . 2>/dev/null || true

# Step 3: Remove the temporary clone directory
echo -e "${YELLOW}[3/6] Cleaning up temporary files...${NC}"
rm -rf "$TEMP_CLONE_DIR"

# Remove default excluded files
for item in "${DEFAULT_EXCLUDES[@]}"; do
    if [ -e "$item" ]; then
        rm -rf "$item"
    fi
done

# Remove additional excluded files if specified
if [ ${#EXCLUDE_FILES[@]} -gt 0 ]; then
    for item in "${EXCLUDE_FILES[@]}"; do
        if [ -e "$item" ]; then
            echo -e "Excluding: $item"
            rm -rf "$item"
        fi
    done
fi

# Step 4: Prepare storage directory
echo -e "${YELLOW}[4/6] Preparing storage directory...${NC}"
# If user has config files in current directory, they override the workflow's storage files
# Copy user's YAML files to storage directory (these will override workflow defaults)
if ls *.yaml 1> /dev/null 2>&1; then
    mkdir -p storage
    for yaml_file in *.yaml; do
        if [ "$yaml_file" != "main.yaml" ]; then
            echo -e "Using local configuration: ${GREEN}$yaml_file${NC}"
            cp -f "$yaml_file" storage/
        fi
    done
fi

# Step 5: Execute the workflow using Cocoon
echo -e "${YELLOW}[5/6] Executing Cocoon workflow...${NC}"
if [ ! -f "main.yaml" ]; then
    echo -e "${RED}Error: main.yaml not found in branch '$BRANCH'${NC}"
    exit 1
fi

curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash

# Step 6: Cleanup workflow files
echo -e "${YELLOW}[6/6] Cleaning up workflow files...${NC}"
rm -f main.yaml
rm -rf storage

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Evaporate execution complete!${NC}"
echo -e "${GREEN}============================================${NC}"

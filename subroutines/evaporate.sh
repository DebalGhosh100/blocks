#!/bin/bash

# Script to clone a git repository, copy files, and run blocks
# Usage: ./evaporate.sh <git_branch> <git_repo_url> [additional_files_to_remove...]

set -e

# Check if minimum required parameters are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <git_branch> <git_repo_url> [additional_files_to_remove...]"
    exit 1
fi

# Parse parameters
GIT_BRANCH="$1"
GIT_REPO="$2"
shift 2  # Remove first two arguments, remaining args are additional files to remove
ADDITIONAL_FILES=("$@")

# Extract repo name from URL (remove .git suffix and get last part)
REPO_NAME=$(basename "$GIT_REPO" .git)

# Set global variable for renamed main.yaml file
NEW_MAIN_NAME="${REPO_NAME}-${GIT_BRANCH}-main"

# Default files/folders to remove
DEFAULT_REMOVES=("${NEW_MAIN_NAME}.yaml")

echo "=== Cloning repository ==="
echo "Branch: $GIT_BRANCH"
echo "Repository: $GIT_REPO"
echo "Repository name: $REPO_NAME"

# Clone into a temporary directory
git clone --branch "$GIT_BRANCH" "$GIT_REPO" temp-clone

echo "=== Handling storage directory merge ==="
# Handle storage directory merging before copying other files
if [ -d "temp-clone/storage" ]; then
    if [ -d "storage" ]; then
        echo "Merging storage directories (temp-clone/storage will override existing files)"
        # Copy/overwrite files from temp-clone/storage to current storage
        cp -rf temp-clone/storage/* storage/ 2>/dev/null || true
        # Remove storage from temp-clone to avoid duplication during main copy
        rm -rf temp-clone/storage
    else
        echo "Creating storage directory from temp-clone"
        # Storage doesn't exist locally, will be copied during main copy
    fi
else
    echo "No storage directory in temp-clone"
fi

echo "=== Renaming main.yaml ==="
# Rename main.yaml if it exists in temp-clone
if [ -f "temp-clone/main.yaml" ]; then
    echo "Renaming main.yaml to ${NEW_MAIN_NAME}.yaml"
    mv "temp-clone/main.yaml" "temp-clone/${NEW_MAIN_NAME}.yaml"
else
    echo "Warning: main.yaml not found in temp-clone"
fi

echo "=== Copying files to current directory ==="
# Copy all files (including hidden ones) to current directory
cp -r temp-clone/* temp-clone/.[!.]* . 2>/dev/null || true

echo "=== Cleaning up temporary clone ==="
# Remove the temporary directory and git-related files
rm -rf temp-clone

echo "=== Creating storage and backing up YAML files ==="
mkdir -p storage


echo "=== Running blocks script ==="
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/subroutines/run_blocks.sh | bash -s "${NEW_MAIN_NAME}_temp" "${NEW_MAIN_NAME}.yaml" storage 2>&1

echo "=== Cleaning up default files/folders ==="
for item in "${DEFAULT_REMOVES[@]}"; do
    if [ -e "$item" ]; then
        echo "Removing: $item"
        rm -rf "$item"
    fi
done

echo "=== Setup and execution complete ==="

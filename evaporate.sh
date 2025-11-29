#!/bin/bash

# Script to clone a git repository, copy files, and run blocks
# Usage: ./setup_and_run.sh <git_branch> <git_repo_url> [additional_files_to_remove...]

set -e

# Check if minimum required parameters are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <git_branch> <git_repo_url> [additional_files_to_remove...]"
    echo "Example: $0 execution-setup-yaml https://github.com/intel-innersource/os.linux.yocto-core.validation.yp-qa-results.git config.ini data/"
    exit 1
fi

# Parse parameters
GIT_BRANCH="$1"
GIT_REPO="$2"
shift 2  # Remove first two arguments, remaining args are additional files to remove
ADDITIONAL_FILES=("$@")

# Default files/folders to remove
DEFAULT_REMOVES=("main.yaml" "storage")

echo "=== Cloning repository ==="
echo "Branch: $GIT_BRANCH"
echo "Repository: $GIT_REPO"

# Clone into a temporary directory
git clone --branch "$GIT_BRANCH" "$GIT_REPO" temp-clone

echo "=== Copying files to current directory ==="
# Copy all files (including hidden ones) to current directory
cp -r temp-clone/* temp-clone/.[!.]* . 2>/dev/null || true

echo "=== Cleaning up temporary clone ==="
# Remove the temporary directory and git-related files
rm -rf temp-clone .git .gitattributes README.md

echo "=== Creating storage and backing up YAML files ==="
mkdir -p storage
# Copy/overwrite YAML files to storage directory
for yaml_file in *.yaml 2>/dev/null; do
    if [ -f "$yaml_file" ]; then
        cp -f "$yaml_file" storage/
    fi
done

echo "=== Running blocks script ==="
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash

echo "=== Cleaning up default files/folders ==="
for item in "${DEFAULT_REMOVES[@]}"; do
    if [ -e "$item" ]; then
        echo "Removing: $item"
        rm -rf "$item"
    fi
done

# Remove additional files/folders if specified
if [ ${#ADDITIONAL_FILES[@]} -gt 0 ]; then
    echo "=== Cleaning up additional files/folders ==="
    for item in "${ADDITIONAL_FILES[@]}"; do
        if [ -e "$item" ]; then
            echo "Removing: $item"
            rm -rf "$item"
        else
            echo "Warning: $item not found, skipping"
        fi
    done
fi

echo "=== Setup and execution complete ==="

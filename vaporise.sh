#!/bin/bash

# vaporise.sh - A lightweight tool to clone and extract specific parts of Git repositories
# Usage: curl -sSL <raw-github-url> | bash -s -- <repo> <branch> [sub-directory] [token]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "${BOLD}${BLUE}============================================${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}============================================${NC}"
}

# Function to display usage
usage() {
    echo "Usage: $0 <repository-name> <branch-name> [sub-directory] [token]"
    echo ""
    echo "Mandatory Parameters:"
    echo "  repository-name    GitHub repository in format 'owner/repo'"
    echo "  branch-name        Branch to clone"
    echo ""
    echo "Optional Parameters:"
    echo "  sub-directory      Specific subdirectory to extract (optional)"
    echo "  token              GitHub personal access token for private repos (optional)"
    echo ""
    echo "Examples:"
    echo "  # Clone entire repository"
    echo "  $0 DebalGhosh100/blocks main"
    echo ""
    echo "  # Clone specific subdirectory"
    echo "  $0 DebalGhosh100/blocks main examples/01-basic-sequential"
    echo ""
    echo "  # Clone private repository with token"
    echo "  $0 owner/private-repo main \"\" github_pat_xxx"
    echo ""
    echo "  # Clone specific subdirectory from private repo"
    echo "  $0 owner/private-repo main src/components github_pat_xxx"
    exit 1
}

# Parse arguments
REPO_NAME="$1"
BRANCH_NAME="$2"
SUB_DIRECTORY="$3"
TOKEN="$4"

# Validate mandatory parameters
if [ -z "$REPO_NAME" ] || [ -z "$BRANCH_NAME" ]; then
    print_error "Missing mandatory parameters!"
    usage
fi

# Validate repository name format
if [[ ! "$REPO_NAME" =~ ^[^/]+/[^/]+$ ]]; then
    print_error "Invalid repository format. Expected 'owner/repo', got '$REPO_NAME'"
    exit 1
fi

# Extract owner and repo
OWNER=$(echo "$REPO_NAME" | cut -d'/' -f1)
REPO=$(echo "$REPO_NAME" | cut -d'/' -f2)

# Display configuration
print_header "Vaporise - Repository Extractor"
print_info "Repository: ${BOLD}$REPO_NAME${NC}"
print_info "Branch: ${BOLD}$BRANCH_NAME${NC}"

if [ -n "$SUB_DIRECTORY" ]; then
    print_info "Sub-directory: ${BOLD}$SUB_DIRECTORY${NC}"
else
    print_info "Sub-directory: ${BOLD}(entire repository)${NC}"
fi

if [ -n "$TOKEN" ]; then
    print_info "Authentication: ${BOLD}Using provided token${NC}"
else
    print_info "Authentication: ${BOLD}Public access${NC}"
fi

echo ""

# Build clone URL
if [ -n "$TOKEN" ]; then
    CLONE_URL="https://${OWNER}:${TOKEN}@github.com/${REPO_NAME}.git"
else
    CLONE_URL="https://github.com/${REPO_NAME}.git"
fi

# Step 1: Clone repository
TEMP_DIR=".repo"
print_info "[1/4] Cloning repository..."

if [ -d "$TEMP_DIR" ]; then
    print_warning "Temporary directory '$TEMP_DIR' already exists. Removing..."
    rm -rf "$TEMP_DIR"
fi

if git clone --branch "$BRANCH_NAME" --depth 1 "$CLONE_URL" "$TEMP_DIR" 2>&1; then
    print_success "Repository cloned successfully"
else
    print_error "Failed to clone repository. Check your repository name, branch, and token (if private)."
    exit 1
fi

# Step 2: Verify sub-directory exists (if specified)
if [ -n "$SUB_DIRECTORY" ]; then
    print_info "[2/4] Verifying sub-directory..."
    if [ ! -d "$TEMP_DIR/$SUB_DIRECTORY" ]; then
        print_error "Sub-directory '$SUB_DIRECTORY' not found in repository"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    print_success "Sub-directory found"
else
    print_info "[2/4] No sub-directory specified, will extract entire repository"
fi

# Step 3: Copy files to current directory
print_info "[3/4] Copying files to current directory..."

if [ -n "$SUB_DIRECTORY" ]; then
    # Copy specific subdirectory
    SOURCE_PATH="$TEMP_DIR/$SUB_DIRECTORY"
    
    # Copy all files and directories from subdirectory to current directory
    if cp -r "$SOURCE_PATH"/* . 2>/dev/null; then
        print_success "Sub-directory contents copied"
    else
        print_warning "No files found in sub-directory or copy failed"
    fi
    
    # Copy hidden files if they exist
    if cp -r "$SOURCE_PATH"/.[!.]* . 2>/dev/null; then
        print_success "Hidden files copied"
    fi
else
    # Copy entire repository (excluding .git)
    shopt -s dotglob  # Enable matching hidden files
    
    for item in "$TEMP_DIR"/*; do
        # Skip .git directory
        if [ "$(basename "$item")" != ".git" ]; then
            if cp -r "$item" . 2>/dev/null; then
                print_success "Copied: $(basename "$item")"
            fi
        fi
    done
    
    shopt -u dotglob  # Disable matching hidden files
fi

# Step 4: Cleanup
print_info "[4/4] Cleaning up..."
rm -rf "$TEMP_DIR"
print_success "Temporary directory removed"

echo ""
print_header "Extraction Complete!"

# List what was extracted
if [ -n "$SUB_DIRECTORY" ]; then
    print_success "Extracted '${SUB_DIRECTORY}' from ${REPO_NAME}/${BRANCH_NAME}"
else
    print_success "Extracted entire repository from ${REPO_NAME}/${BRANCH_NAME}"
fi

print_info "Files are now available in the current directory"
echo ""

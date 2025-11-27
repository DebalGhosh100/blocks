# Evaporate

A shell script to clone a git repository, copy its contents, and run blocks automation.

## Usage

Run directly from the repository using curl:

```bash
curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/evaporate.sh | bash -s -- <git_branch> <git_repo_url> [additional_files_to_remove...]
```

### Parameters

1. `git_branch` - The branch to clone from the target repository
2. `git_repo_url` - The URL of the repository to clone
3. `[additional_files_to_remove...]` - Optional additional files/folders to remove at the end

### Examples

Basic usage:
```bash
curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/evaporate.sh | bash -s -- \
  execution-setup-yaml \
  https://github.com/intel-innersource/os.linux.yocto-core.validation.yp-qa-results.git
```

With additional files to remove:
```bash
curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/evaporate.sh | bash -s -- \
  execution-setup-yaml \
  https://github.com/intel-innersource/os.linux.yocto-core.validation.yp-qa-results.git \
  config.ini logs/
```

### What it does

1. Clones the specified repository and branch into a temporary directory
2. Copies all files (including hidden ones) to the current directory
3. Cleans up temporary files and git metadata
4. Backs up YAML files to a `storage/` directory
5. Runs the blocks automation script
6. Removes `main.yaml` and `storage/` by default
7. Removes any additional files/folders you specify

### Local Usage

You can also download and run the script locally:

```bash
curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/evaporate.sh -o evaporate.sh
chmod +x evaporate.sh
./evaporate.sh <git_branch> <git_repo_url> [additional_files_to_remove...]
```

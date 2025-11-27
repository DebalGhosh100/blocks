
# Evaporate

A shell script to clone a git repository, create a 'storage' directory, copy all yamls in the current-directory into the newly created storage directory, and run the cocoon blocks-automation script.

## Usage

Run directly from the repository using curl:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/evaporate/evaporate.sh | bash -s -- <git_branch> <git_repo_url> [additional_files_to_remove...]
```

### Parameters

1. `git_branch` - The branch to clone from the target repository
2. `git_repo_url` - The URL of the repository to clone
3. `[additional_files_to_remove...]` - Optional additional files/folders to remove at the end


### Local Usage

You can also download and run the script locally:

```bash
curl -sSL https://raw.githubusercontent.com/<owner>/<repo>/<branch>/evaporate.sh -o evaporate.sh
chmod +x evaporate.sh
./evaporate.sh <git_branch> <git_repo_url> [additional_files_to_remove...]
```


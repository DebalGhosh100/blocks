
# Evaporate

A shell script to clone a git repository, create a 'storage' directory, copy all yamls in the current-directory into the newly created storage directory, and run the cocoon blocks-automation script.

**Having created a main.yaml file and a storage directory [and other scripting aids] as instructed in cocoon's main documentation, just push main.yaml, the scripting aids and potentially a few yamls from the storage directory which contain default values into a repo and simply chug the curl -sSL command below that takes in your repo as parameter.**

## Usage

Run directly from the repository using curl:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/evaporate/evaporate.sh | bash -s -- <git_branch> <git_repo_url> [additional_files_to_remove...]
```
**All yamls in your current directory will be dumped in [and / or] overridden in the storage directory when the remote procedural-call is made using this curl.**


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



# Vaporise

**Vaporise** is a lightweight shell script that allows you to quickly clone and extract specific parts of Git repositories without maintaining the full Git history. Perfect for grabbing examples, templates, or specific project subdirectories.

## 🚀 Features

- ✅ **One-Command Extraction**: Clone and extract with a single curl command
- ✅ **Subdirectory Support**: Extract only specific folders from repositories
- ✅ **Private Repository Access**: Supports GitHub personal access tokens
- ✅ **Shallow Cloning**: Uses `--depth 1` for fast downloads
- ✅ **Auto Cleanup**: Automatically removes Git metadata after extraction
- ✅ **Branch Selection**: Clone from any branch, not just main

## 📋 Prerequisites

- `bash` shell
- `git` command-line tool
- `curl` (for one-command execution)

## 🎯 Usage

### Basic Syntax

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- <repository-name> <branch-name> [sub-directory] [token]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `repository-name` | ✅ Yes | GitHub repository in format `owner/repo` |
| `branch-name` | ✅ Yes | Branch to clone from |
| `sub-directory` | ❌ No | Specific subdirectory to extract (leave empty for entire repo) |
| `token` | ❌ No | GitHub personal access token for private repositories |

## 📚 Examples

### Example 1: Clone Entire Public Repository

Extract everything from the `main` branch:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- DebalGhosh100/blocks main
```

**What happens:**
- Clones the entire `DebalGhosh100/blocks` repository from `main` branch
- Copies all files to current directory (excluding `.git`)
- Removes temporary clone directory

### Example 2: Clone Specific Subdirectory

Extract only the `examples/01-basic-sequential` folder:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- DebalGhosh100/blocks main examples/01-basic-sequential
```

**What happens:**
- Clones the repository
- Extracts only files from `examples/01-basic-sequential`
- Copies them to current directory
- Cleans up temporary files

### Example 3: Clone from Different Branch

Extract from a specific branch:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- DebalGhosh100/blocks develop
```

### Example 4: Clone Private Repository

Use a GitHub token to access private repositories:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- owner/private-repo main "" github_pat_xxxxxxxxxxxxx
```

**Note:** Pass empty string `""` for sub-directory parameter if you want the entire repo but need to provide a token.

### Example 5: Clone Specific Subdirectory from Private Repo

Combine subdirectory extraction with authentication:

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- owner/private-repo main src/components github_pat_xxxxxxxxxxxxx
```

## 🔐 Using GitHub Tokens

### When Do You Need a Token?

- Accessing private repositories
- Avoiding GitHub API rate limits
- Accessing repositories from organizations with SSO

### How to Create a Token

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Vaporise CLI")
4. Select scopes:
   - ✅ `repo` (for private repositories)
   - ✅ `public_repo` (for public repositories only)
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)

### Token Format

Tokens start with `github_pat_` or `ghp_`:
```
github_pat_11A7HDVWY0JTlp6Rv9CvwO_Ce1vxCIkutMO7wuOrH7IZS30SVCKzkYzyGckk3lGNEp...
```

## 🛠️ Local Usage (Without curl)

You can also download and run the script locally:

```bash
# Download the script
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh -o vaporise.sh

# Make it executable
chmod +x vaporise.sh

# Run it
./vaporise.sh DebalGhosh100/blocks main examples/01-basic-sequential
```

## ⚡ Create an Alias for Quick Access

For even faster usage, create a shell alias to avoid typing the full curl command:

### Bash/Zsh

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
echo "alias vaporise='curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s --'" >> ~/.bashrc
source ~/.bashrc
```

### Usage After Aliasing

Once the alias is set up, you can use vaporise directly:

```bash
# Extract specific subdirectory
vaporise DebalGhosh100/blocks main examples/01-basic-sequential

# Extract entire repository
vaporise DebalGhosh100/blocks main

# Private repo with token
vaporise owner/private-repo main "" github_pat_xxx

# Subdirectory from private repo
vaporise owner/private-repo main src/components github_pat_xxx
```

**Benefits:**
- ⚡ Shorter command
- 🎯 Cleaner syntax
- 🚀 Works from anywhere
- 💾 No local script needed

## 💡 Use Cases

### 1. Grab Example Projects

Quickly get started with example code:
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- facebook/react main packages/react-dom
```

### 2. Extract Project Templates

Bootstrap new projects with templates:
```bash
mkdir my-new-project && cd my-new-project
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- vercel/next.js main examples/blog-starter
```

### 3. Clone Internal Tools

Access company-internal repositories:
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- mycompany/internal-tools main scripts "" $GITHUB_TOKEN
```

### 4. Educational Content

Extract specific chapters or sections from learning repositories:
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- owner/course-materials main week-3/exercises
```

## 🔍 How It Works

1. **Clone**: Shallow clones (`--depth 1`) the specified repository and branch into a temporary `.repo` directory
2. **Extract**: 
   - If sub-directory specified: copies only that folder's contents to current directory
   - If no sub-directory: copies entire repository (excluding `.git`) to current directory
3. **Cleanup**: Removes the temporary `.repo` directory, leaving only the extracted files

## ⚠️ Important Notes

### Files in Current Directory

Vaporise copies files directly into your current working directory. Make sure you're in the right location:

```bash
# Good practice: create a new directory first
mkdir my-project && cd my-project
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- owner/repo main
```

### Existing Files

If files with the same name already exist, they will be **overwritten**. Be careful!

### No Git History

Vaporise is designed for extraction, not for maintaining Git repositories. The extracted files will **not** have:
- Git history
- Remote connections
- Branch information

If you need full Git functionality, use `git clone` directly.

## 🐛 Troubleshooting

### Error: "Failed to clone repository"

**Possible causes:**
- Incorrect repository name format (should be `owner/repo`)
- Branch doesn't exist
- Private repository without token
- Invalid or expired token
- Network connectivity issues

**Solution:**
```bash
# Verify repository exists on GitHub
# Check branch name (case-sensitive)
# Ensure token has correct permissions
```

### Error: "Sub-directory not found"

**Cause:** The specified subdirectory doesn't exist in the repository.

**Solution:**
```bash
# List available directories first by cloning the entire repo
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh | bash -s -- owner/repo main
ls -la
# Then re-run with correct path
```

### Warning: "Temporary directory already exists"

**Cause:** Previous run didn't complete successfully, leaving `.repo` directory.

**Solution:** Vaporise automatically removes it, but you can manually clean up:
```bash
rm -rf .repo
```

## 📖 Comparison with Git Clone

| Feature | Vaporise | Git Clone |
|---------|----------|-----------|
| Speed | ⚡ Fast (shallow) | 🐌 Slower (full history) |
| Disk Usage | 💾 Minimal | 💾 Higher |
| Git History | ❌ No | ✅ Yes |
| Subdirectory Only | ✅ Yes | ❌ No (requires sparse-checkout) |
| Auto Cleanup | ✅ Yes | ❌ Manual |
| Best For | Templates, examples, extraction | Development, contributions |

## 🤝 Contributing

This is a single-script tool, so contributions are straightforward:

1. Fork the repository
2. Edit `vaporise.sh`
3. Test your changes
4. Submit a pull request

## 📄 License

This script is open source and available for use in any project.

## 🔗 Links

- **Repository**: https://github.com/DebalGhosh100/blocks
- **Raw Script**: https://raw.githubusercontent.com/DebalGhosh100/blocks/tooling/vaporise.sh
- **Report Issues**: https://github.com/DebalGhosh100/blocks/issues

## 💬 Quick Reference

```bash
# Entire public repo
curl -sSL <script-url> | bash -s -- owner/repo branch

# Specific subdirectory
curl -sSL <script-url> | bash -s -- owner/repo branch path/to/dir

# Private repo (entire)
curl -sSL <script-url> | bash -s -- owner/repo branch "" token

# Private repo (subdirectory)
curl -sSL <script-url> | bash -s -- owner/repo branch path/to/dir token
```

---

**Made with ❤️ for developers who want to move fast**















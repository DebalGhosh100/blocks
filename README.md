# Cocoon Paraphrase 🔐

**Compress, Share, and Deploy Cocoon Workflows with a Single Base64 String**

Cocoon Paraphrase is a powerful tooling utility that allows you to compress entire YAML-based workflow directories into portable base64-encoded strings. Share your Cocoon configurations, deploy them across machines, and recreate complex workflow structures with a single command.

---

## 🚀 Quick Start

### Install via curl

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/paraphrase.sh -o paraphrase.sh && chmod +x paraphrase.sh
```

### Encode a Workflow Directory

```bash
./paraphrase.sh /path/to/your/yaml/directory
```

### Decode and Execute

```bash
echo "IyEvYmluL2Jhc2gKCiMgQ29jb29uIFdvcmtmbG93IFN0cnVjdHVyZSBTZXR1cCBTY3JpcHQKIyBHZW5lcmF0ZWQgZnJvbSBDb2Nvb24gUGFyYXBocmFzZQoKc2V0IC1lICAjIEV4aXQgb24gYW55IGVycm9yCgplY2hvICJDcmVhdGluZyB3b3JrZmxvdyBzdHJ1Y3R1cmUuLi4iCmVjaG8gIiIKCmNhdCA+ICJtYWluLnlhbWwiIDw8ICdFT0YnCmJsb2NrczoKICAtIHJ1bjogJ2VjaG8gIkhlbGxvLCBDb2Nvb24hIicKRU9GCgplY2hvICIiCmVjaG8gIuKck+KAiCBXb3JrZmxvdyBzdHJ1Y3R1cmUgY3JlYXRlZCBzdWNjZXNzZnVsbHkhIgplY2hvICJSdW4gJ2NvY29vbiBtYWluLnlhbWwnIHRvIGV4ZWN1dGUgeW91ciB3b3JrZmxvdy4iCg==" | base64 -d | bash
```

---

## 📖 Table of Contents

1. [What is Cocoon Paraphrase?](#what-is-cocoon-paraphrase)
2. [Installation](#installation)
3. [Usage](#usage)
   - [Encoding Workflows](#encoding-workflows)
   - [Decoding Workflows](#decoding-workflows)
4. [Use Cases](#use-cases)
5. [Examples](#examples)
6. [How It Works](#how-it-works)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)

---

## 🎯 What is Cocoon Paraphrase?

Cocoon Paraphrase solves the problem of sharing and deploying complex workflow configurations across different machines and environments. Instead of:

- Manually copying multiple YAML files
- Zipping and transferring directories
- Managing version control for simple configurations
- Setting up repository access for quick tests

You can now:

- **Encode** an entire workflow directory into a single base64 string
- **Share** the string via chat, email, or documentation
- **Deploy** instantly on any Linux machine with `echo | base64 -d | bash`
- **Version** workflows as simple text strings

---

## 💾 Installation

### Method 1: Direct Download (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/paraphrase.sh -o paraphrase.sh
chmod +x paraphrase.sh
```

### Method 2: Clone Repository

```bash
git clone -b paraphrase https://github.com/DebalGhosh100/blocks.git
cd blocks
chmod +x paraphrase.sh
```

### Method 3: Add to PATH

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/paraphrase.sh -o ~/bin/cocoon-paraphrase
chmod +x ~/bin/cocoon-paraphrase
export PATH="$HOME/bin:$PATH"
```

---

## 🔧 Usage

### Encoding Workflows

The `paraphrase.sh` script scans a directory for all YAML files and generates a base64-encoded string that can recreate the entire structure.

#### Basic Usage

```bash
# Encode current directory
./paraphrase.sh

# Encode specific directory
./paraphrase.sh /path/to/workflow
```

#### Example Output

```
Cocoon Paraphrase - YAML Workflow Encoder
==========================================

Scanning directory: /home/user/my-workflow

Found 3 YAML file(s)

  ✓ Encoded: main.yaml
  ✓ Encoded: parameters/config.yaml
  ✓ Encoded: parameters/servers.yaml

Generating base64 paraphrase...

========================================
Paraphrase Generated Successfully!
========================================

Original Size: 12K
Encoded Size: 1847 characters

Copy the following base64 string:

----------------------------------------
IyEvYmluL2Jhc2gKCnNldCAtZQoKZWNobyAiQ3JlYXRpbmcgd29ya2Zsb3cgc3RydWN0dXJlLi4uIg...
----------------------------------------

To recreate this workflow on another machine:

  echo "IyEvYmluL2Jhc2gK..." | base64 -d | bash
```

### Decoding Workflows

Once you have a base64 paraphrase string, you can recreate the workflow on any machine:

#### Method 1: Direct Execution

```bash
echo "YOUR_BASE64_STRING_HERE" | base64 -d | bash
```

#### Method 2: Save and Execute

```bash
# Save to variable
WORKFLOW="YOUR_BASE64_STRING_HERE"

# Create workflow structure
echo "$WORKFLOW" | base64 -d | bash

# Execute workflow
cocoon main.yaml
```

#### Method 3: Remote Deployment

```bash
# Store your paraphrase string in a URL-accessible location
curl -sSL https://example.com/my-workflow-paraphrase.txt | base64 -d | bash
```

---

## 🎨 Use Cases

### 1. **Quick Workflow Sharing**

Share Cocoon workflows with team members without repository access:

```bash
# Developer A encodes workflow
./paraphrase.sh my-deployment-workflow

# Developer B recreates it instantly
echo "IyEvYmluL2Jhc2gK..." | base64 -d | bash
```

### 2. **Documentation Examples**

Embed complete, executable workflow examples in documentation:

```markdown
Try this Cocoon workflow:
\`\`\`bash
echo "IyEvYmluL2Jhc2gKCnNl..." | base64 -d | bash && cocoon main.yaml
\`\`\`
```

### 3. **CI/CD Integration**

Deploy workflow configurations dynamically in pipelines:

```yaml
# GitLab CI example
deploy_workflow:
  script:
    - echo "$WORKFLOW_PARAPHRASE" | base64 -d | bash
    - cocoon main.yaml
```

### 4. **Remote Machine Setup**

Bootstrap Cocoon workflows on remote servers:

```bash
ssh user@server "echo 'IyEvYmluL2Jhc2gK...' | base64 -d | bash"
```

### 5. **Backup and Versioning**

Store workflow snapshots as text strings:

```bash
# Backup current state
./paraphrase.sh > backup-$(date +%Y%m%d).txt

# Restore from backup
cat backup-20260210.txt | base64 -d | bash
```

---

## 📚 Examples

### Example 1: Simple Sequential Workflow

**Original Structure:**
```
my-workflow/
├── main.yaml
└── parameters/
    └── config.yaml
```

**Encode:**
```bash
./paraphrase.sh my-workflow
```

**Output Paraphrase:**
```
IyEvYmluL2Jhc2gKCnNldCAtZQoKZWNobwogIkNyZWF0aW5nIHdvcmtmbG93IHN0cnVjdHVyZS4uLiIKZWNobyAiIgoKY2F0ID4gIm1haW4ueWFtbCIgPDwgJ0VPRicKYmxvY2tzOgogIC0gcnVuOiAnZWNobyAiU3RlcCAxOiBDb25maWd1cmF0aW9uIicKICAtIHJ1bjogJ2VjaG8gIlN0ZXAgMjogRGVwbG95bWVudCInCkVPRgoKbWtkaXIgLXAgInBhcmFtZXRlcnMiCmNhdCA+ICJwYXJhbWV0ZXJzL2NvbmZpZy55YW1sIiA8PCAnRU9GJwplbnZpcm9ubWVudDogcHJvZHVjdGlvbgpyZXBsaWNhczogMwpFT0YKCmVjaG8gIiIKZWNobyAi4pyT4oCIIFdvcmtmbG93IHN0cnVjdHVyZSBjcmVhdGVkIHN1Y2Nlc3NmdWxseSEiCmVjaG8gIlJ1biAnY29jb29uIG1haW4ueWFtbCcgdG8gZXhlY3V0ZSB5b3VyIHdvcmtmbG93LiIK
```

**Recreate:**
```bash
mkdir test-recreation && cd test-recreation
echo "IyEvYmluL2Jhc2gKCnNldCAtZQoK..." | base64 -d | bash
```

### Example 2: Complex Multi-File Workflow

**Original Structure:**
```
complex-workflow/
├── main.yaml
├── parameters/
│   ├── servers.yaml
│   ├── databases.yaml
│   └── credentials.yaml
└── README.md
```

**Encode:**
```bash
./paraphrase.sh complex-workflow
```

**Deploy to Remote Server:**
```bash
# Store paraphrase in environment variable on CI/CD
export WORKFLOW_PARAPHRASE="IyEvYmluL2Jhc2gKCnNldC..."

# Deploy to remote machine
ssh production-server << 'ENDSSH'
  mkdir -p /opt/workflows/my-app
  cd /opt/workflows/my-app
  echo "$WORKFLOW_PARAPHRASE" | base64 -d | bash
  cocoon main.yaml
ENDSSH
```

### Example 3: Workflow Template Distribution

**Create a template repository of paraphrases:**

```bash
# Directory structure
workflow-templates/
├── basic-deployment.txt
├── multi-server-setup.txt
└── data-pipeline.txt

# Each .txt file contains a base64 paraphrase string
# Users can download and execute directly:

curl -sSL https://my-templates.com/basic-deployment.txt | base64 -d | bash
```

---

## ⚙️ How It Works

### Encoding Process

1. **Scan Directory**: `paraphrase.sh` recursively finds all `.yaml` and `.yml` files
2. **Generate Script**: Creates a bash script that:
   - Creates necessary directory structure
   - Uses heredocs to write each YAML file with exact content
   - Preserves file paths and hierarchy
3. **Encode**: Base64 encodes the entire script into a single string
4. **Output**: Displays the paraphrase string and usage instructions

### Decoding Process

1. **Decode**: `echo "string" | base64 -d` decodes the base64 string back to bash script
2. **Execute**: `| bash` pipes the decoded script to bash for execution
3. **Recreate**: The script runs and recreates all directories and YAML files
4. **Result**: Identical workflow structure ready to use

### Technical Details

- **Encoding**: Standard base64 encoding (no line wrapping with `-w 0`)
- **Heredocs**: Uses EOF markers to preserve exact YAML content
- **Safety**: Uses `set -e` to exit on any error during recreation
- **Compatibility**: Works on any Linux system with bash and base64

---

## 🔬 Advanced Usage

### 1. Automated Paraphrase Generation

Create a workflow to automatically generate and store paraphrases:

```bash
#!/bin/bash
# auto-paraphrase.sh

for workflow_dir in workflows/*/; do
    workflow_name=$(basename "$workflow_dir")
    ./paraphrase.sh "$workflow_dir" > "paraphrases/${workflow_name}.txt"
    echo "Generated paraphrase for $workflow_name"
done
```

### 2. Paraphrase with Git Integration

```bash
# Encode current workflow state
./paraphrase.sh > ".paraphrase-$(git rev-parse --short HEAD).txt"

# Track paraphrases in git
git add .paraphrase-*.txt
git commit -m "Add workflow paraphrase snapshot"
```

### 3. Dynamic Workflow Deployment

```bash
#!/bin/bash
# deploy-workflow.sh

ENVIRONMENT=$1
WORKFLOW_PARAPHRASE=$(cat "paraphrases/${ENVIRONMENT}.txt")

ssh "server-${ENVIRONMENT}" << EOF
  cd /opt/applications
  echo "$WORKFLOW_PARAPHRASE" | base64 -d | bash
  cocoon main.yaml
EOF
```

### 4. Paraphrase Validation

```bash
# Validate a paraphrase before deployment
validate_paraphrase() {
    local paraphrase=$1
    
    # Try to decode
    if echo "$paraphrase" | base64 -d > /dev/null 2>&1; then
        echo "✓ Valid base64 encoding"
    else
        echo "✗ Invalid base64 encoding"
        return 1
    fi
    
    # Check if it's a bash script
    if echo "$paraphrase" | base64 -d | head -1 | grep -q "#!/bin/bash"; then
        echo "✓ Valid bash script"
    else
        echo "✗ Not a bash script"
        return 1
    fi
    
    echo "✓ Paraphrase is valid"
}

validate_paraphrase "IyEvYmluL2Jhc2gK..."
```

### 5. Compress Paraphrase Further

For very large workflows, you can combine base64 with gzip:

```bash
# Enhanced paraphrase with compression
enhanced_paraphrase() {
    ./paraphrase.sh "$1" > /tmp/script.sh
    cat /tmp/script.sh | gzip | base64 -w 0
}

# Decode and execute
echo "H4sIAAAAAAAAA..." | base64 -d | gunzip | bash
```

---

## 🛠️ Troubleshooting

### Issue: "No YAML files found"

**Problem:** The directory doesn't contain any `.yaml` or `.yml` files.

**Solution:**
```bash
# Check for YAML files
find . -type f \( -name "*.yaml" -o -name "*.yml" \)

# Ensure you're in the correct directory
cd /path/to/your/workflow
./paraphrase.sh
```

### Issue: "base64: invalid input"

**Problem:** The paraphrase string is corrupted or incomplete.

**Solution:**
```bash
# Ensure the entire string is copied (no line breaks or truncation)
# Verify the string starts with standard base64 characters
echo "YOUR_STRING" | base64 -d > /tmp/test.sh
cat /tmp/test.sh  # Should show a valid bash script
```

### Issue: Permission denied during recreation

**Problem:** The decoded script doesn't have execute permissions.

**Solution:**
```bash
# Save script first, then run
echo "YOUR_PARAPHRASE" | base64 -d > setup.sh
chmod +x setup.sh
./setup.sh
```

### Issue: Files not created in expected location

**Problem:** Script executed in wrong directory.

**Solution:**
```bash
# Create a dedicated directory first
mkdir my-workflow && cd my-workflow
echo "YOUR_PARAPHRASE" | base64 -d | bash
ls -la  # Verify files created
```

### Issue: Special characters in YAML not preserved

**Problem:** Heredoc EOF marker conflicts with file content.

**Solution:** The paraphrase script uses `'EOF'` (quoted) to prevent variable expansion. If issues persist:

```bash
# Manually verify YAML integrity
./paraphrase.sh > paraphrase.txt
echo "$(cat paraphrase.txt)" | base64 -d | bash
diff -r original-workflow recreated-workflow
```

---

## 🔒 Security Considerations

### ⚠️ Important Security Notes

1. **Inspect Before Execution**
  
   ```bash
   # Always review decoded content before executing
   echo "PARAPHRASE" | base64 -d | less
   
   # Then execute if safe
   echo "PARAPHRASE" | base64 -d | bash
   ```

2. **Trusted Sources Only**

   Only decode and execute paraphrases from trusted sources. Malicious scripts can be base64-encoded just as easily.

3. **Sensitive Data**

   Avoid encoding workflows with:
   - API keys or tokens
   - Passwords or credentials
   - Private configuration data
   
   Instead, use environment variables or secrets management:
   
   ```yaml
   # In your YAML, reference environment variables
   blocks:
     - run: 'echo "API_KEY: $API_KEY"'
   ```

4. **Sandboxed Testing**

   Test paraphrases in isolated environments first:
   
   ```bash
   # Use Docker for safe testing
   docker run -it --rm ubuntu:latest bash
   echo "PARAPHRASE" | base64 -d | bash
   ```

5. **Checksum Verification**

   For critical workflows, add checksum verification:
   
   ```bash
   # Generate checksum when encoding
   echo "PARAPHRASE" | sha256sum
   
   # Verify before decoding
   echo "PARAPHRASE" | sha256sum  # Compare with expected hash
   ```

---

## 🤝 Contributing

Found a bug or have a feature request? Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This tool is part of the Cocoon framework. See the main repository for license information.

---

## 🌟 Quick Reference

### Encode Workflow
```bash
./paraphrase.sh /path/to/workflow
```

### Decode and Execute
```bash
echo "BASE64_STRING" | base64 -d | bash
```

### Curl and Execute
```bash
curl -sSL https://url-to-paraphrase.txt | base64 -d | bash
```

### Install Tool
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/paraphrase/paraphrase.sh -o paraphrase.sh && chmod +x paraphrase.sh
```

---

## 📞 Support

- **Repository**: [DebalGhosh100/blocks](https://github.com/DebalGhosh100/blocks)
- **Branch**: `paraphrase`
- **Issues**: [GitHub Issues](https://github.com/DebalGhosh100/blocks/issues)

---

**Happy Paraphrasing! 🎉**

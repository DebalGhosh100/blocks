# Cocoon

A powerful YAML-based workflow automation tool for executing sequential and parallel tasks with configuration management and SSH remote execution capabilities.

> **Repository:** https://github.com/DebalGhosh100/blocks.git

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Writing Workflow YAML Files](#writing-workflow-yaml-files)
- [Configuration Management](#configuration-management)
- [Variable Interpolation](#variable-interpolation)
- [Parallel Execution](#parallel-execution)
- [SSH Remote Execution](#ssh-remote-execution)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Blocks Executor allows you to define complex workflows in simple YAML files. Key features:

- ✅ **Sequential Execution**: Run tasks in order
- ✅ **Parallel Execution**: Run multiple tasks simultaneously
- ✅ **Configuration Management**: Store reusable configs in YAML files
- ✅ **Variable Interpolation**: Reference config values anywhere in your workflow
- ✅ **SSH Remote Execution**: Execute commands on remote machines with real-time log streaming
- ✅ **Detailed Reporting**: Get execution summaries with timing and status

## Installation

### Method 1: One-Command Execution (Recommended)

If you already have `main.yaml` and a `storage/` directory with configuration files in your current directory, use this one-liner to clone, install, execute, and cleanup:

**Linux/Mac:**

First, install Cocoon as an alias (one-time setup):
```bash
echo "alias cocoon='curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash'" >> ~/.bashrc && source ~/.bashrc
```

Then simply run:
```bash
cocoon
```

Or use the full command directly without installing the alias:
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.ps1 | iex
```

**Alternative (if you prefer to see the script first):**

Linux/Mac:
```bash
# Download and inspect the script
curl -O https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh
chmod +x run_blocks.sh
# Review the script, then run it
./run_blocks.sh
```

Windows PowerShell:
```powershell
# Download and inspect the script
Invoke-WebRequest -Uri https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.ps1 -OutFile run_blocks.ps1
# Review the script, then run it
.\run_blocks.ps1
```

**What this does:**
1. Clones the repository into a temporary `.blocks_temp` directory
2. Installs Python dependencies from `requirements.txt`
3. Executes your `main.yaml` workflow using configurations from your `storage/` directory
4. Cleans up by deleting all framework files after execution completes

**Prerequisites:**
- Python 3 installed on your system
- Git installed on your system
- `main.yaml` file in your current directory
- `storage/` directory with configuration YAML files in your current directory

**Your directory structure should be:**
```
your-project/
├── main.yaml           # Your workflow definition
└── storage/            # Your configuration files
    ├── machines.yaml
    ├── servers.yaml
    └── ... (other config files)
```

After running the one-liner, the framework will execute your workflow and then self-destruct, leaving only your original files and any generated logs.

---

### Method 2: Standard Installation (For Development)

If you want to keep the framework installed for repeated use:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DebalGhosh100/blocks.git
   cd blocks
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python3 blocks_executor.py --help
   ```

## Quick Start

### Option A: One-Command Execution (No Installation)

If you want to run the framework without installing it permanently:

1. **Create your workflow and configuration:**

```bash
# Create your project directory
mkdir my-project && cd my-project

# Create storage directory
mkdir storage

# Create a configuration file
cat > storage/machines.yaml << 'EOF'
server1:
  ip: "192.168.1.10"
  username: "admin"
  password: "password123"
EOF

# Create your workflow
cat > main.yaml << 'EOF'
blocks:
  - name: "Test Connection"
    run: "echo 'Testing server at ${machines.server1.ip}'"
EOF
```

2. **(Optional) Install the Cocoon alias for convenience:**

```bash
echo "alias cocoon='curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash'" >> ~/.bashrc && source ~/.bashrc
```

3. **Execute with one command:**

```bash
# If you installed the alias:
cocoon

# Or use the full command directly:
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

The framework will execute your workflow and automatically clean up afterward!

---

### Option B: Standard Quick Start (Persistent Installation)

### 1. Create a storage directory for configurations

```bash
mkdir storage
```

### 2. Create a simple workflow file (`hello.yaml`)

```yaml
blocks:
  - name: "Say Hello"
    description: "Print a greeting"
    run: "echo 'Hello, World!'"

  - name: "List Files"
    description: "Show current directory contents"
    run: "ls -la"
```

Or use the minimal syntax (name and description are optional):

```yaml
blocks:
  - run: "echo 'Hello, World!'"
  - run: "ls -la"
```

### 3. Run the workflow

```bash
python3 blocks_executor.py hello.yaml
```

## Writing Workflow YAML Files

### Basic Structure

Every workflow YAML file must have a `blocks` section containing a list of blocks. Only the `run` field is required:

```yaml
blocks:
  - name: "Block Name"           # Optional
    description: "What this does" # Optional
    run: "command to execute"     # Required
```

Minimal example (name and description omitted):

```yaml
blocks:
  - run: "echo 'Hello, World!'"
  - run: "ls -la"
```

### Block Properties

Each block has three properties:

| Property | Required | Description |
|----------|----------|-------------|
| `name` | No | Human-readable name for the block (defaults to the command if omitted) |
| `description` | No | Detailed description of what the block does |
| `run` | Yes | Shell command(s) to execute |

### Multi-line Commands

Use the pipe `|` operator for multi-line commands:

```yaml
blocks:
  - name: "Multi-step Setup"
    description: "Install and configure software"
    run: |
      sudo apt-get update &&
      sudo apt-get install -y python3-pip &&
      pip3 install numpy pandas
```

### Sequential Execution

By default, blocks execute sequentially (one after another):

```yaml
blocks:
  - name: "Step 1"
    description: "First step"
    run: "echo 'Starting...'"

  - name: "Step 2"
    description: "Second step"
    run: "echo 'Processing...'"

  - name: "Step 3"
    description: "Final step"
    run: "echo 'Complete!'"
```

**Execution Order**: Step 1 → Step 2 → Step 3

## Configuration Management

### Storage Directory

Configuration files are stored in YAML files within the `storage/` directory (or custom directory specified with `--storage` flag).

### Creating Configuration Files

Create YAML files in `storage/` with nested key-value pairs:

**`storage/servers.yaml`:**
```yaml
web_server:
  host: "192.168.1.100"
  port: 8080
  username: "admin"
  password: "secure123"

database:
  host: "192.168.1.101"
  port: 5432
  name: "mydb"
  credentials:
    user: "dbuser"
    password: "dbpass"
```

**`storage/settings.yaml`:**
```yaml
app:
  name: "MyApplication"
  version: "1.0.0"
  debug: false

paths:
  logs: "/var/log/myapp"
  data: "/data/myapp"
```

### Configuration Rules

- ✅ **Nested dictionaries**: Any level of nesting is supported
- ✅ **Multiple files**: Create as many YAML files as needed
- ✅ **Any filename**: Use descriptive names (e.g., `machines.yaml`, `credentials.yaml`)
- ❌ **No lists**: Only key-value pairs (dictionaries) are supported

## Variable Interpolation

### Syntax

Reference configuration values using `${path.to.value}` syntax:

```yaml
${filename.key1.key2.key3}
```

- `filename`: YAML filename in storage directory (without `.yaml` extension)
- `key1.key2.key3`: Nested path to the value

### Examples

Given `storage/servers.yaml`:
```yaml
web:
  ip: "10.0.0.50"
  user: "webadmin"
```

Use in workflow:
```yaml
blocks:
  - name: "Connect to Web Server"
    description: "SSH into web server"
    run: "ssh ${servers.web.user}@${servers.web.ip}"
```

**Result**: `ssh webadmin@10.0.0.50`

### Multiple Variables in One Command

```yaml
blocks:
  - name: "Deploy Application"
    description: "Copy files to server"
    run: "scp app.tar.gz ${servers.web.user}@${servers.web.ip}:${paths.data}/"
```

### Variables in Multi-line Commands

```yaml
blocks:
  - name: "Database Backup"
    description: "Backup database to file"
    run: |
      pg_dump -h ${database.host} \
              -p ${database.port} \
              -U ${database.credentials.user} \
              ${database.name} > backup.sql
```

## Parallel Execution

### Syntax

Use the `parallel:` keyword to execute multiple blocks simultaneously:

```yaml
blocks:
  - name: "Setup Phase"
    description: "Prepare environment"
    run: "echo 'Setting up...'"

  - parallel:
      - name: "Task A"
        description: "First parallel task"
        run: "echo 'Running A' && sleep 5"

      - name: "Task B"
        description: "Second parallel task"
        run: "echo 'Running B' && sleep 5"

      - name: "Task C"
        description: "Third parallel task"
        run: "echo 'Running C' && sleep 5"

  - name: "Cleanup Phase"
    description: "Clean up after parallel tasks"
    run: "echo 'All parallel tasks complete!'"
```

**Execution Timeline:**
1. "Setup Phase" runs first (sequential)
2. Tasks A, B, and C run simultaneously (parallel)
3. Executor waits for ALL parallel tasks to complete
4. "Cleanup Phase" runs after all parallel tasks finish (sequential)

### Real-World Parallel Example

```yaml
blocks:
  - parallel:
      - name: "Download Dataset 1"
        description: "Download large dataset from server 1"
        run: "wget http://server1.com/dataset1.tar.gz -O dataset1.tar.gz"

      - name: "Download Dataset 2"
        description: "Download large dataset from server 2"
        run: "wget http://server2.com/dataset2.tar.gz -O dataset2.tar.gz"

      - name: "Download Dataset 3"
        description: "Download large dataset from server 3"
        run: "wget http://server3.com/dataset3.tar.gz -O dataset3.tar.gz"

  - name: "Process All Datasets"
    description: "Combine and process downloaded datasets"
    run: |
      tar -xzf dataset1.tar.gz &&
      tar -xzf dataset2.tar.gz &&
      tar -xzf dataset3.tar.gz &&
      python3 process_data.py
```

## One-Command Execution Pattern

### Overview

The framework supports a "clone, execute, and evaporate" pattern where you can run workflows without permanently installing the framework. This is ideal for:

- **CI/CD Pipelines**: Execute workflows as part of automated builds
- **Clean Environments**: Avoid cluttering your workspace with framework files
- **Temporary Tasks**: Run one-off automation tasks
- **Production Deployments**: Execute and cleanup in controlled environments

### How It Works

```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

This one-liner downloads and executes a shell script that performs the following steps:

**Step-by-step breakdown:**

1. **Download**: Fetches the execution script from GitHub
2. **Clone**: Downloads framework into `.blocks_temp` directory
3. **Install**: Installs Python dependencies (paramiko, pyyaml)
4. **Execute**: Runs your workflow using your `main.yaml` and `storage/` configs
5. **Cleanup**: Deletes all framework files, leaving only your files and generated outputs

### What Gets Preserved

After execution and cleanup:
- ✅ Your `main.yaml` file
- ✅ Your `storage/` directory with all configurations
- ✅ Generated log files (e.g., `./logs/` directory)
- ✅ Any outputs created by your workflow
- ❌ Framework Python files (deleted)
- ❌ `requirements.txt` (deleted)
- ❌ `README.md` (deleted)
- ❌ `.blocks_temp` directory (deleted)

### Use Cases

**1. Automated Testing:**
```bash
# Create test_workflow.yaml, then run:
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s test_workflow.yaml
```

**2. Deployment Pipeline:**
```bash
# Create deploy.yaml, then run:
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s deploy.yaml
```

**3. Data Collection:**
```bash
# Create collect_logs.yaml, then run:
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s collect_logs.yaml
```

**Note:** The script accepts custom workflow files as arguments. By default, it looks for `main.yaml`.

### Requirements for One-Command Execution

Before running the one-command pattern, ensure:

1. **Python 3** is installed: `python3 --version`
2. **Git** is installed: `git --version`
3. **pip** is available: `pip3 --version`
4. You have a **`main.yaml`** file in your current directory
5. You have a **`storage/`** directory with configuration files

### Customization

You can customize the script execution for different scenarios:

**Use different workflow file:**
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s ../my_workflow.yaml
```

**Use different workflow and storage directory:**
```bash
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash -s ../my_workflow.yaml ../config
```

**Keep framework files (skip cleanup) - Download the script first:**
```bash
# Download the script
curl -O https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh
chmod +x run_blocks.sh

# Edit the script and comment out the cleanup step (line with 'rm -rf')
nano run_blocks.sh

# Run the modified script
./run_blocks.sh
```

---

## SSH Remote Execution

### Remotely Script

The included `remotely.py` script executes commands on remote machines and streams logs to local files in real-time.

### Basic SSH Syntax

```bash
python3 remotely.py <user@host> <password> "<command>" <log-file>
```

### SSH in Workflows

**`storage/machines.yaml`:**
```yaml
server1:
  ip: "192.168.1.10"
  username: "admin"
  password: "admin123"

server2:
  ip: "192.168.1.20"
  username: "root"
  password: "root456"
```

**`workflow.yaml`:**
```yaml
blocks:
  - name: "Check Server 1 Disk Space"
    description: "Monitor disk usage on server 1"
    run: |
      python3 remotely.py \
        ${machines.server1.username}@${machines.server1.ip} \
        ${machines.server1.password} \
        "df -h" \
        ./logs/server1_disk.log

  - parallel:
      - name: "Download on Server 1"
        description: "Download file on remote server 1"
        run: |
          python3 remotely.py \
            ${machines.server1.username}@${machines.server1.ip} \
            ${machines.server1.password} \
            "wget http://example.com/large-file.iso" \
            ./logs/server1_download.log

      - name: "Download on Server 2"
        description: "Download file on remote server 2"
        run: |
          python3 remotely.py \
            ${machines.server2.username}@${machines.server2.ip} \
            ${machines.server2.password} \
            "wget http://example.com/large-file.iso" \
            ./logs/server2_download.log
```

### SSH Log Files

- Logs are saved to the path specified in the 4th argument
- Supports both relative and absolute paths
- Parent directories are created automatically
- Logs include timestamps, command output, and exit status
- Progress bars (like wget) are captured in real-time

## Complete Examples

### Example 1: System Setup Workflow

**`storage/config.yaml`:**
```yaml
packages:
  essential: "git curl wget vim"
  development: "build-essential python3-dev"

user:
  name: "developer"
  home: "/home/developer"
```

**`setup.yaml`:**
```yaml
blocks:
  - name: "Update System"
    description: "Update package lists"
    run: "sudo apt-get update"

  - name: "Install Essential Packages"
    description: "Install required packages"
    run: "sudo apt-get install -y ${config.packages.essential}"

  - name: "Install Development Tools"
    description: "Install development packages"
    run: "sudo apt-get install -y ${config.packages.development}"

  - name: "Create User Directory"
    description: "Setup user workspace"
    run: |
      mkdir -p ${config.user.home}/projects &&
      mkdir -p ${config.user.home}/logs
```

### Example 2: Multi-Server Deployment

**`storage/servers.yaml`:**
```yaml
production:
  web1:
    ip: "10.0.1.10"
    user: "deploy"
    password: "deploy123"
  
  web2:
    ip: "10.0.1.11"
    user: "deploy"
    password: "deploy123"
  
  web3:
    ip: "10.0.1.12"
    user: "deploy"
    password: "deploy123"

app:
  name: "myapp"
  version: "2.1.0"
```

**`deploy.yaml`:**
```yaml
blocks:
  - name: "Build Application"
    description: "Build application locally"
    run: |
      echo "Building ${app.name} version ${app.version}" &&
      npm run build &&
      tar -czf app.tar.gz dist/

  - parallel:
      - name: "Deploy to Web1"
        description: "Deploy application to web server 1"
        run: |
          python3 remotely.py \
            ${servers.production.web1.user}@${servers.production.web1.ip} \
            ${servers.production.web1.password} \
            "cd /var/www && tar -xzf app.tar.gz && systemctl restart nginx" \
            ./logs/deploy_web1.log

      - name: "Deploy to Web2"
        description: "Deploy application to web server 2"
        run: |
          python3 remotely.py \
            ${servers.production.web2.user}@${servers.production.web2.ip} \
            ${servers.production.web2.password} \
            "cd /var/www && tar -xzf app.tar.gz && systemctl restart nginx" \
            ./logs/deploy_web2.log

      - name: "Deploy to Web3"
        description: "Deploy application to web server 3"
        run: |
          python3 remotely.py \
            ${servers.production.web3.user}@${servers.production.web3.ip} \
            ${servers.production.web3.password} \
            "cd /var/www && tar -xzf app.tar.gz && systemctl restart nginx" \
            ./logs/deploy_web3.log

  - name: "Verify Deployment"
    description: "Check if all servers are responding"
    run: |
      curl -f http://${servers.production.web1.ip}/health &&
      curl -f http://${servers.production.web2.ip}/health &&
      curl -f http://${servers.production.web3.ip}/health &&
      echo "All servers healthy!"
```

### Example 3: Data Processing Pipeline

**`storage/pipeline.yaml`:**
```yaml
sources:
  api_endpoint: "https://api.example.com/data"
  backup_server: "backup.example.com"
  credentials:
    api_key: "abc123xyz"

processing:
  threads: 4
  memory: "8G"
  output_dir: "/data/processed"
```

**`pipeline.yaml`:**
```yaml
blocks:
  - name: "Fetch Raw Data"
    description: "Download data from API"
    run: |
      curl -H "Authorization: Bearer ${pipeline.sources.credentials.api_key}" \
           ${pipeline.sources.api_endpoint} \
           -o raw_data.json

  - parallel:
      - name: "Process Chunk 1"
        description: "Process data chunk 1"
        run: "python3 process.py --chunk 1 --threads ${pipeline.processing.threads}"

      - name: "Process Chunk 2"
        description: "Process data chunk 2"
        run: "python3 process.py --chunk 2 --threads ${pipeline.processing.threads}"

      - name: "Process Chunk 3"
        description: "Process data chunk 3"
        run: "python3 process.py --chunk 3 --threads ${pipeline.processing.threads}"

      - name: "Process Chunk 4"
        description: "Process data chunk 4"
        run: "python3 process.py --chunk 4 --threads ${pipeline.processing.threads}"

  - name: "Merge Results"
    description: "Combine processed chunks"
    run: |
      python3 merge.py --output ${pipeline.processing.output_dir}/final.csv &&
      echo "Pipeline complete!"
```

### Example 4: Testing & Validation

**`storage/test_config.yaml`:**
```yaml
test_servers:
  unit_test:
    ip: "192.168.1.50"
    user: "tester"
    password: "test123"
  
  integration_test:
    ip: "192.168.1.51"
    user: "tester"
    password: "test123"
  
  e2e_test:
    ip: "192.168.1.52"
    user: "tester"
    password: "test123"
```

**`test.yaml`:**
```yaml
blocks:
  - name: "Setup Test Environment"
    description: "Prepare testing infrastructure"
    run: |
      mkdir -p ./test_logs &&
      echo "Starting test suite..."

  - parallel:
      - name: "Run Unit Tests"
        description: "Execute unit tests on test server"
        run: |
          python3 remotely.py \
            ${test_config.test_servers.unit_test.user}@${test_config.test_servers.unit_test.ip} \
            ${test_config.test_servers.unit_test.password} \
            "cd /app && pytest tests/unit/" \
            ./test_logs/unit_tests.log

      - name: "Run Integration Tests"
        description: "Execute integration tests"
        run: |
          python3 remotely.py \
            ${test_config.test_servers.integration_test.user}@${test_config.test_servers.integration_test.ip} \
            ${test_config.test_servers.integration_test.password} \
            "cd /app && pytest tests/integration/" \
            ./test_logs/integration_tests.log

      - name: "Run E2E Tests"
        description: "Execute end-to-end tests"
        run: |
          python3 remotely.py \
            ${test_config.test_servers.e2e_test.user}@${test_config.test_servers.e2e_test.ip} \
            ${test_config.test_servers.e2e_test.password} \
            "cd /app && pytest tests/e2e/" \
            ./test_logs/e2e_tests.log

  - name: "Generate Test Report"
    description: "Compile test results"
    run: |
      echo "Test Results Summary:" &&
      grep -h "passed\|failed" ./test_logs/*.log &&
      python3 generate_report.py
```

## Best Practices

### 1. Organize Configuration Files

Group related configurations:
```
storage/
├── servers.yaml          # Server definitions
├── credentials.yaml      # Authentication details
├── paths.yaml           # File system paths
└── settings.yaml        # Application settings
```

### 2. Use Descriptive Names (Recommended)

While `name` is optional, providing descriptive names improves readability:

❌ **Less Clear:**
```yaml
blocks:
  - run: "apt-get install python3"
```

✅ **Better:**
```yaml
blocks:
  - name: "Install Python 3"
    run: "sudo apt-get install -y python3 python3-pip"
```

✅ **Best:**
```yaml
blocks:
  - name: "Install Python 3"
    description: "Install Python 3 interpreter and pip package manager"
    run: "sudo apt-get install -y python3 python3-pip"
```

### 3. Add Error Handling

Use `&&` to chain commands and stop on errors:
```yaml
blocks:
  - name: "Safe Installation"
    description: "Install package with error checking"
    run: |
      sudo apt-get update &&
      sudo apt-get install -y mypackage &&
      mypackage --verify
```

### 4. Create Logs Directory First

```yaml
blocks:
  - name: "Prepare Logging"
    description: "Create logs directory"
    run: "mkdir -p ./logs"

  - parallel:
      # ... blocks that write to ./logs/
```

### 5. Use Comments in YAML

```yaml
blocks:
  # Phase 1: Environment Setup
  - name: "Update System"
    run: "sudo apt-get update"

  # Phase 2: Parallel Processing
  - parallel:
      - name: "Task A"
        run: "process_a.sh"
      - name: "Task B"
        run: "process_b.sh"
```

### 6. Keep Commands Testable

Test commands individually before adding to workflow:
```bash
# Test the command first
python3 remotely.py user@host pass "ls -la" ./test.log

# Then add to workflow once verified
```

### 7. Use Relative Paths for Portability

✅ **Good:**
```yaml
run: "python3 remotely.py ... ./logs/output.log"
```

❌ **Avoid:**
```yaml
run: "python3 remotely.py ... /home/myuser/logs/output.log"
```

## Troubleshooting

### Issue: Variable not interpolated

**Problem:** Command shows `${config.value}` instead of actual value

**Solution:** 
- Check that YAML file exists in `storage/` directory
- Verify the path is correct: `filename.key1.key2`
- Ensure the YAML file has valid structure (no lists)

### Issue: Parallel blocks run sequentially

**Problem:** Blocks under `parallel:` execute one at a time

**Solution:**
- Check YAML indentation (use spaces, not tabs)
- Ensure `parallel:` keyword is followed by a list with `-` for each block

**Correct:**
```yaml
- parallel:
    - name: "Task 1"
      run: "..."
    - name: "Task 2"
      run: "..."
```

### Issue: SSH connection fails

**Problem:** `remotely.py` can't connect to remote host

**Solution:**
- Verify IP address and credentials in configuration
- Test SSH connection manually: `ssh user@host`
- Check network connectivity: `ping host`
- Ensure SSH service is running on remote machine

### Issue: Command not found

**Problem:** Shell reports command doesn't exist

**Solution:**
- Use full paths: `/usr/bin/python3` instead of `python3`
- Check if command is installed: `which command_name`
- Ensure PATH is set correctly in workflow

### Issue: Permission denied

**Problem:** Commands fail with permission errors

**Solution:**
- Add `sudo` for privileged operations
- Ensure user has necessary permissions
- For SSH: Check remote user's sudo privileges

### Issue: Workflow stops unexpectedly

**Problem:** Execution halts without completing all blocks

**Solution:**
- Check exit status of failed command
- Look at execution summary for failed blocks
- Add error handling with `|| true` to continue on errors:
  ```yaml
  run: "some_command || true"
  ```

## Advanced Tips

### Environment Variables

Access system environment variables:
```yaml
blocks:
  - name: "Use Environment Variable"
    run: "echo Current user: $USER"
```

### Conditional Execution

Use shell conditionals:
```yaml
blocks:
  - name: "Conditional Task"
    run: |
      if [ -f /tmp/data.txt ]; then
        echo "File exists, processing..."
        process_data.sh
      else
        echo "File not found, skipping..."
      fi
```

### Timeout Handling

Add timeouts to commands:
```yaml
blocks:
  - name: "Task with Timeout"
    run: "timeout 300 long_running_command.sh"
```

### Background Processes

Run tasks in background:
```yaml
blocks:
  - name: "Start Background Service"
    run: "nohup service.sh > service.log 2>&1 &"
```

## Getting Help

Run the executor with `--help` flag:
```bash
python3 blocks_executor.py --help
```

View remotely script help:
```bash
python3 remotely.py --help
```

---

## Quick Reference Card

### Workflow Structure
```yaml
blocks:
  - name: "Sequential Block"
    description: "Runs in order"
    run: "command"

  - parallel:
      - name: "Parallel Block 1"
        run: "command1"
      - name: "Parallel Block 2"
        run: "command2"
```

### Variable Syntax
```yaml
${filename.key1.key2.key3}
```

### SSH Remote Execution
```bash
python3 remotely.py user@host password "command" log-file
```

### Run Workflow
```bash
python3 blocks_executor.py workflow.yaml
```

---

**Happy Automating! 🚀**

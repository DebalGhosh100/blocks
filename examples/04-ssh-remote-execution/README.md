# Example 4: SSH Remote Execution with Parallel Deployment

## Overview
This example demonstrates how to use the `remotely.py` script to execute commands on **multiple remote servers in parallel** via SSH and stream the output to local log files in real-time.

## What This Example Demonstrates
- ✅ SSH remote command execution using `remotely.py`
- ✅ **Parallel execution across multiple servers simultaneously**
- ✅ Real-time log streaming to local files
- ✅ Variable interpolation for SSH credentials
- ✅ Multi-server system updates and package installation
- ✅ Log file management and display

## Prerequisites
- Python 3.x installed
- Blocks framework installed (including `remotely.py`)
- SSH access to a remote server
- `paramiko` Python library installed (`pip install paramiko`)

## Directory Structure
```
04-ssh-remote-execution/
├── main.yaml           # Workflow with SSH remote executions
├── storage/            # Configuration files
│   └── machines.yaml   # SSH server credentials
├── logs/               # Created during execution (stores SSH logs)
└── README.md           # This file
```

## How to Run

### Step 1: Configure Your SSH Servers

Edit `storage/machines.yaml` and replace with your actual server details:

```yaml
server1:
  ip: "YOUR_SERVER1_IP"          # e.g., "192.168.1.100"
  username: "YOUR_USERNAME"       # e.g., "admin"
  password: "YOUR_PASSWORD"       # e.g., "admin123"
  description: "Primary application server"

server2:
  ip: "YOUR_SERVER2_IP"          # e.g., "192.168.1.101"
  username: "YOUR_USERNAME"       # e.g., "deploy"
  password: "YOUR_PASSWORD"       # e.g., "deploy456"
  description: "Secondary application server"

server3:
  ip: "YOUR_SERVER3_IP"          # e.g., "192.168.1.102"
  username: "YOUR_USERNAME"       # e.g., "sysadmin"
  password: "YOUR_PASSWORD"       # e.g., "sysadmin789"
  description: "Tertiary application server"
```

⚠️ **Security Note**: For production use, consider using SSH keys instead of passwords.

### Step 2: Run the Workflow

```bash
# Clone this specific example and navigate to it
git clone --depth 1 --filter=blob:none --sparse https://github.com/DebalGhosh100/blocks.git && cd blocks && git sparse-checkout set examples/04-ssh-remote-execution && cd examples/04-ssh-remote-execution

# Edit storage/machines.yaml with your server details
# Then run with one-command execution
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

**What this does:**
1. Clones only this example directory (sparse checkout)
2. Downloads the Blocks framework automatically
3. Installs dependencies (paramiko, pyyaml)
4. Executes the workflow with your SSH servers
5. Cleans up framework files after completion

## Expected Output
The workflow will:
1. Create `./logs/` directory for storing SSH execution logs
2. **Parallel Execution**: Execute complete setup on all 3 servers simultaneously
   - Each server runs: update → upgrade → install tools → list files → system info
   - Streams to `./logs/server1_execution.log`, `./logs/server2_execution.log`, `./logs/server3_execution.log`
3. Display all collected logs from all servers
4. Show summary of execution (3 total log files created)

## Remotely Script Syntax

### Basic Usage
```bash
python3 remotely.py <ssh_url> <password> "<command>" <log_file>
```

### Parameters
- `ssh_url`: SSH connection string (formats: `user@host`, `ssh://user@host:port`, or `host`)
- `password`: SSH password for authentication
- `command`: Linux command to execute on remote server (wrap in quotes)
- `log_file`: Local file path where logs will be streamed (relative or absolute)

### Examples

**Simple command:**
```bash
python3 remotely.py admin@192.168.1.100 mypass "ls -la" ./logs/output.log
```

**Complex command with pipes:**
```bash
python3 remotely.py admin@192.168.1.100 mypass "df -h && free -m" ./logs/system.log
```

**Custom SSH port:**
```bash
python3 remotely.py ssh://admin@192.168.1.100:2222 mypass "uptime" ./logs/uptime.log
```

## Workflow Breakdown

### Block 1: Prepare Logs Directory
```yaml
- name: "Prepare Logs Directory"
  description: "Create directory for SSH execution logs"
  run: "mkdir -p ./logs && echo 'Logs directory ready'"
```
Creates the logs directory if it doesn't exist.

### Block 2: Parallel Complete Setup (All 3 Servers)
```yaml
- parallel:
    - name: "Server 1 - Complete Setup"
      description: "Update, install tools, and gather info from server 1"
      run: python3 remotely.py ${machines.server1.username}@${machines.server1.ip} ${machines.server1.password} "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y neovim nstools tree && ls -lah ~ && uname -a && df -h && free -h" ./logs/server1_execution.log
    
    - name: "Server 2 - Complete Setup"
      description: "Update, install tools, and gather info from server 2"
      run: python3 remotely.py ${machines.server2.username}@${machines.server2.ip} ${machines.server2.password} "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y neovim nstools tree && ls -lah ~ && uname -a && df -h && free -h" ./logs/server2_execution.log
    
    - name: "Server 3 - Complete Setup"
      description: "Update, install tools, and gather info from server 3"
      run: python3 remotely.py ${machines.server3.username}@${machines.server3.ip} ${machines.server3.password} "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y neovim nstools tree && ls -lah ~ && uname -a && df -h && free -h" ./logs/server3_execution.log
```

**What happens:**
- All 3 servers execute their complete setup simultaneously (parallel execution)
- Each server runs a chain of commands:
  1. `sudo apt-get update` - Update package lists
  2. `sudo apt-get upgrade -y` - Upgrade installed packages
  3. `sudo apt-get install -y neovim nstools tree` - Install tools
  4. `ls -lah ~` - List home directory contents
  5. `uname -a && df -h && free -h` - Gather system information
- Output streams in real-time to separate log files (one per server)
- The workflow waits for ALL servers to complete before proceeding
- Commands are chained with `&&` so execution stops if any command fails

### Block 3: Display Log Results
```yaml
- name: "Display Log Results"
  description: "Show the logs collected from remote execution"
  run: |
    echo "=== Remote Command Logs ==="
    echo "--- Server 1 Execution Log ---"
    cat ./logs/server1_execution.log
    echo "--- Server 2 Execution Log ---"
    cat ./logs/server2_execution.log
    echo "--- Server 3 Execution Log ---"
    cat ./logs/server3_execution.log
```
Displays all collected logs from all servers sequentially.

### Block 4: Summary
```yaml
- name: "Summary"
  run: |
    echo "=== Execution Summary ==="
    echo "Total servers configured: 3"
    echo "Total log files created: $(ls -1 ./logs/*.log | wc -l)"
    ls -lh ./logs/*.log
```
Shows execution summary with file counts and sizes.

## Log File Format

Each log file generated by `remotely.py` includes:

```
=== SSH Log Stream Started ===
Timestamp: 2024-11-09T10:30:45.123456
Host: admin@192.168.1.100
Command: ls -lah ~
==================================================

[Command output appears here in real-time]

==================================================
Command completed with exit status: 0
Timestamp: 2024-11-09T10:30:47.654321
=== SSH Log Stream Ended ===
```

## Real-Time Log Streaming

The `remotely.py` script streams output **in real-time**, which means:

✅ **Progress bars** are captured (e.g., `wget`, `dd`, `rsync`)
✅ **Long-running commands** show output as they execute
✅ **Immediate feedback** - no waiting for command completion
✅ **Binary-safe** - handles all output types correctly

Example with progress bar:
```yaml
- run: |
    python3 remotely.py user@host pass \
      "wget http://example.com/large-file.iso" \
      ./logs/download.log
```

The log file will capture the wget progress bar updates!

## Parallel Execution Benefits

This example demonstrates the power of parallel SSH execution:

**Sequential Execution Time:**
- Server 1 complete setup: 5 minutes
- Server 2 complete setup: 5 minutes  
- Server 3 complete setup: 5 minutes
- **Total: 15 minutes**

**Parallel Execution Time:**
- All 3 servers execute simultaneously: **5 minutes**
- **Time saved: 10 minutes (67% faster!)**

With more servers, the time savings multiply! The key advantage is that all servers execute their full command chain in parallel, with real-time log streaming for each.

## Variable Interpolation with SSH

Combine variable interpolation with SSH for powerful workflows:

**storage/machines.yaml:**
```yaml
server1:
  ip: "10.0.1.10"
  username: "deploy"
  password: "deploy123"
  description: "Web server 1"

server2:
  ip: "10.0.1.11"
  username: "deploy"
  password: "deploy123"
  description: "Web server 2"
```

**Workflow:**
```yaml
blocks:
  - parallel:
      - run: python3 remotely.py ${machines.server1.username}@${machines.server1.ip} ${machines.server1.password} "systemctl status nginx" ./logs/web1_nginx.log
      - run: python3 remotely.py ${machines.server2.username}@${machines.server2.ip} ${machines.server2.password} "systemctl status nginx" ./logs/web2_nginx.log
```

## Use Cases

### 1. Health Checks
```yaml
- run: |
    python3 remotely.py ${machines.server.username}@${machines.server.ip} \
      ${machines.server.password} \
      "systemctl status app && curl -f http://localhost:8080/health" \
      ./logs/health_check.log
```

### 2. Log Collection
```yaml
- run: |
    python3 remotely.py ${machines.server.username}@${machines.server.ip} \
      ${machines.server.password} \
      "tail -n 100 /var/log/app/error.log" \
      ./logs/app_errors.log
```

### 3. File Downloads (with progress)
```yaml
- run: |
    python3 remotely.py ${machines.server.username}@${machines.server.ip} \
      ${machines.server.password} \
      "wget http://updates.example.com/package.tar.gz" \
      ./logs/download.log
```

### 4. Database Backups
```yaml
- run: |
    python3 remotely.py ${machines.db.username}@${machines.db.ip} \
      ${machines.db.password} \
      "pg_dump mydb > /backups/mydb_$(date +%Y%m%d).sql" \
      ./logs/backup.log
```

## Troubleshooting

### Issue: Connection Refused
**Problem:** Cannot connect to SSH server

**Solutions:**
- Verify IP address is correct
- Check that SSH service is running: `sudo systemctl status sshd`
- Verify network connectivity: `ping <server-ip>`
- Check firewall rules allow port 22

### Issue: Authentication Failed
**Problem:** Password authentication fails

**Solutions:**
- Double-check username and password in `machines.yaml`
- Verify the user account exists on remote server
- Check that password authentication is enabled in `/etc/ssh/sshd_config`

### Issue: Command Not Found
**Problem:** Remote command fails with "command not found"

**Solutions:**
- Use full paths: `/usr/bin/command` instead of `command`
- Check that the command is installed on the remote server
- Verify PATH is set correctly for the remote user

### Issue: Permission Denied
**Problem:** Command fails due to insufficient permissions

**Solutions:**
- Use `sudo` for privileged commands: `"sudo systemctl restart nginx"`
- Ensure remote user has necessary permissions
- Check file/directory permissions on remote server

## Security Considerations

⚠️ **Warning**: This example stores passwords in plain text for simplicity.

**For production use:**
1. **Use SSH Keys** instead of passwords
2. **Environment Variables** for sensitive data
3. **Secret Management Tools** (HashiCorp Vault, AWS Secrets Manager)
4. **Encrypted Configuration Files**
5. **Principle of Least Privilege** - use accounts with minimal permissions

## Key Takeaways
- `remotely.py` enables SSH command execution from workflows
- **Parallel execution drastically reduces multi-server deployment time**
- Output is streamed in real-time to local log files for each server
- Progress bars and long-running commands are fully supported
- Combine with variable interpolation for flexible configurations
- Log files include metadata and execution status
- Scale from 1 to N servers without changing workflow structure

## Next Steps
- Configure your actual SSH servers in `machines.yaml`
- Try executing different commands on your servers
- Explore the next example: **05-multi-server-deployment**

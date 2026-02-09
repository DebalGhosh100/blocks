# Example 4: SSH Remote Execution with Parallel Deployment

## Overview
This example demonstrates how to use the **`run-remotely` YAML syntax** to execute commands on **multiple remote servers in parallel** via SSH and stream the output to local log files in real-time.

## What This Example Demonstrates
- ✅ **New `run-remotely` YAML syntax** for structured remote execution
- ✅ SSH remote command execution with structured configuration
- ✅ **Parallel execution across multiple servers simultaneously**
- ✅ Real-time log streaming to local files
- ✅ Streaming mode without log files (optional)
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
├── parameters/            # Configuration files
│   └── machines.yaml   # SSH server credentials
├── logs/               # Created during execution (stores SSH logs)
└── README.md           # This file
```

## How to Run

### Step 1: Configure Your SSH Servers

Edit `parameters/machines.yaml` and replace with your actual server details:

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

# Edit parameters/machines.yaml with your server details
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

## Remote Execution Syntax

### New `run-remotely` YAML Syntax

The framework now supports a dedicated YAML syntax for remote execution that's cleaner and more maintainable than calling `remotely.py` directly:

```yaml
- run-remotely:
    ip: "192.168.1.100"                    # Server IP address
    user: "admin"                           # SSH username
    pass: "mypassword"                      # SSH password (optional, uses key-based auth if omitted)
    run: "ls -la && df -h"                  # Command(s) to execute
    log-into: "./logs/output.log"           # Log file (optional for sequential, mandatory for parallel)
                                             # Stream in real-time: tail -f ./logs/output.log
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ip` | string | ✅ Yes | IP address or hostname of the remote server |
| `user` | string | ✅ Yes | SSH username for authentication |
| `pass` | string | ⚠️ Optional | SSH password for authentication. If omitted, uses key-based authentication (SSH keys) |
| `run` | string | ✅ Yes | Linux command(s) to execute (can chain with `&&` or `;`) |
| `log-into` | string | ⚠️ Conditional | Log file path. **Optional** for sequential execution, **mandatory** for parallel execution |

### Execution Modes

#### 1. Sequential with Log File
```yaml
- name: "Check System Info"
  description: "Get system information and save to log"
  run-remotely:
    ip: ${machines.server1.ip}
    user: ${machines.server1.username}
    pass: ${machines.server1.password}
    run: "uname -a && df -h"
    log-into: ./logs/server1_sysinfo.log  # Stream: tail -f ./logs/server1_sysinfo.log
```
- Executes command and saves output to specified log file
- Streams output in real-time to the file
- Use when you need to preserve command output
- **Monitor live:** `tail -f ./logs/server1_sysinfo.log`

#### 2. Sequential with Streaming (No Log File)
```yaml
- name: "Quick Health Check"
  description: "Stream output directly to console"
  run-remotely:
    ip: ${machines.server1.ip}
    user: ${machines.server1.username}
    pass: ${machines.server1.password}
    run: "systemctl status nginx"
    # log-into is optional - output streams to console
```
- Executes command and displays output in real-time
- No log file is created
- Use for quick checks or when logs aren't needed

#### 3. Key-Based Authentication (No Password)
```yaml
- name: "Deploy with SSH Keys"
  description: "Use SSH key-based authentication"
  run-remotely:
    ip: ${machines.server1.ip}
    user: ${machines.server1.username}
    # pass field omitted - uses SSH keys from ~/.ssh/
    run: "git pull && npm install && pm2 restart app"
    log-into: ./logs/deploy.log
```
- Omit the `pass` field to use SSH key-based authentication
- Requires SSH keys to be set up on the remote server
- More secure than password authentication
- Ideal for production deployments

#### 4. Parallel Execution (Log Files Mandatory)
```yaml
- parallel:
    - name: "Server 1 Setup"
      run-remotely:
        ip: ${machines.server1.ip}
        user: ${machines.server1.username}
        pass: ${machines.server1.password}
        run: "apt-get update && apt-get upgrade -y"
        log-into: ./logs/server1_setup.log  # REQUIRED for parallel
    
    - name: "Server 2 Setup"
      run-remotely:
        ip: ${machines.server2.ip}
        user: ${machines.server2.username}
        pass: ${machines.server2.password}
        run: "apt-get update && apt-get upgrade -y"
        log-into: ./logs/server2_setup.log  # REQUIRED for parallel
```
- **`log-into` field is mandatory** when executing multiple remote commands in parallel
- Prevents output from different servers from mixing together
- Each server's output is isolated in its own log file
- Framework validates this requirement and returns an error if missing

### Best Practice

Always use the `run-remotely` syntax for SSH commands:

✅ **Recommended:**
```yaml
- run-remotely:
    ip: <host>
    user: <username>
    pass: <password>
    run: <command>
    log-into: ./log.txt
```

This provides better readability, validation, and maintainability.

## Workflow Breakdown

### Block 1: Prepare Logs Directory
```yaml
- name: "Prepare Logs Directory"
  description: "Create directory for SSH execution logs"
  run: "mkdir -p ./logs && echo 'Logs directory ready'"
```
Creates the logs directory if it doesn't exist.

### Block 2: Sequential Remote Execution with Log File
```yaml
- name: "Server 1 - System Information"
  description: "Gather system info and save to log file"
  run-remotely:
    ip: ${machines.server1.ip}
    user: ${machines.server1.username}
    pass: ${machines.server1.password}
    run: "uname -a && df -h"
    log-into: ./logs/server1_sysinfo.log  # Stream: tail -f ./logs/server1_sysinfo.log
```
- Uses new `run-remotely` syntax for cleaner configuration
- Saves output to `./logs/server1_sysinfo.log`
- Variables are interpolated from `parameters/machines.yaml`
- **Monitor live:** `tail -f ./logs/server1_sysinfo.log`

### Block 3: Sequential Remote Execution with Streaming
```yaml
- name: "Server 1 - Quick Check (Streaming)"
  description: "Stream output directly without saving to log"
  run-remotely:
    ip: ${machines.server1.ip}
    user: ${machines.server1.username}
    pass: ${machines.server1.password}
    run: "ps aux | head -10"
    # No log-into field - output streams to console
```
- Output is streamed directly to console in real-time
- No log file is created
- Useful for quick checks where logs aren't needed

### Block 4: Parallel Complete Setup (All 3 Servers)
```yaml
# Monitor all servers in real-time: tail -f ./logs/server*_execution.log
- parallel:
    - name: "Server 1 - Complete Setup"
      description: "Update, install tools, and gather info"
      run-remotely:
        ip: ${machines.server1.ip}
        user: ${machines.server1.username}
        pass: ${machines.server1.password}
        run: "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y neovim net-tools tree && ls -lah ~ && uname -a && df -h && free -h"
        log-into: ./logs/server1_execution.log
    
    - name: "Server 2 - Complete Setup"
      description: "Update, install tools, and gather info"
      run-remotely:
        ip: ${machines.server2.ip}
        user: ${machines.server2.username}
        pass: ${machines.server2.password}
        run: "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y neovim net-tools tree && ls -lah ~ && uname -a && df -h && free -h"
        log-into: ./logs/server2_execution.log
    
    - name: "Server 3 - Complete Setup"
      description: "Update, install tools, and gather info"
      run-remotely:
        ip: ${machines.server3.ip}
        user: ${machines.server3.username}
        pass: ${machines.server3.password}
        run: "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y neovim net-tools tree && ls -lah ~ && uname -a && df -h && free -h"
        log-into: ./logs/server3_execution.log
```

**What happens:**
- All 3 servers execute their complete setup simultaneously (parallel execution)
- Uses new `run-remotely` syntax for better readability
- **`log-into` field is mandatory** for parallel execution to prevent output mixing
- Each server runs a chain of commands:
  1. `sudo apt-get update` - Update package lists
  2. `sudo apt-get upgrade -y` - Upgrade installed packages
  3. `sudo apt-get install -y neovim net-tools tree` - Install tools
  4. `ls -lah ~` - List home directory contents
  5. `uname -a && df -h && free -h` - Gather system information
- **Sudo authentication is handled automatically** using the password from `machines.yaml`
- Output streams in real-time to separate log files (one per server)
- The workflow waits for ALL servers to complete before proceeding
- Commands are chained with `&&` so execution stops if any command fails

### Block 5: Display Log Results
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

### Block 6: Summary
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

Remote execution streams output **in real-time**, which means:

✅ **Progress bars** are captured (e.g., `wget`, `dd`, `rsync`)
✅ **Long-running commands** show output as they execute
✅ **Immediate feedback** - no waiting for command completion
✅ **Binary-safe** - handles all output types correctly

Example with progress bar:
```yaml
- run-remotely:
    ip: ${server.ip}
    user: ${server.user}
    pass: ${server.pass}
    run: wget http://example.com/large-file.iso
    log-into: ./logs/download.log  # Watch: tail -f ./logs/download.log
```

The log file will capture the wget progress bar updates!

**Monitor download progress live:**
```bash
tail -f ./logs/download.log
```

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

With more servers or longer-running commands, the time savings multiply! The key advantage is that all servers execute their full command chain in parallel, with real-time log streaming for each.

## Automatic Sudo Password Handling

The framework **automatically handles sudo password authentication** for you:

- ✅ No need to configure passwordless sudo on remote servers
- ✅ Password from `machines.yaml` is automatically injected for sudo commands
- ✅ Uses secure `echo 'password' | sudo -S command` pattern
- ✅ Works with any command containing `sudo`
- ✅ No manual intervention required

Simply include `sudo` in your commands and the framework handles the rest!

## Variable Interpolation with SSH

Combine variable interpolation with SSH for powerful workflows using the `run-remotely` syntax:

**parameters/machines.yaml:**
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
      - run-remotely:
          ip: ${machines.server1.ip}
          user: ${machines.server1.username}
          pass: ${machines.server1.password}
          run: "systemctl status nginx"
          log-into: ./logs/web1_nginx.log
      
      - run-remotely:
          ip: ${machines.server2.ip}
          user: ${machines.server2.username}
          pass: ${machines.server2.password}
          run: "systemctl status nginx"
          log-into: ./logs/web2_nginx.log
```

## Use Cases

### 1. Health Checks
```yaml
- name: "Application Health Check"
  run-remotely:
    ip: ${machines.server.ip}
    user: ${machines.server.username}
    pass: ${machines.server.password}
    run: "systemctl status app && curl -f http://localhost:8080/health"
    log-into: ./logs/health_check.log
```

### 2. Log Collection
```yaml
- name: "Collect Application Errors"
  run-remotely:
    ip: ${machines.server.ip}
    user: ${machines.server.username}
    pass: ${machines.server.password}
    run: "tail -n 100 /var/log/app/error.log"
    log-into: ./logs/app_errors.log
```

### 3. File Downloads (with progress)
```yaml
- name: "Download Updates"
  run-remotely:
    ip: ${machines.server.ip}
    user: ${machines.server.username}
    pass: ${machines.server.password}
    run: "wget http://updates.example.com/package.tar.gz"
    log-into: ./logs/download.log
```

### 4. Database Backups
```yaml
- name: "Backup Database"
  run-remotely:
    ip: ${machines.db.ip}
    user: ${machines.db.username}
    pass: ${machines.db.password}
    run: "pg_dump mydb > /backups/mydb_$(date +%Y%m%d).sql"
    log-into: ./logs/backup.log
```

### 5. Quick Status Check (No Log File)
```yaml
- name: "Quick Server Status"
  run-remotely:
    ip: ${machines.server.ip}
    user: ${machines.server.username}
    pass: ${machines.server.password}
    run: "uptime && free -h && df -h"
    # No log-into - streams to console
```

## Troubleshooting

### Issue: Sudo Commands Fail
**Problem:** Commands with `sudo` fail with "permission denied" or authentication errors

**Solution:** The framework automatically handles sudo password authentication using the password from `machines.yaml`. Ensure:
1. The password in `machines.yaml` is correct
2. The user has sudo privileges on the remote server
3. The remote server allows password-based sudo (default configuration)

**How it works:** When the framework detects `sudo` in a command, it automatically wraps it with password injection: `echo 'password' | sudo -S command`

### Issue: Connection Refused
**Problem:** Cannot connect to SSH server

**Solutions:**
- Verify IP address is correct
- Check that SSH service is running: `systemctl status sshd`
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
- Ensure remote user has necessary permissions
- Check file/directory permissions on remote server
- Configure passwordless sudo (see "Command Hangs" section above)

## Security Considerations

⚠️ **Warning**: This example stores passwords in plain text for simplicity.

**For production use:**
1. **Use SSH Keys** instead of passwords
2. **Environment Variables** for sensitive data
3. **Secret Management Tools** (HashiCorp Vault, AWS Secrets Manager)
4. **Encrypted Configuration Files**
5. **Principle of Least Privilege** - use accounts with minimal permissions

## Key Takeaways
- **New `run-remotely` YAML syntax** provides cleaner, more structured remote execution
- Structured fields: `ip`, `user`, `pass`, `run`, `log-into` (optional/conditional)
- **Two execution modes**: with log file or streaming to console
- **`log-into` is mandatory** for parallel execution to prevent output mixing
- **`log-into` is optional** for sequential execution (use streaming when logs aren't needed)
- **Parallel execution drastically reduces multi-server deployment time**
- **Sudo commands work automatically** - no configuration needed on remote servers
- Output is streamed in real-time to local log files or console
- Progress bars and long-running commands are fully supported
- Combine with variable interpolation for flexible configurations
- Log files include metadata and execution status
- Scale from 1 to N servers without changing workflow structure
- Password from `machines.yaml` is securely used for sudo authentication
- Old `remotely.py` direct syntax still supported for backward compatibility

## Next Steps
- Configure your actual SSH servers in `machines.yaml`
- Try executing different commands on your servers
- Explore the next example: **05-loop-iteration**

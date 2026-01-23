# Example 5: Multi-Server Parallel Deployment

## Overview
This example demonstrates a real-world scenario: deploying an application to multiple web servers in parallel, followed by parallel health checks. This pattern is commonly used in production environments for zero-downtime deployments.

## What This Example Demonstrates
- ✅ Parallel SSH deployments to multiple servers simultaneously
- ✅ Variable interpolation for server configurations
- ✅ Real-time deployment log streaming
- ✅ Post-deployment verification with parallel health checks
- ✅ Comprehensive reporting and log aggregation
- ✅ Complex multi-stage workflows (build → deploy → verify)

## Prerequisites
- Python 3.x installed
- Blocks framework installed
- SSH access to 3 target servers
- `paramiko` Python library installed (included in requirements.txt)

## Directory Structure
```
06-multi-server-deployment/
├── main.yaml           # Multi-stage deployment workflow
├── storage/            # Configuration files
│   └── config.yaml     # Server and application configuration
├── logs/               # Created during execution
└── README.md           # This file
```

## How to Run

### Step 1: Configure Your Servers

Edit `storage/config.yaml` with your actual server details:

```yaml
servers:
  web1:
    ip: "YOUR_WEB1_IP"
    username: "YOUR_USERNAME"
    password: "YOUR_PASSWORD"
  
  web2:
    ip: "YOUR_WEB2_IP"
    username: "YOUR_USERNAME"
    password: "YOUR_PASSWORD"
  
  web3:
    ip: "YOUR_WEB3_IP"
    username: "YOUR_USERNAME"
    password: "YOUR_PASSWORD"

app:
  name: "MyWebApp"
  version: "3.2.1"
  environment: "production"
  deploy_path: "/var/www/myapp"
  health_port: 8080
```

### Step 2: Run the Deployment

```bash
# Clone this specific example and navigate to it
git clone --depth 1 --filter=blob:none --sparse https://github.com/DebalGhosh100/blocks.git && cd blocks && git sparse-checkout set examples/06-multi-server-deployment && cd examples/06-multi-server-deployment

# Edit storage/config.yaml with your server details
# Then run with one-command execution
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

**What this does:**
1. Clones only this example directory (sparse checkout)
2. Downloads the Blocks framework automatically
3. Installs dependencies (paramiko, pyyaml)
4. Executes parallel deployment to all servers
5. Cleans up framework files after completion

## Expected Output

The workflow executes in these stages:

### Stage 1: Preparation
- Creates logs directory
- Builds application package locally

### Stage 2: Parallel Deployment (saves time!)
- Deploys to **all 3 servers simultaneously**
- Each deployment streams logs independently
- All deployments complete in parallel (not sequential)

**Time saved**: If each deployment takes 30 seconds:
- Sequential: 90 seconds (30 + 30 + 30)
- Parallel: ~30 seconds (all at once!)

### Stage 3: Verification
- Displays all deployment logs
- Confirms successful deployment on each server

### Stage 4: Parallel Health Checks
- Runs health checks on **all 3 servers simultaneously**
- Verifies services are running
- Checks health endpoints

### Stage 5: Summary
- Aggregates health check results
- Displays final deployment status

## Workflow Breakdown

### Phase 1: Build Application Package (Sequential)
```yaml
- name: "Build Application Package"
  run: |
    echo "Building application package..."
    mkdir -p ./deploy_package
    echo "Application Version: ${config.app.version}" > ./deploy_package/version.txt
```

Creates a local deployment package with version information.

### Phase 2: Deploy to All Servers (Parallel)
```yaml
# Monitor deployment: tail -f ./logs/deploy_*.log
- parallel:
    - name: "Deploy to Web Server 1"
      run-remotely:
        ip: ${config.servers.web1.ip}
        user: ${config.servers.web1.username}
        pass: ${config.servers.web1.password}
        run: mkdir -p ${config.app.deploy_path} && ...
        log-into: ./logs/deploy_web1.log
    
    - name: "Deploy to Web Server 2"
      run-remotely:
        ip: ${config.servers.web2.ip}
        user: ${config.servers.web2.username}
        pass: ${config.servers.web2.password}
        run: mkdir -p ${config.app.deploy_path} && ...
        log-into: ./logs/deploy_web2.log
    
    - name: "Deploy to Web Server 3"
      run-remotely:
        ip: ${config.servers.web3.ip}
        user: ${config.servers.web3.username}
        pass: ${config.servers.web3.password}
        run: mkdir -p ${config.app.deploy_path} && ...
        log-into: ./logs/deploy_web3.log
```

**Key Points:**
- All 3 deployments start at the same time
- Each deployment runs in its own thread
- The workflow waits for ALL deployments to complete before continuing
- Each deployment logs to a separate file

### Phase 3: Verify Deployments (Sequential)
```yaml
- name: "Verify Deployments"
  run: |
    echo "--- Web Server 1 Deployment Log ---"
    cat ./logs/deploy_web1.log
    echo "--- Web Server 2 Deployment Log ---"
    cat ./logs/deploy_web2.log
    echo "--- Web Server 3 Deployment Log ---"
    cat ./logs/deploy_web3.log
```

Displays all deployment logs to verify success.

### Phase 4: Health Checks (Parallel)
```yaml
# Monitor health checks: tail -f ./logs/health_*.log
- parallel:
    - name: "Health Check - Web Server 1"
      run-remotely:
        ip: ${config.servers.web1.ip}
        user: ${config.servers.web1.username}
        pass: ${config.servers.web1.password}
        run: ps aux | grep nginx && curl -f http://localhost:${config.app.health_port}/health
        log-into: ./logs/health_web1.log
    
    # Similar blocks for web2 and web3...
```

Runs health checks on all servers simultaneously to verify the deployment.

## Execution Timeline

```
Time 0s:   [Build Package] ─────────────────► (completes ~2s)

Time 2s:   [Deploy Web1] ─────────────────────────────────────────► (30s)
           [Deploy Web2] ─────────────────────────────────────────► (30s)
           [Deploy Web3] ─────────────────────────────────────────► (30s)
           (All deployments run simultaneously)

Time 32s:  [Verify Deployments] ───────────► (completes ~3s)

Time 35s:  [Health Check Web1] ─────────────────────► (10s)
           [Health Check Web2] ─────────────────────► (10s)
           [Health Check Web3] ─────────────────────► (10s)
           (All health checks run simultaneously)

Time 45s:  [Summary] ───────────► (completes ~2s)

Total Time: ~47 seconds

Without Parallel Execution: ~104 seconds (30+30+30+10+10+10+4)
Time Saved: 57 seconds (54% faster!)
```

## Real-World Deployment Scenarios

### Scenario 1: Code Deployment with File Transfer
```yaml
- parallel:
    # Copy files to server (local command)
    - run: scp -r ./build/* ${config.servers.web1.username}@${config.servers.web1.ip}:${config.app.deploy_path}/
    
    # Restart service via SSH
    - run-remotely:
        ip: ${config.servers.web1.ip}
        user: ${config.servers.web1.username}
        pass: ${config.servers.web1.password}
        run: cd ${config.app.deploy_path} && sudo systemctl restart nginx
        log-into: ./logs/restart_web1.log
```

### Scenario 2: Database Migration
```yaml
- name: "Run Database Migration"
  run-remotely:
    ip: ${config.servers.web1.ip}
    user: ${config.servers.web1.username}
    pass: ${config.servers.web1.password}
    run: cd ${config.app.deploy_path} && ./migrate.sh
    log-into: ./logs/migration.log  # Stream: tail -f ./logs/migration.log
```

### Scenario 3: Rolling Deployment (one at a time)
```yaml
blocks:
  - name: "Deploy Web1"
    run: [deployment command]
  
  - name: "Verify Web1"
    run: [health check]
  
  - name: "Deploy Web2"
    run: [deployment command]
  
  - name: "Verify Web2"
    run: [health check]
```

## Best Practices for Multi-Server Deployments

### 1. Always Build Before Deploy
```yaml
- name: "Build"
  run: "npm run build && tar -czf app.tar.gz dist/"

- parallel:
    # Deploy to all servers
```

### 2. Verify Each Stage
```yaml
- parallel:
    # Deployments
    
- name: "Verify All Deployments"
  run: # Check logs

- parallel:
    # Health checks
```

### 3. Keep Logs Organized
```
logs/
├── deploy_web1.log
├── deploy_web2.log
├── deploy_web3.log
├── health_web1.log
├── health_web2.log
└── health_web3.log
```

### 4. Include Rollback Capability
```yaml
- name: "Backup Current Version"
  run-remotely:
    ip: ${config.servers.web1.ip}
    user: ${config.servers.web1.username}
    pass: ${config.servers.web1.password}
    run: cp -r ${config.app.deploy_path} ${config.app.deploy_path}.backup
    log-into: ./logs/backup.log

# If deployment fails, rollback:
- name: "Rollback"
  run-remotely:
    ip: ${config.servers.web1.ip}
    user: ${config.servers.web1.username}
    pass: ${config.servers.web1.password}
    run: rm -rf ${config.app.deploy_path} && mv ${config.app.deploy_path}.backup ${config.app.deploy_path}
    log-into: ./logs/rollback.log
```

### 5. Monitor Deployment Progress
```yaml
# Watch progress: tail -f ./logs/deploy_web1.log
- parallel:
    - name: "Deploy Web1"
      run-remotely:
        ip: ${config.servers.web1.ip}
        user: ${config.servers.web1.username}
        pass: ${config.servers.web1.password}
        run: |
          echo 'Starting deployment...'
          date
          [deployment commands]
          echo 'Deployment complete!'
          date
        log-into: ./logs/deploy_web1.log
```

## Scaling to More Servers

To deploy to additional servers, simply add them to the configuration and parallel block:

**storage/config.yaml:**
```yaml
servers:
  web1: { ip: "10.0.1.10", username: "deploy", password: "pass" }
  web2: { ip: "10.0.1.11", username: "deploy", password: "pass" }
  web3: { ip: "10.0.1.12", username: "deploy", password: "pass" }
  web4: { ip: "10.0.1.13", username: "deploy", password: "pass" }
  web5: { ip: "10.0.1.14", username: "deploy", password: "pass" }
```

**main.yaml:**
```yaml
- parallel:
    - name: "Deploy Web1"
      run: [...]
    - name: "Deploy Web2"
      run: [...]
    - name: "Deploy Web3"
      run: [...]
    - name: "Deploy Web4"  # New server
      run: [...]
    - name: "Deploy Web5"  # New server
      run: [...]
```

The framework automatically handles any number of parallel tasks!

## Use Cases

✅ **Web Application Deployment** - Deploy to load-balanced web servers
✅ **Microservices Updates** - Update multiple services simultaneously
✅ **Configuration Management** - Push config changes to all servers
✅ **Database Cluster Updates** - Update replica databases in parallel
✅ **Container Deployments** - Deploy to multiple Docker hosts
✅ **Log Collection** - Gather logs from multiple servers at once
✅ **Backup Operations** - Backup multiple systems simultaneously

## Key Takeaways
- Parallel deployments dramatically reduce total deployment time
- Each deployment logs independently for easy troubleshooting
- Health checks verify successful deployment before completion
- Variable interpolation makes it easy to manage multiple servers
- The pattern scales to any number of servers

## Next Steps
- Configure your actual web servers in `config.yaml`
- Try deploying a real application
- Add rollback capabilities for production use
- Explore the next example: **07-data-pipeline**

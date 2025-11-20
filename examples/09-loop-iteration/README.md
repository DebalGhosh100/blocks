# Example 9: Loop Iteration & List Comprehension

## Overview
This example demonstrates Cocoon's powerful **loop iteration** feature that allows you to iterate over lists defined in your storage YAML files. Think of it as "list comprehension" for workflows - write once, execute many times with different data.

## What This Example Demonstrates
- ✅ **Simple loops** over string lists
- ✅ **Dictionary loops** over structured data
- ✅ **Parallel loop execution** for simultaneous operations
- ✅ **Remote execution loops** for multi-server operations
- ✅ **Nested loops** for complex structures
- ✅ **Loop with conditionals** for dynamic behavior

## Prerequisites
- Python 3.x installed
- Cocoon framework installed
- Basic understanding of YAML syntax

## Directory Structure
```
09-loop-iteration/
├── main.yaml              # Workflow with loop examples
├── storage/               # Configuration files with lists
│   ├── config.yaml        # Simple string lists
│   ├── servers.yaml       # Server configurations
│   ├── datasets.yaml      # Data source URLs
│   └── structure.yaml     # Nested directory structures
└── README.md              # This file
```

## How to Run

```bash
cd examples/09-loop-iteration
python3 ../../blocks_executor.py main.yaml
```

## Loop Patterns

### Pattern 1: Simple Loop (Sequential)
**Use case:** Create multiple directories from a list

```yaml
- for:
    individual: folder-name
    in: ${config.backup-folders}
    run: mkdir -p ./backups/${folder-name}
```

**How it works:**
- `individual`: Name for each item in the iteration (like a loop variable)
- `in`: Path to the list in your storage YAML
- `run`: Command to execute for each item
- Variables: `${folder-name}` gets replaced with each list item

**Result:** Creates directories `data`, `logs`, `configs`, `archives`

### Pattern 2: Dictionary Loop
**Use case:** Process structured data with multiple fields

```yaml
- for:
    individual: server
    in: ${servers.web-servers}
    run: echo "Server: ${server.name} at ${server.ip}:${server.port}"
```

**Storage (servers.yaml):**
```yaml
web-servers:
  - name: "web-01"
    ip: "192.168.1.10"
    port: 8080
  
  - name: "web-02"
    ip: "192.168.1.11"
    port: 8080
```

**How it works:**
- Each item is a dictionary with `name`, `ip`, and `port` fields
- Access fields using dot notation: `${server.name}`, `${server.ip}`, `${server.port}`
- Executes sequentially for each server

### Pattern 3: Parallel Loop Execution
**Use case:** Download multiple files simultaneously

```yaml
- parallel:
    for:
      individual: dataset
      in: ${datasets.sources}
      run: wget -O ./backups/data/${dataset.filename} ${dataset.url}
```

**Why parallel?**
- All downloads start simultaneously
- Dramatically reduces total execution time
- Perfect for I/O-bound operations (downloads, remote commands, database queries)

**Time savings example:**
- Sequential: 3 downloads × 10 seconds each = 30 seconds
- Parallel: All 3 downloads at once = ~10 seconds (67% faster!)

### Pattern 4: Remote Execution with Loops
**Use case:** Run health checks on multiple servers in parallel

```yaml
# Monitor all servers in real-time: tail -f ./backups/logs/*_health.log
- parallel:
    for:
      individual: server
      in: ${servers.production-servers}
      run-remotely:
        ip: ${server.ip}
        user: ${server.username}
        pass: ${server.password}
        run: uptime && df -h && free -m
        log-into: ./backups/logs/${server.name}_health.log
```

**Key features:**
- Combines loop iteration with remote SSH execution
- Parallel execution for all servers simultaneously
- Separate log files for each server (mandatory for parallel remote execution)
- Variable substitution works in all fields: `ip`, `user`, `pass`, `run`, `log-into`
- **Monitor live:** `tail -f ./backups/logs/*_health.log`

**Real-world use case:**
- Deploy updates to 50 servers in parallel
- Collect metrics from 100 servers simultaneously
- Run database migrations across multiple instances

### Pattern 5: Nested Loops
**Use case:** Create complex directory structures

```yaml
- for:
    individual: project
    in: ${structure.projects}
    run: mkdir -p ${project.name}
    for:
      individual: subdir
      in: ${project.subdirectories}
      run: mkdir -p ${project.name}/${subdir.name}
```

**Storage (structure.yaml):**
```yaml
projects:
  - name: "project-alpha"
    subdirectories:
      - name: "src"
      - name: "tests"
      - name: "docs"
  
  - name: "project-beta"
    subdirectories:
      - name: "frontend"
      - name: "backend"
```

**How it works:**
1. Outer loop iterates over projects
2. For each project, creates the project directory
3. Inner loop iterates over that project's subdirectories
4. Creates nested structure automatically

**Result:**
```
project-alpha/
  ├── src/
  ├── tests/
  └── docs/
project-beta/
  ├── frontend/
  └── backend/
```

### Pattern 6: Loop with Conditionals
**Use case:** Dynamic behavior based on item values

```yaml
- for:
    individual: file-type
    in: ${config.file-types}
    run: |
      if [ "${file-type}" = "logs" ]; then
        echo "Processing log files..."
        ls -la ./backups/${file-type}/*.log
      else
        echo "Skipping ${file-type}"
      fi
```

**How it works:**
- Loop variable can be used in shell conditionals
- Different actions based on item value
- Combines loop power with shell scripting flexibility

## Real-World Use Cases

### 1. Multi-Server Deployment
```yaml
# Watch deployment progress: tail -f ./deploy-logs/*.log
- parallel:
    for:
      individual: server
      in: ${infrastructure.app-servers}
      run-remotely:
        ip: ${server.ip}
        user: ${server.deploy-user}
        pass: ${server.deploy-pass}
        run: |
          cd /opt/app
          git pull origin main
          npm install
          pm2 restart app
        log-into: ./deploy-logs/${server.name}.log  # Stream: tail -f ./deploy-logs/${server.name}.log
```

### 2. Database Backup Rotation
```yaml
- for:
    individual: database
    in: ${databases.production-dbs}
    run: |
      pg_dump -h ${database.host} -U ${database.user} ${database.name} \
        > ./backups/db/${database.name}_$(date +%Y%m%d).sql
      
      # Keep only last 7 days of backups
      find ./backups/db/${database.name}_*.sql -mtime +7 -delete
```

### 3. Configuration File Generation
```yaml
- for:
    individual: env
    in: ${environments.all}
    run: |
      cat > ./configs/${env.name}.conf << EOF
      SERVER_NAME=${env.name}
      API_URL=${env.api-url}
      DATABASE_HOST=${env.db-host}
      LOG_LEVEL=${env.log-level}
      EOF
```

### 4. Test Suite Execution
```yaml
- parallel:
    for:
      individual: test-suite
      in: ${testing.suites}
      run: |
        echo "Running ${test-suite.name}..."
        pytest ${test-suite.path} \
          --junit-xml=./test-results/${test-suite.name}.xml \
          --cov=${test-suite.coverage-path}
```

### 5. Multi-Environment CI/CD
```yaml
- for:
    individual: stage
    in: ${pipeline.stages}
    run: echo "=== Stage: ${stage.name} ==="
    parallel:
      for:
        individual: job
        in: ${stage.jobs}
        run: |
          echo "Running ${job.name}..."
          ${job.command}
          echo "${job.name} completed"
```

## Variable Substitution Rules

### Simple String Lists
```yaml
# Storage: config.yaml
folders: ["data", "logs", "temp"]

# Usage in workflow
- for:
    individual: folder
    in: ${config.folders}
    run: mkdir ${folder}  # ${folder} = "data", "logs", "temp"
```

### Dictionary Lists
```yaml
# Storage: servers.yaml
servers:
  - name: "web-01"
    ip: "10.0.1.10"
    port: 8080

# Usage in workflow
- for:
    individual: srv
    in: ${servers.servers}
    run: echo "${srv.name} at ${srv.ip}:${srv.port}"
    # ${srv.name} = "web-01"
    # ${srv.ip} = "10.0.1.10"
    # ${srv.port} = 8080
```

### Nested Structures
```yaml
# Storage: structure.yaml
projects:
  - name: "alpha"
    subdirs:
      - name: "src"
      - name: "test"

# Usage in workflow
- for:
    individual: proj
    in: ${structure.projects}
    run: mkdir ${proj.name}
    for:
      individual: sub
      in: ${proj.subdirs}
      run: mkdir ${proj.name}/${sub.name}
      # Outer variable (proj) accessible in inner loop
```

## Performance Comparison

### Sequential vs Parallel Loops

**Scenario:** Download 10 files, each takes 5 seconds

**Sequential:**
```yaml
- for:
    individual: file
    in: ${files.list}
    run: wget ${file.url}
```
⏱️ Total time: 10 × 5s = **50 seconds**

**Parallel:**
```yaml
- parallel:
    for:
      individual: file
      in: ${files.list}
      run: wget ${file.url}
```
⏱️ Total time: **~5 seconds** (90% faster!)

### When to Use Parallel Loops

✅ **Good for parallel:**
- Network operations (downloads, API calls)
- Remote SSH commands
- Database queries
- File I/O operations
- Independent computations

❌ **Not suitable for parallel:**
- Operations that must be sequential (dependencies)
- Operations that modify shared state
- CPU-bound tasks (Python GIL limitation)

## Best Practices

### 1. Descriptive Variable Names
```yaml
# ✅ Good
- for:
    individual: backup-location
    in: ${storage.backup-paths}

# ❌ Bad
- for:
    individual: x
    in: ${storage.backup-paths}
```

### 2. Use Parallel for Independent Operations
```yaml
# ✅ Parallel - operations are independent
- parallel:
    for:
      individual: server
      in: ${servers.list}
      run: ssh ${server.ip} "systemctl status app"

# ❌ Sequential when parallel would work
- for:
    individual: server
    in: ${servers.list}
    run: ssh ${server.ip} "systemctl status app"
```

### 3. Mandatory Log Files for Parallel Remote Execution
```yaml
# ✅ Correct - log files prevent output mixing
# Stream logs: tail -f ./logs/*.log
- parallel:
    for:
      individual: srv
      in: ${servers.list}
      run-remotely:
        ip: ${srv.ip}
        user: ${srv.user}
        pass: ${srv.pass}
        run: "uptime"
        log-into: ./logs/${srv.name}.log  # Required! Monitor: tail -f ./logs/${srv.name}.log

# ❌ Will fail - missing log-into
- parallel:
    for:
      individual: srv
      in: ${servers.list}
      run-remotely:
        ip: ${srv.ip}
        run: "uptime"
        # Missing log-into field!
```

### 4. Structure Configuration for Reusability
```yaml
# ✅ Good - reusable lists
environments:
  - name: "dev"
    api-url: "https://dev-api.example.com"
  - name: "prod"
    api-url: "https://api.example.com"

# ❌ Bad - hardcoded values
- run: deploy dev https://dev-api.example.com
- run: deploy prod https://api.example.com
```

## Common Patterns

### Pattern: Loop + Cleanup
```yaml
- for:
    individual: temp-dir
    in: ${config.temp-directories}
    run: |
      mkdir -p ${temp-dir}
      # Do work...
      rm -rf ${temp-dir}
```

### Pattern: Loop + Error Handling
```yaml
- for:
    individual: service
    in: ${services.list}
    run: |
      if systemctl is-active ${service.name}; then
        echo "${service.name} is running"
      else
        echo "ERROR: ${service.name} is down" >&2
        exit 1
      fi
```

### Pattern: Loop + Progress Tracking
```yaml
- for:
    individual: task
    in: ${tasks.batch}
    run: |
      echo "Processing ${task.id}..."
      process-task ${task.id}
      echo "✓ ${task.id} complete"
```

## Troubleshooting

### Issue: Variable not substituted
**Problem:** `${variable}` appears in output instead of actual value

**Solution:** Check the path is correct in storage YAML
```yaml
# Workflow
in: ${config.items}

# Storage must have this structure
# config.yaml:
items:
  - value1
  - value2
```

### Issue: Nested loop fails
**Problem:** Inner loop can't access outer variable

**Solution:** Use the outer variable in the inner loop's `in` path
```yaml
for:
  individual: parent
  in: ${data.parents}
  for:
    individual: child
    in: ${parent.children}  # Correct!
    # NOT: ${data.parents.children}
```

### Issue: Parallel remote execution fails
**Problem:** "log-into field required" error

**Solution:** Always provide `log-into` for parallel remote execution
```yaml
- parallel:
    for:
      individual: srv
      in: ${servers.list}
      run-remotely:
        ip: ${srv.ip}
        user: ${srv.user}
        pass: ${srv.pass}
        run: "command"
        log-into: ./logs/${srv.name}.log  # Required for parallel!
```

## Key Takeaways
- ✅ Loops eliminate repetitive workflow code
- ✅ Works with both simple lists and complex dictionaries
- ✅ Parallel loops provide massive performance improvements
- ✅ Nested loops enable complex structure creation
- ✅ Combines seamlessly with remote execution
- ✅ Variable substitution works in all block fields
- ✅ Configuration-driven approach improves maintainability

## Next Steps
- Try modifying the storage YAML files with your own data
- Experiment with different loop combinations
- Build a multi-server deployment workflow
- Combine loops with the other examples (parallel, remote, etc.)

---

**Pro Tip:** Loops are most powerful when combined with:
1. **Parallel execution** - for speed
2. **Remote execution** - for multi-server operations
3. **Variable interpolation** - for configuration-driven workflows

This combination allows you to write a single workflow that scales from 1 to 1000+ servers! 🚀

# Example 7: Conditional Logic and Error Handling

## Overview
This example demonstrates advanced shell scripting techniques within Blocks workflows, including conditional execution, error handling, retry logic, and cleanup operations.

## What This Example Demonstrates
- ✅ If/else conditional statements
- ✅ File and directory existence checks
- ✅ Numeric and string comparisons
- ✅ Complex conditions with AND/OR logic
- ✅ Case/switch statements
- ✅ Error handling and graceful failures
- ✅ Retry logic with exponential backoff
- ✅ Cleanup operations with trap
- ✅ Loop iterations with conditionals

## Prerequisites
- Python 3.x installed
- Blocks framework installed
- Basic understanding of shell scripting

## Directory Structure
```
07-conditional-logic/
├── main.yaml           # Workflow with conditional logic
├── storage/            # Configuration files
│   └── config.yaml     # Configuration values for conditionals
└── README.md           # This file
```

## How to Run

```bash
# Clone this specific example
git clone --depth 1 --filter=blob:none --sparse https://github.com/DebalGhosh100/blocks.git
cd blocks
git sparse-checkout set examples/07-conditional-logic
cd examples/07-conditional-logic

# Run with one-command execution
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

**What this does:**
1. Clones only this example directory (sparse checkout)
2. Downloads the Blocks framework automatically
3. Installs dependencies (paramiko, pyyaml)
4. Executes the conditional logic workflow
5. Cleans up framework files after completion

## Expected Output

The workflow demonstrates various conditional patterns:
1. File existence checking and creation
2. Directory validation and permission checks
3. Environment variable validation
4. Error handling with graceful fallbacks
5. Numeric threshold comparisons
6. String-based environment switching
7. Complex multi-condition checks
8. Case statement for action routing
9. Loop processing with conditional filtering
10. Retry logic with backoff
11. Error trapping and cleanup

## Conditional Logic Patterns

### 1. File Existence Check

```bash
if [ -f "$file" ]; then
  echo "File exists"
else
  echo "File does not exist"
  # Create the file
fi
```

**Use Cases:**
- Check if configuration file exists before reading
- Verify output file from previous step
- Prevent overwriting existing files

### 2. Directory Validation

```bash
if [ -d "$directory" ]; then
  echo "Directory exists"
  
  if [ -w "$directory" ]; then
    echo "Directory is writable"
  fi
else
  mkdir -p "$directory"
fi
```

**Use Cases:**
- Ensure output directories exist
- Verify write permissions before processing
- Create directory structure on-demand

### 3. Numeric Comparisons

```bash
threshold=100
current_value=75

if [ $current_value -gt $threshold ]; then
  echo "Exceeds threshold"
elif [ $current_value -eq $threshold ]; then
  echo "At threshold"
else
  echo "Within range"
fi
```

**Operators:**
- `-eq`: equal to
- `-ne`: not equal to
- `-gt`: greater than
- `-ge`: greater than or equal to
- `-lt`: less than
- `-le`: less than or equal to

**Use Cases:**
- Disk space monitoring
- Resource threshold checks
- File size validation

### 4. String Comparisons

```bash
environment="production"

if [ "$environment" = "production" ]; then
  echo "Production mode"
elif [ "$environment" = "staging" ]; then
  echo "Staging mode"
else
  echo "Development mode"
fi
```

**Use Cases:**
- Environment-specific behavior
- Configuration switching
- Input validation

### 5. Complex Conditions (AND/OR)

```bash
# AND logic
if [ condition1 ] && [ condition2 ]; then
  echo "Both conditions true"
fi

# OR logic
if [ condition1 ] || [ condition2 ]; then
  echo "At least one condition true"
fi
```

**Example:**
```bash
if [ -f "$file" ] && [ -r "$file" ]; then
  echo "File exists and is readable"
fi
```

### 6. Case Statements

```bash
action="start"

case $action in
  "start")
    echo "Starting service"
    ;;
  "stop")
    echo "Stopping service"
    ;;
  "restart")
    echo "Restarting service"
    ;;
  *)
    echo "Unknown action"
    exit 1
    ;;
esac
```

**Use Cases:**
- Command routing
- Multi-option processing
- Status code handling

### 7. Error Handling

```bash
# Continue on error
command || echo "Command failed but continuing"

# Exit on error
command || {
  echo "Command failed"
  exit 1
}

# Try with fallback
primary_command || backup_command
```

**Example:**
```bash
if curl -f http://api.example.com/data; then
  echo "API call successful"
else
  echo "API call failed, using cached data"
  cat cached_data.json
fi
```

### 8. Retry Logic

```bash
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
  retry_count=$((retry_count + 1))
  
  if command; then
    echo "Success"
    break
  else
    echo "Attempt $retry_count failed"
    sleep $((retry_count * 2))  # Exponential backoff
  fi
done
```

**Use Cases:**
- Network operations
- Database connections
- File downloads

### 9. Cleanup with Trap

```bash
cleanup() {
  echo "Cleaning up..."
  rm -f temp_files*
}

trap cleanup EXIT

# Your commands here
# cleanup() runs automatically on exit
```

**Use Cases:**
- Remove temporary files
- Close connections
- Release resources

### 10. Loops with Conditionals

```bash
for i in {1..10}; do
  if [ $((i % 2)) -eq 0 ]; then
    echo "Even: $i"
  else
    echo "Odd: $i"
  fi
done
```

**Use Cases:**
- Batch processing with filtering
- Selective operations
- Iterative validation

## Real-World Examples

### Example 1: Pre-Flight Checks

```yaml
- name: "Pre-Flight Validation"
  run: |
    echo "Running pre-flight checks..."
    
    # Check disk space
    available=$(df / | tail -1 | awk '{print $4}')
    required=1000000
    
    if [ $available -lt $required ]; then
      echo "ERROR: Insufficient disk space"
      exit 1
    fi
    
    # Check required files
    for file in config.yaml data.csv script.sh; do
      if [ ! -f "$file" ]; then
        echo "ERROR: Missing required file: $file"
        exit 1
      fi
    done
    
    echo "All pre-flight checks passed!"
```

### Example 2: Environment-Specific Deployment

```yaml
- name: "Deploy Application"
  run: |
    environment=${config.environment}
    
    case $environment in
      "production")
        echo "Deploying to production..."
        target="/var/www/prod"
        restart_cmd="sudo systemctl restart nginx"
        ;;
      "staging")
        echo "Deploying to staging..."
        target="/var/www/staging"
        restart_cmd="sudo systemctl restart nginx-staging"
        ;;
      "development")
        echo "Deploying to development..."
        target="./dev-server"
        restart_cmd="./restart-dev.sh"
        ;;
      *)
        echo "ERROR: Unknown environment: $environment"
        exit 1
        ;;
    esac
    
    # Deploy to target
    cp -r ./build/* $target/
    $restart_cmd
```

### Example 3: Conditional SSH Execution

```yaml
- name: "Remote Server Check"
  run: |
    server_ip=${servers.web1.ip}
    
    # Check if server is reachable
    if ping -c 1 $server_ip >/dev/null 2>&1; then
      echo "Server is reachable, proceeding with deployment..."
      
      python3 ../../remotely.py \
        ${servers.web1.username}@${servers.web1.ip} \
        ${servers.web1.password} \
        "systemctl status nginx" \
        ./logs/server_status.log
    else
      echo "ERROR: Server is not reachable"
      echo "Skipping deployment for this server"
    fi
```

### Example 4: Data Validation Pipeline

```yaml
- name: "Validate Data Quality"
  run: |
    input_file="data.csv"
    min_records=1000
    
    # Check file exists
    if [ ! -f "$input_file" ]; then
      echo "ERROR: Input file not found"
      exit 1
    fi
    
    # Check record count
    record_count=$(wc -l < "$input_file")
    
    if [ $record_count -lt $min_records ]; then
      echo "WARNING: Only $record_count records (minimum: $min_records)"
      echo "Proceeding with caution..."
    else
      echo "PASSED: $record_count records found"
    fi
    
    # Validate data format
    if head -1 "$input_file" | grep -q "id,name,value"; then
      echo "PASSED: Header format valid"
    else
      echo "ERROR: Invalid header format"
      exit 1
    fi
    
    echo "Data validation complete!"
```

### Example 5: Backup with Rotation

```yaml
- name: "Backup with Rotation"
  run: |
    backup_dir="./backups"
    max_backups=5
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Check number of existing backups
    backup_count=$(ls -1 "$backup_dir" | wc -l)
    
    if [ $backup_count -ge $max_backups ]; then
      echo "Maximum backups reached, removing oldest..."
      oldest=$(ls -t "$backup_dir" | tail -1)
      rm "$backup_dir/$oldest"
      echo "Removed: $oldest"
    fi
    
    # Create new backup
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "$backup_dir/backup_$timestamp.tar.gz" ./data/
    
    echo "Backup created: backup_$timestamp.tar.gz"
```

## Testing Conditional Logic

### Test Different Scenarios

Modify `storage/config.yaml` to test different paths:

```yaml
config:
  environment: "production"  # Try: staging, development
  action: "start"            # Try: stop, restart, status, invalid
  
  thresholds:
    max_size: 50             # Change to test different comparisons
```

### Simulate Failures

```bash
# Modify workflow to test error handling
- name: "Test Error Handling"
  run: |
    # Force a failure
    if false; then
      echo "This won't execute"
    else
      echo "Error handled gracefully"
    fi
```

## Best Practices

### 1. Always Quote Variables
```bash
# Good
if [ "$var" = "value" ]; then

# Bad (can break with spaces)
if [ $var = value ]; then
```

### 2. Check Exit Codes
```bash
if command; then
  # Success path
else
  # Failure path
fi
```

### 3. Provide Informative Messages
```bash
echo "✓ Success: Operation completed"
echo "✗ Error: Operation failed"
echo "⚠ Warning: Proceeding with caution"
```

### 4. Use Meaningful Variable Names
```bash
# Good
max_retry_count=3

# Bad
x=3
```

### 5. Fail Fast on Critical Errors
```bash
if [ critical_check_failed ]; then
  echo "CRITICAL ERROR"
  exit 1
fi
```

## Common Pitfalls

### 1. Missing Quotes
```bash
# Wrong
if [ $var = value ]; then

# Right
if [ "$var" = "value" ]; then
```

### 2. Using = vs ==
```bash
# In [ ], use =
if [ "$var" = "value" ]; then

# In [[ ]], can use ==
if [[ "$var" == "value" ]]; then
```

### 3. Forgetting -z/-n for Empty Checks
```bash
# Check if empty
if [ -z "$var" ]; then
  echo "Variable is empty"
fi

# Check if not empty
if [ -n "$var" ]; then
  echo "Variable is set"
fi
```

## Key Takeaways
- Conditional logic enables intelligent, adaptive workflows
- Proper error handling prevents cascading failures
- Retry logic improves resilience for transient failures
- Cleanup operations ensure resource management
- Variable interpolation works seamlessly with conditionals

## Next Steps
- Modify the conditionals to match your use cases
- Add custom validation logic
- Implement environment-specific behaviors
- Explore the next example: **08-complex-workflow**

# Example 3: Variable Interpolation

## Overview
This example demonstrates how to use variable interpolation to reference configuration values stored in YAML files. This feature allows you to centralize configuration and reuse values throughout your workflow.

## What This Example Demonstrates
- ✅ Variable interpolation using `${filename.key.path}` syntax
- ✅ Reading from configuration files in the `storage/` directory
- ✅ Nested configuration values (multiple levels deep)
- ✅ Using variables in command construction
- ✅ Centralizing configuration management

## Prerequisites
- Python 3.x installed
- Blocks framework installed

## Directory Structure
```
03-variable-interpolation/
├── main.yaml           # Workflow using variables
├── storage/            # Configuration files
│   └── config.yaml     # Application configuration with nested values
└── README.md           # This file
```

## How to Run

### Option 1: From the Example Directory
```bash
# Navigate to this example
cd blocks/examples/03-variable-interpolation

# Run the workflow
python3 ../../blocks_executor.py main.yaml
```

### Option 2: Run with One-Command Execution
```bash
# From this directory
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

## Expected Output
The workflow will:
1. Display application information from config
2. Show database connection details
3. Display file system paths
4. Show server configuration
5. Create directories based on configured paths
6. Construct and display API endpoint URL
7. Clean up created directories

## Configuration File (`storage/config.yaml`)

```yaml
app:
  name: "MyAwesomeApp"
  version: "2.1.5"
  environment: "production"
  debug: false

database:
  host: "db.example.com"
  port: 5432
  name: "app_database"
  credentials:
    username: "dbuser"
    password: "secure_password_123"

paths:
  logs: "./app_logs"
  data: "./app_data"
  backups: "./app_backups"
  temp: "./app_temp"

servers:
  web:
    host: "web.example.com"
    port: 80
  api:
    host: "api.example.com"
    port: 8080
    endpoint: "/v1/status"
    key: "abc123xyz789"
```

## Variable Interpolation Syntax

### Basic Syntax
```yaml
${filename.key1.key2.key3}
```

- `filename`: Name of the YAML file in `storage/` (without `.yaml` extension)
- `key1.key2.key3`: Dot-separated path to the value

### Examples from This Workflow

#### Simple Value
```yaml
run: "echo 'Application: ${app.name}'"
```
References `config.yaml` → `app` → `name` → Result: `"MyAwesomeApp"`

#### Nested Value (3 levels deep)
```yaml
run: "echo 'Username: ${database.credentials.username}'"
```
References `config.yaml` → `database` → `credentials` → `username` → Result: `"dbuser"`

#### Multiple Variables in One Command
```yaml
run: "echo 'Server: ${servers.web.host}:${servers.web.port}'"
```
Result: `"Server: web.example.com:80"`

#### Complex String Construction
```yaml
run: "echo 'Connection: postgresql://${database.credentials.username}@${database.host}:${database.port}/${database.name}'"
```
Result: `"Connection: postgresql://dbuser@db.example.com:5432/app_database"`

## Workflow Breakdown

### Block 1: Display Application Info
```yaml
- name: "Display Application Info"
  run: |
    echo "Application: ${app.name}"
    echo "Version: ${app.version}"
    echo "Environment: ${app.environment}"
    echo "Debug Mode: ${app.debug}"
```
Demonstrates accessing top-level configuration values.

### Block 2: Show Database Configuration
```yaml
- name: "Show Database Configuration"
  run: |
    echo "Host: ${database.host}"
    echo "Port: ${database.port}"
    echo "Username: ${database.credentials.username}"
```
Shows both simple values (`database.host`) and nested values (`database.credentials.username`).

### Block 5: Create Directories from Config
```yaml
- name: "Create Directories from Config"
  run: |
    mkdir -p ${paths.logs} ${paths.data} ${paths.backups} ${paths.temp}
```
Uses variables as command arguments - very powerful for dynamic workflows!

## Using Multiple Configuration Files

You can create multiple YAML files in the `storage/` directory:

**storage/servers.yaml:**
```yaml
production:
  web: "prod-web.example.com"
  api: "prod-api.example.com"

staging:
  web: "staging-web.example.com"
  api: "staging-api.example.com"
```

**storage/credentials.yaml:**
```yaml
admin:
  username: "admin"
  password: "admin123"
```

**In your workflow:**
```yaml
blocks:
  - run: "echo 'Production Web: ${servers.production.web}'"
  - run: "echo 'Admin User: ${credentials.admin.username}'"
```

## Benefits of Variable Interpolation

✅ **Centralized Configuration**: All settings in one place
✅ **Reusability**: Use the same values across multiple blocks
✅ **Easy Updates**: Change configuration without modifying workflow
✅ **Environment Management**: Switch between dev/staging/prod configs
✅ **Security**: Separate credentials from workflow logic
✅ **Maintainability**: Cleaner, more readable workflows

## Best Practices

### 1. Organize Configuration by Purpose
```
storage/
├── app.yaml          # Application settings
├── servers.yaml      # Server configurations
├── credentials.yaml  # Authentication details
└── paths.yaml        # File system paths
```

### 2. Use Descriptive Key Names
```yaml
# Good
database:
  connection:
    host: "db.example.com"
    port: 5432

# Avoid
db:
  h: "db.example.com"
  p: 5432
```

### 3. Group Related Values
```yaml
# Good - grouped by server
servers:
  api:
    host: "api.example.com"
    port: 8080
    timeout: 30

# Avoid - scattered
api_host: "api.example.com"
api_port: 8080
api_timeout: 30
```

### 4. Don't Store Sensitive Data in Plain Text
For production use, consider:
- Environment variables
- Secret management tools (HashiCorp Vault, AWS Secrets Manager)
- Encrypted configuration files

## Key Takeaways
- Variable interpolation uses `${filename.key.path}` syntax
- Configuration files must be in the `storage/` directory
- Variables can be used anywhere in commands
- Multiple variables can be used in a single command
- Nested values are accessed with dot notation
- This feature enables powerful configuration management

## Next Steps
- Try adding your own configuration values
- Create multiple configuration files and reference them
- Explore the next example: **04-ssh-remote-execution**

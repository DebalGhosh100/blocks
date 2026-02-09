# Cocoon Tests

This directory contains test workflows to verify framework functionality.

## Test Files

### test_refactor_validation.yaml
**Purpose:** Quick validation test for refactored code  
**What it tests:**
- Basic command execution
- Directory creation and navigation
- File operations
- Directory state persistence
- Command chaining with `&&`

**Run with:**
```bash
python ../blocks_executor.py test_refactor_validation.yaml
```

---

### test_compound_cd.yaml
**Purpose:** Test compound cd commands with shell operators  
**What it tests:**
- `cd dir && command` patterns
- Directory persistence after compound commands
- Multiple directory changes in workflow
- Relative path resolution

**Run with:**
```bash
python ../blocks_executor.py test_compound_cd.yaml
```

---

### test_directory_persistence.yaml
**Purpose:** Simulate real-world Yocto build workflow directory changes  
**What it tests:**
- Complex directory navigation patterns
- `cd` at end of compound commands
- Nested directory creation
- Directory state across multiple blocks

**Run with:**
```bash
python ../blocks_executor.py test_directory_persistence.yaml
```

---

### test_all_cd_cases.yaml
**Purpose:** Comprehensive test of all directory change scenarios  
**What it tests:**
- Simple `cd` commands
- `cd` at beginning of compound commands
- `cd` at end of compound commands
- Multiple `cd` in one command
- Relative paths with `../`
- Sibling directory navigation
- Complex compound commands with `cd` in middle

**Run with:**
```bash
python ../blocks_executor.py test_all_cd_cases.yaml
```

---

## Running All Tests

To run all tests sequentially:

**Linux/Mac:**
```bash
for test in tests/*.yaml; do
    echo "Running $test..."
    python blocks_executor.py "$test"
    echo "---"
done
```

**Windows PowerShell:**
```powershell
Get-ChildItem tests\*.yaml | ForEach-Object {
    Write-Host "Running $_..."
    python ..\blocks_executor.py $_
    Write-Host "---"
}
```

---

### test_loops.yaml
**Purpose:** Test loop iteration over lists from parameters configuration  
**What it tests:**
- Simple for-loop over list of strings
- Loop over list of dictionaries
- Variable substitution within loops
- Loops in parallel execution

**Run with:**
```bash
python ../blocks_executor.py test_loops.yaml
```

---

## Loop Testing

The `test_loops.yaml` file demonstrates the new loop iteration feature that allows you to iterate over lists defined in parameters YAML files.

### Example Patterns

**Pattern 1: Simple loop over strings**
```yaml
- for:
    individual: item
    in: ${config.list}
    run: echo "Processing ${item}"
```

**Pattern 2: Loop over dictionary items**
```yaml
- for:
    individual: server
    in: ${machines.servers}
    run: echo "Server: ${server.ip}"
```

**Pattern 3: Nested loops**
```yaml
- for:
    individual: parent
    in: ${config.parents}
    run: mkdir -p ${parent.name}
    for:
      individual: child
      in: ${parent.children}
      run: mkdir -p ${parent.name}/${child.name}
```

**Pattern 4: Parallel execution with loops**
```yaml
- parallel:
    for:
      individual: server
      in: ${machines.servers}
      run-remotely:
        ip: ${server.ip}
        user: ${server.username}
        pass: ${server.password}
        run: "command"
        log-into: ./logs/${server.ip}.log
```

**Windows PowerShell:**
```powershell
Get-ChildItem tests\*.yaml | ForEach-Object {
    Write-Host "Running $($_.Name)..." -ForegroundColor Cyan
    python blocks_executor.py $_.FullName
    Write-Host "---"
}
```

## Expected Results

All tests should:
- ✅ Complete without errors
- ✅ Show colored output with execution status
- ✅ Clean up any created directories/files
- ✅ Display execution summary at the end

## Troubleshooting

If a test fails:
1. Check the error message in red
2. Verify you're in the correct directory
3. Ensure bash (Linux/Mac) or PowerShell (Windows) is available
4. Check that Python 3.x is installed
5. Verify all dependencies in `requirements.txt` are installed

# Blocks - Examples & Tutorials

Welcome to the Blocks examples directory! This collection of examples demonstrates every feature and capability of the Blocks workflow automation framework, from simple sequential execution to complex multi-phase CI/CD pipelines.

## Table of Contents

- [Getting Started](#getting-started)
- [Examples Overview](#examples-overview)
- [Learning Path](#learning-path)
- [Quick Reference](#quick-reference)
- [Contributing Examples](#contributing-examples)

---

## Getting Started

### Prerequisites
- Python 3.x installed
- Blocks framework installed in parent directory
- Basic understanding of YAML and shell commands

### Running Examples

Each example is self-contained with its own `main.yaml`, `storage/` directory, and detailed `README.md`.

**To run any example:**
```bash
cd examples/<example-name>
python3 ../../blocks_executor.py main.yaml
```

**Example:**
```bash
cd examples/01-basic-sequential
python3 ../../blocks_executor.py main.yaml
```

---

## Examples Overview

### 1. Basic Sequential Execution
**Directory:** `01-basic-sequential/`  
**Difficulty:** 🟢 Beginner  
**Duration:** 2-3 minutes

Learn the fundamentals of Blocks with simple sequential command execution.

**What You'll Learn:**
- Basic block structure with `name`, `description`, and `run`
- Sequential execution order
- Simple shell commands
- File creation and cleanup

**Use Cases:**
- System setup scripts
- Simple automation tasks
- Learning the basics

[📖 Read Full Guide](./01-basic-sequential/README.md)

---

### 2. Parallel Execution
**Directory:** `02-parallel-execution/`  
**Difficulty:** 🟢 Beginner  
**Duration:** 5-7 seconds (demonstrates speed!)

Discover how to run multiple tasks simultaneously for dramatic performance improvements.

**What You'll Learn:**
- `parallel:` keyword syntax
- Simultaneous task execution
- Performance benefits (3x+ speedup)
- Coordination between parallel and sequential blocks

**Use Cases:**
- Downloading multiple files
- Running parallel tests
- Multi-server operations
- Independent data processing

[📖 Read Full Guide](./02-parallel-execution/README.md)

---

### 3. Variable Interpolation
**Directory:** `03-variable-interpolation/`  
**Difficulty:** 🟡 Intermediate  
**Duration:** 2-3 minutes

Master configuration management with variable interpolation from YAML files.

**What You'll Learn:**
- `${filename.key.path}` syntax
- Configuration files in `storage/` directory
- Nested value access
- Multi-file configuration management
- Environment-specific configurations

**Use Cases:**
- Configuration management
- Environment switching (dev/staging/prod)
- Credential management
- Reusable workflows

[📖 Read Full Guide](./03-variable-interpolation/README.md)

---

### 4. SSH Remote Execution
**Directory:** `04-ssh-remote-execution/`  
**Difficulty:** 🟡 Intermediate  
**Duration:** Variable (depends on remote commands)

Execute commands on remote servers via SSH with real-time log streaming.

**What You'll Learn:**
- Using `remotely.py` for SSH execution
- Real-time log streaming to local files
- SSH credential management
- Remote command execution
- Progress bar capture (wget, dd, etc.)

**Use Cases:**
- Remote server management
- Log collection
- Remote deployments
- System monitoring

**Prerequisites:**
- SSH access to a remote server
- Server credentials configured in `storage/machines.yaml`

[📖 Read Full Guide](./04-ssh-remote-execution/README.md)

---

### 5. Loop Iteration
**Directory:** `05-loop-iteration/`  
**Difficulty:** 🟡 Intermediate  
**Duration:** ~10 seconds

Master powerful loop iteration with `for` keyword to process lists, datasets, and multi-server operations.

**What You'll Learn:**
- `for` loop syntax with `individual`, `in`, and `run`
- Iterating over simple lists
- Iterating over complex nested structures
- Parallel loops with `for` inside `parallel`
- Variable interpolation within loops
- Real-world multi-server deployment patterns

**Use Cases:**
- Multi-server operations
- Batch file processing
- Dataset iteration
- Dynamic directory creation
- Repeated task execution

[📖 Read Full Guide](./05-loop-iteration/README.md)

---

### 6. Multi-Server Parallel Deployment
**Directory:** `06-multi-server-deployment/`  
**Difficulty:** 🟡 Intermediate  
**Duration:** ~30 seconds (vs 90+ seconds sequential)

Deploy applications to multiple servers simultaneously with parallel SSH execution.

**What You'll Learn:**
- Parallel SSH deployments
- Multi-stage workflows (Build → Deploy → Verify)
- Health check patterns
- Production deployment strategies
- Time savings with parallel execution (50%+ faster)

**Use Cases:**
- Multi-server deployments
- Load balancer updates
- Cluster management
- Zero-downtime deployments

**Prerequisites:**
- SSH access to multiple servers
- Configured server credentials

[📖 Read Full Guide](./06-multi-server-deployment/README.md)

---

### 7. Data Processing Pipeline
**Directory:** `07-data-pipeline/`  
**Difficulty:** 🟡 Intermediate  
**Duration:** ~15 seconds

Build ETL pipelines with parallel data processing and sequential coordination.

**What You'll Learn:**
- Multi-stage pipeline architecture
- Fan-out/fan-in patterns
- Parallel data processing
- Data validation and transformation
- Report generation and aggregation

**Use Cases:**
- ETL pipelines
- Data analysis workflows
- Log processing
- Batch processing
- Machine learning pipelines

[📖 Read Full Guide](./07-data-pipeline/README.md)

---

### 8. Conditional Logic & Error Handling
**Directory:** `08-conditional-logic/`  
**Difficulty:** 🟠 Advanced  
**Duration:** 3-4 minutes

Implement intelligent workflows with conditionals, error handling, and retry logic.

**What You'll Learn:**
- If/else conditionals
- File and directory validation
- Numeric and string comparisons
- Complex conditions (AND/OR)
- Case/switch statements
- Error handling patterns
- Retry logic with exponential backoff
- Cleanup with trap

**Use Cases:**
- Pre-flight validation
- Environment-specific behavior
- Error recovery
- Robust production workflows

[📖 Read Full Guide](./08-conditional-logic/README.md)

---

## Learning Path

### 🎓 Beginner Track (Start Here!)
1. **01-basic-sequential** - Learn the fundamentals
2. **02-parallel-execution** - Discover parallel processing
3. **03-variable-interpolation** - Master configuration management

**Time Investment:** ~30 minutes  
**Goal:** Understand core Blocks concepts

---

### 🚀 Intermediate Track
4. **04-ssh-remote-execution** - Execute commands remotely
5. **05-loop-iteration** - Master loop patterns
6. **06-multi-server-deployment** - Deploy to multiple servers
7. **07-data-pipeline** - Build data processing workflows

**Time Investment:** ~1 hour  
**Goal:** Build practical automation workflows

---

### 💼 Advanced Track
8. **08-conditional-logic** - Add intelligence to workflows
9. **09-complex-workflow** - Master enterprise patterns

**Time Investment:** ~1-2 hours  
**Goal:** Create production-grade automation

---

## Quick Reference

### Common Patterns

#### Sequential Execution
```yaml
blocks:
  - name: "Step 1"
    run: "command1"
  - name: "Step 2"
    run: "command2"
```

#### Parallel Execution
```yaml
blocks:
  - parallel:
      - name: "Task A"
        run: "command_a"
      - name: "Task B"
        run: "command_b"
```

#### Variable Interpolation
```yaml
# storage/config.yaml
server:
  ip: "192.168.1.100"
  
# main.yaml
blocks:
  - run: "ping ${config.server.ip}"
```

#### SSH Remote Execution
```yaml
blocks:
  # Stream logs: tail -f ./logs/output.log
  - run-remotely:
      ip: ${server.ip}
      user: ${server.user}
      pass: ${server.password}
      run: command
      log-into: ./logs/output.log
```

#### Conditional Logic
```yaml
blocks:
  - run: |
      if [ -f "file.txt" ]; then
        echo "File exists"
      else
        echo "File not found"
      fi
```

---

## Feature Matrix

| Example | Sequential | Parallel | Variables | SSH | Loops | Conditionals | Complexity |
|---------|-----------|----------|-----------|-----|-------|--------------|------------|
| 01-basic-sequential | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | 🟢 Low |
| 02-parallel-execution | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | 🟢 Low |
| 03-variable-interpolation | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | 🟡 Medium |
| 04-ssh-remote-execution | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | 🟡 Medium |
| 05-loop-iteration | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 🟡 Medium |
| 06-multi-server-deployment | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | 🟡 Medium |
| 07-data-pipeline | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | 🟡 Medium |
| 08-conditional-logic | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | 🟠 High |
| 09-complex-workflow | ✅ | ✅ | ✅ | 🟡 | ❌ | ✅ | 🔴 Very High |

🟡 = Simulated (real SSH commands in comments)

---

## Use Case Index

### By Industry

**DevOps & IT Operations:**
- 06-multi-server-deployment
- 09-complex-workflow
- 04-ssh-remote-execution
- 05-loop-iteration

**Data Engineering:**
- 07-data-pipeline
- 05-loop-iteration

**Software Development:**
- 01-basic-sequential
- 02-parallel-execution
- 09-complex-workflow

**System Administration:**
- 04-ssh-remote-execution
- 08-conditional-logic
- 05-loop-iteration

### By Task Type

**Deployment:**
- 06-multi-server-deployment
- 09-complex-workflow

**Testing:**
- 09-complex-workflow (phases 3)

**Data Processing:**
- 07-data-pipeline
- 05-loop-iteration

**Configuration Management:**
- 03-variable-interpolation
- 08-conditional-logic

**Remote Execution:**
- 04-ssh-remote-execution
- 05-loop-iteration
- 06-multi-server-deployment

---

## Tips for Success

### 1. Start Simple
Begin with example 01 and progress sequentially. Each example builds on concepts from previous ones.

### 2. Experiment Freely
All examples are safe to run and modify. They create temporary files and clean up after themselves.

### 3. Read the READMEs
Each example has a comprehensive README with:
- Detailed explanations
- Real-world use cases
- Troubleshooting tips
- Best practices

### 4. Adapt for Your Needs
Use examples as templates for your own workflows. Copy, modify, and extend them.

### 5. Check Variable Interpolation
When using variables, verify:
- YAML file exists in `storage/`
- Variable path is correct (`${filename.key.path}`)
- No typos in variable names

### 6. Test SSH Configurations
For SSH examples (04, 05):
- Update `storage/machines.yaml` with your servers
- Test SSH connection manually first
- Check credentials are correct

---

## Troubleshooting

### Example Won't Run

**Problem:** `python3 ../../blocks_executor.py main.yaml` fails

**Solutions:**
- Ensure you're in the example directory
- Check Blocks framework is in parent directory
- Verify Python 3 is installed: `python3 --version`
- Check file paths are correct

### Variables Not Interpolating

**Problem:** Seeing `${variable.name}` in output instead of value

**Solutions:**
- Check YAML file exists in `storage/`
- Verify variable path syntax
- Ensure no spaces in variable path
- Check for typos in variable names

### SSH Connection Fails

**Problem:** Cannot connect to remote server

**Solutions:**
- Verify server IP address
- Check SSH credentials
- Test manual SSH: `ssh user@host`
- Ensure SSH service is running on remote server

### Parallel Blocks Run Sequentially

**Problem:** Parallel tasks executing one at a time

**Solutions:**
- Check YAML indentation (use spaces, not tabs)
- Verify `parallel:` keyword is present
- Ensure each parallel task uses `-` prefix

---

## Contributing Examples

Have a great example to share? We'd love to include it!

### Example Template Structure
```
XX-example-name/
├── main.yaml           # Workflow definition
├── storage/            # Configuration files
│   └── config.yaml
└── README.md           # Comprehensive guide
```

### README Template Sections
1. Overview
2. What This Example Demonstrates
3. Prerequisites
4. How to Run
5. Expected Output
6. Workflow Breakdown
7. Use Cases
8. Key Takeaways

---

## Additional Resources

- **Main Documentation:** [../README.md](../README.md)
- **GitHub Repository:** https://github.com/DebalGhosh100/blocks
- **Issue Tracker:** Report bugs or request features on GitHub

---

## Example Directory Structure

```
examples/
├── README.md (this file)
├── 01-basic-sequential/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
├── 02-parallel-execution/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
├── 03-variable-interpolation/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
├── 04-ssh-remote-execution/
│   ├── main.yaml
│   ├── storage/
│   │   └── machines.yaml
│   └── README.md
├── 05-loop-iteration/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
├── 06-multi-server-deployment/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
├── 07-data-pipeline/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
├── 08-conditional-logic/
│   ├── main.yaml
│   ├── storage/
│   │   └── config.yaml
│   └── README.md
└── 09-complex-workflow/
    ├── main.yaml
    ├── storage/
    │   └── config.yaml
    └── README.md
```

---

## Summary

You now have **9 comprehensive examples** covering:

✅ Sequential execution  
✅ Parallel processing  
✅ Variable interpolation  
✅ SSH remote execution  
✅ Loop iteration  
✅ Multi-server deployment  
✅ Data pipelines  
✅ Conditional logic  
✅ Complex CI/CD workflows  

**Total Learning Time:** 3-5 hours  
**Skill Level:** Beginner to Expert  
**Ready for Production:** ✅

---

## Quick Start Recommendation

**New to Blocks?** Start here:

```bash
cd examples/01-basic-sequential
python3 ../../blocks_executor.py main.yaml
```

Then progress through examples 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09

**Need production workflows?** Jump to:
- Example 05 for loop iteration patterns
- Example 06 for multi-server deployment
- Example 09 for complete CI/CD pipeline

---

**Happy Automating! 🚀**

For questions or issues, visit: https://github.com/DebalGhosh100/blocks

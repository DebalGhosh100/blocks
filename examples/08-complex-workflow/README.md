# Example 8: Complex Multi-Phase Workflow

## Overview
This example demonstrates a comprehensive, production-grade CI/CD workflow that combines all concepts from previous examples into a realistic enterprise deployment pipeline. It showcases the full power of Blocks for complex automation scenarios.

## What This Example Demonstrates
- ✅ Multi-phase workflow (Setup → Build → Test → Deploy → Monitor → Report)
- ✅ Mixed sequential and parallel execution
- ✅ Variable interpolation throughout the workflow
- ✅ Conditional logic and validation
- ✅ Parallel builds and tests
- ✅ Parallel multi-server deployment
- ✅ Health monitoring and verification
- ✅ Comprehensive reporting and logging
- ✅ Real-world CI/CD pipeline patterns

## Prerequisites
- Python 3.x installed
- Blocks framework installed
- Understanding of CI/CD concepts

## Directory Structure
```
08-complex-workflow/
├── main.yaml           # Complex multi-phase workflow
├── storage/            # Configuration files
│   └── config.yaml     # Workflow and server configuration
├── build/              # Created during execution
├── tests/              # Created during execution
├── logs/               # Created during execution
├── artifacts/          # Created during execution
└── README.md           # This file
```

## How to Run

```bash
# Clone this specific example
git clone --depth 1 --filter=blob:none --sparse https://github.com/DebalGhosh100/blocks.git
cd blocks
git sparse-checkout set examples/08-complex-workflow
cd examples/08-complex-workflow

# Run with one-command execution
curl -sSL https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.sh | bash
```

**What this does:**
1. Clones only this example directory (sparse checkout)
2. Downloads the Blocks framework automatically
3. Installs dependencies (paramiko, pyyaml)
4. Executes the complete 6-phase CI/CD pipeline
5. Cleans up framework files after completion

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: SETUP                           │
│  • Initialize project structure                              │
│  • Validate environment prerequisites                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2: BUILD                           │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Compile     │  │   Process    │  │   Generate      │  │
│  │   Source      │  │   Assets     │  │   Docs          │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│              (Parallel compilation phase)                    │
│                           │                                  │
│                           ▼                                  │
│                   Package Application                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 3: TESTING                         │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │    Unit       │  │ Integration  │  │  Performance    │  │
│  │    Tests      │  │   Tests      │  │  Tests          │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│              (Parallel test execution)                       │
│                           │                                  │
│                           ▼                                  │
│                    Generate Test Report                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 4: DEPLOYMENT                        │
│              Pre-deployment Validation                       │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Deploy      │  │   Deploy     │  │    Deploy       │  │
│  │  Server 1     │  │  Server 2    │  │   Server 3      │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│          (Parallel deployment to all servers)                │
│                           │                                  │
│                           ▼                                  │
│              Post-deployment Verification                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PHASE 5: MONITORING                        │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Health      │  │   Health     │  │    Health       │  │
│  │  Check S1     │  │  Check S2    │  │   Check S3      │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│          (Parallel health verification)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PHASE 6: REPORTING                        │
│  • Generate comprehensive workflow report                    │
│  • Display workflow statistics                              │
│  • Save artifacts and logs                                  │
└─────────────────────────────────────────────────────────────┘

Total Execution Time: ~30-35 seconds
Without Parallel Execution: ~100+ seconds
Time Saved: ~70% faster!
```

## Execution Timeline

```
Phase 1: Setup (Sequential)
  ├─ Initialize structure        [2s]
  └─ Validate environment         [2s]
                                 ────► 4s total

Phase 2: Build (Parallel + Sequential)
  ├─ Prepare environment          [1s]
  ├─ [Compile Sources]            [5s] ┐
  ├─ [Process Assets]             [4s] │ Parallel
  └─ [Generate Docs]              [2s] ┘
  └─ Package application          [1s]
                                 ────► 7s total (not 13s!)

Phase 3: Testing (Parallel + Sequential)
  ├─ Prepare test environment     [1s]
  ├─ [Unit Tests]                 [3s] ┐
  ├─ [Integration Tests]          [3s] │ Parallel
  └─ [Performance Tests]          [2s] ┘
  └─ Generate test report         [1s]
                                 ────► 5s total (not 11s!)

Phase 4: Deployment (Parallel + Sequential)
  ├─ Pre-deployment checks        [2s]
  ├─ [Deploy Server 1]            [5s] ┐
  ├─ [Deploy Server 2]            [5s] │ Parallel
  └─ [Deploy Server 3]            [5s] ┘
  └─ Post-deployment verify       [2s]
                                 ────► 9s total (not 19s!)

Phase 5: Monitoring (Parallel)
  ├─ [Health Check Server 1]      [2s] ┐
  ├─ [Health Check Server 2]      [2s] │ Parallel
  └─ [Health Check Server 3]      [2s] ┘
                                 ────► 2s total (not 6s!)

Phase 6: Reporting (Sequential)
  ├─ Generate workflow report     [2s]
  └─ Display summary              [1s]
                                 ────► 3s total

═══════════════════════════════════════
Total Time: ~30 seconds

Without Parallel Execution: 4+13+11+19+6+3 = 56+ seconds
With Parallel Execution: ~30 seconds
Performance Improvement: ~46% faster
═══════════════════════════════════════
```

## Phase-by-Phase Breakdown

### Phase 1: Environment Setup (Sequential)

Creates complete directory structure and validates prerequisites.

```yaml
- name: "Initialize Project Structure"
  run: |
    mkdir -p ./build/{src,dist,cache}
    mkdir -p ./tests/{unit,integration}
    mkdir -p ./logs/{build,test,deploy,monitoring}
    mkdir -p ./artifacts
```

**Why Sequential?**
- Must create directories before other phases use them
- Validation must complete before proceeding

### Phase 2: Build Stage (Mixed)

**Sequential Preparation:**
```yaml
- name: "Prepare Build Environment"
  run: |
    echo "Build Version: ${workflow.version}" > ./build/build_info.txt
```

**Parallel Execution:**
```yaml
- parallel:
    - name: "Compile Source Files"
    - name: "Process Assets"
    - name: "Generate Documentation"
```

**Why Parallel?**
- Compilation, asset processing, and docs are independent
- No shared resources or dependencies
- 3x speedup (5s instead of 12s)

**Sequential Finalization:**
```yaml
- name: "Build Package"
  run: |
    tar -czf artifacts/app_v${workflow.version}.tar.gz build/*
```

### Phase 3: Testing Stage (Mixed)

**Parallel Test Execution:**
```yaml
- parallel:
    - name: "Run Unit Tests"
      run: |
        # 50 unit tests
        # Check coverage threshold: ${workflow.test_coverage_min}%
    
    - name: "Run Integration Tests"
      run: |
        # 30 integration tests
    
    - name: "Run Performance Tests"
      run: |
        # Benchmark tests
```

**Why Parallel?**
- Test suites are independent
- Different test types can run simultaneously
- Significant time savings (3s instead of 8s)

**Why Coverage Check?**
- Uses conditional logic to validate ${workflow.test_coverage_min}
- Fails pipeline if coverage below threshold
- Production-grade quality gate

### Phase 4: Deployment Stage (Mixed)

**Pre-Deployment Validation:**
```yaml
- name: "Pre-Deployment Checks"
  run: |
    if [ ! -f ./artifacts/package.tar.gz ]; then
      exit 1
    fi
```

**Parallel Deployment:**
```yaml
- parallel:
    - name: "Deploy to Server 1"
      run: |
        # Backup → Upload → Extract → Configure
    - name: "Deploy to Server 2"
    - name: "Deploy to Server 3"
```

**Why Parallel?**
- Independent server deployments
- Zero coordination needed between servers
- 3x faster (5s instead of 15s)

**Post-Deployment Verification:**
```yaml
- name: "Post-Deployment Verification"
  run: |
    cat ./logs/deploy/server1.log
    cat ./logs/deploy/server2.log
    cat ./logs/deploy/server3.log
```

### Phase 5: Health Monitoring (Parallel)

```yaml
- parallel:
    - name: "Health Check - Server 1"
      run: |
        # Check HTTP, CPU, Memory, Response Time
    - name: "Health Check - Server 2"
    - name: "Health Check - Server 3"
```

**Why Parallel?**
- Health checks are independent
- Want real-time status of all servers
- 3x faster (2s instead of 6s)

### Phase 6: Final Reporting (Sequential)

```yaml
- name: "Generate Workflow Report"
  run: |
    # Aggregate all phase results
    # Create comprehensive report
    
- name: "Workflow Summary"
  run: |
    # Display statistics
    # Show artifacts created
```

**Why Sequential?**
- Report needs data from all previous phases
- Summary must be the final step

## Variable Interpolation Usage

This workflow uses variable interpolation extensively:

```yaml
workflow:
  name: "Enterprise CI/CD Pipeline"
  version: "2.5.3"
  build_number: "1025"
  environment: "production"
  test_coverage_min: 90

servers:
  prod1:
    ip: "10.0.1.10"
    user: "deploy"
```

**Used in workflow:**
- `${workflow.version}` - Build version number
- `${workflow.build_number}` - Unique build identifier
- `${workflow.environment}` - Environment type (production/staging/dev)
- `${workflow.test_coverage_min}` - Coverage threshold
- `${servers.prod1.ip}` - Server IP addresses
- `${servers.prod1.user}` - SSH username

## Conditional Logic Examples

### Environment-Based Behavior
```yaml
case $env_type in
  "production")
    echo "Strict validation enabled"
    ;;
  "staging")
    echo "Standard validation enabled"
    ;;
  *)
    echo "Minimal validation"
    ;;
esac
```

### Coverage Threshold Check
```yaml
if [ $coverage -ge ${workflow.test_coverage_min} ]; then
  echo "✓ Coverage meets threshold"
else
  echo "✗ Coverage below threshold"
  exit 1
fi
```

### Pre-Deployment Validation
```yaml
if [ -f ./artifacts/package.tar.gz ]; then
  echo "✓ Package found"
else
  echo "✗ Package not found"
  exit 1
fi
```

## Real-World Adaptations

### For Real SSH Deployment

Replace simulation with actual SSH commands:

```yaml
- name: "Deploy to Server 1"
  run: |
    # Upload package
    scp ./artifacts/app.tar.gz ${servers.prod1.user}@${servers.prod1.ip}:/tmp/
    
    # Deploy via SSH
    python3 ../../remotely.py \
      ${servers.prod1.user}@${servers.prod1.ip} \
      ${servers.prod1.password} \
      "cd /var/www && tar -xzf /tmp/app.tar.gz && systemctl restart app" \
      ./logs/deploy/server1.log
```

### For Database Migrations

Add a migration phase:

```yaml
- name: "Run Database Migration"
  run: |
    python3 ../../remotely.py \
      ${database.user}@${database.host} \
      ${database.password} \
      "cd /opt/migrations && ./migrate.sh --version ${workflow.version}" \
      ./logs/migration.log
```

### For Rollback Capability

Add rollback blocks:

```yaml
- name: "Create Rollback Point"
  run: |
    python3 ../../remotely.py ... \
      "cp -r /var/www/app /var/www/app.backup_${workflow.build_number}" \
      ./logs/backup.log

# If deployment fails:
- name: "Rollback Deployment"
  run: |
    python3 ../../remotely.py ... \
      "rm -rf /var/www/app && mv /var/www/app.backup_${workflow.build_number} /var/www/app" \
      ./logs/rollback.log
```

### For Slack/Email Notifications

Add notification blocks:

```yaml
- name: "Send Success Notification"
  run: |
    curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
      -H 'Content-Type: application/json' \
      -d "{
        \"text\": \"✓ Deployment ${workflow.version} successful!\"
      }"
```

## Generated Artifacts

After execution, the following artifacts are created:

```
./artifacts/
├── app_v2.5.3_build1025.tar.gz         # Deployment package
└── workflow_report_1025.txt            # Comprehensive report

./logs/
├── build/
│   ├── compile.log
│   ├── assets.log
│   └── docs.log
├── test/
│   ├── unit_tests.log
│   ├── integration_tests.log
│   └── performance.log
├── deploy/
│   ├── server1.log
│   ├── server2.log
│   └── server3.log
└── monitoring/
    ├── health_server1.log
    ├── health_server2.log
    └── health_server3.log
```

## Performance Optimization Strategies

### 1. Identify Independent Tasks
- Compilation, asset processing, docs → Parallel
- Unit, integration, performance tests → Parallel
- Server deployments → Parallel

### 2. Group Dependent Tasks
- Build → Test → Deploy → Monitor (Sequential phases)
- Prepare → Execute → Verify (Within each phase)

### 3. Minimize Sequential Bottlenecks
- Only use sequential when truly necessary
- Keep preparation steps minimal
- Parallelize wherever possible

## Key Takeaways

- Complex workflows benefit from careful phase design
- Parallel execution provides significant time savings (50%+ improvement)
- Variable interpolation enables configuration-driven workflows
- Conditional logic adds intelligence and validation
- Comprehensive logging enables troubleshooting
- This pattern scales to enterprise-level deployments

## Customization Guide

### Modify for Your Application

1. **Update build steps** to match your tech stack (Java, Node.js, Go, etc.)
2. **Customize test suites** for your testing framework
3. **Configure actual servers** in `storage/config.yaml`
4. **Add real SSH deployments** using `remotely.py`
5. **Integrate with CI/CD tools** (Jenkins, GitLab CI, GitHub Actions)

### Environment-Specific Configurations

Create multiple config files:

```
storage/
├── production.yaml
├── staging.yaml
└── development.yaml
```

Run with different configs:
```bash
python3 ../../blocks_executor.py main.yaml --storage ./storage_prod
python3 ../../blocks_executor.py main.yaml --storage ./storage_staging
```

## Next Steps

- Adapt this workflow for your project
- Add monitoring and alerting integrations
- Implement rollback capabilities
- Set up automated triggers (git hooks, cron)
- Integrate with your existing CI/CD pipeline

## Conclusion

This example demonstrates the full power of Blocks for orchestrating complex, production-grade workflows. By combining sequential coordination, parallel execution, variable interpolation, and conditional logic, you can build sophisticated automation pipelines that are both fast and maintainable.

---

**Congratulations!** You've completed all Blocks examples. You now have the knowledge to build powerful automation workflows for any scenario.

# Example 6: Data Processing Pipeline

## Overview
This example demonstrates a multi-stage data processing pipeline with parallel processing stages. It simulates a real-world ETL (Extract, Transform, Load) workflow with data ingestion, parallel processing, and report generation.

## What This Example Demonstrates
- ✅ Multi-stage data pipeline (Ingest → Process → Analyze → Report)
- ✅ Parallel data processing for independent datasets
- ✅ Sequential coordination between pipeline stages
- ✅ Data validation and transformation
- ✅ Report generation and aggregation
- ✅ Pipeline statistics and monitoring

## Prerequisites
- Python 3.x installed
- Blocks framework installed
- Basic understanding of data pipelines

## Directory Structure
```
06-data-pipeline/
├── main.yaml           # Pipeline workflow definition
├── storage/            # Configuration files
│   └── config.yaml     # Pipeline configuration
├── data/               # Created during execution
│   ├── raw/           # Raw input data
│   ├── processed/     # Processed data
│   └── output/        # Final reports
└── README.md           # This file
```

## How to Run

```bash
# Navigate to this example
cd blocks/examples/06-data-pipeline

# Run the pipeline
python3 ../../blocks_executor.py main.yaml
```

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STAGE 1: SETUP                       │
│         Create directories and prepare environment       │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 STAGE 2: DATA INGESTION                 │
│           Fetch/generate raw data from sources           │
│        (Weather, Sales, Activity datasets)               │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              STAGE 3: PARALLEL PROCESSING               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Process    │  │   Process    │  │   Process    │  │
│  │   Weather    │  │    Sales     │  │   Activity   │  │
│  │     Data     │  │     Data     │  │     Data     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         (All three run simultaneously)                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  STAGE 4: VERIFICATION                  │
│         Verify all processing completed successfully     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│            STAGE 5: PARALLEL REPORT GENERATION          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Weather    │  │    Sales     │  │   Activity   │  │
│  │    Report    │  │    Report    │  │    Report    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         (All three reports generated in parallel)        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│               STAGE 6: MASTER REPORT                    │
│      Combine all reports into single master report       │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  STAGE 7: DISPLAY & STATS               │
│           Show results and pipeline statistics           │
└─────────────────────────────────────────────────────────┘
```

## Expected Output

### Stage 1-2: Setup & Data Ingestion
Creates directory structure and generates 3 CSV datasets:
- `weather.csv` - 100 weather records
- `sales.csv` - 100 sales transactions
- `activity.csv` - 100 user activity records

### Stage 3: Parallel Processing
Processes all 3 datasets **simultaneously**:
- Validates data integrity
- Removes invalid entries
- Transforms data formats
- Saves to processed directory

**Time Advantage**: If each processing task takes 10 seconds:
- Sequential: 30 seconds
- Parallel: 10 seconds (3x faster!)

### Stage 4: Verification
Confirms all processing completed successfully with file listings and log checks.

### Stage 5: Parallel Report Generation
Generates 3 analysis reports **simultaneously**:
- Weather analysis with temperature averages
- Sales analysis with transaction totals
- Activity analysis with user counts

### Stage 6-7: Master Report & Statistics
Combines all reports into a master summary and displays pipeline statistics.

## Workflow Breakdown

### Stage 1: Setup Pipeline Environment
```yaml
- name: "Setup Pipeline Environment"
  run: |
    mkdir -p ${pipeline.paths.raw_data}
    mkdir -p ${pipeline.paths.processed_data}
    mkdir -p ${pipeline.paths.output}
```
Uses variable interpolation to create standardized directory structure.

### Stage 2: Fetch Raw Data
```yaml
- name: "Fetch Raw Data"
  run: |
    echo "Dataset 1: Weather data" > ${pipeline.paths.raw_data}/weather.csv
    for i in {1..100}; do
      echo "2024-01-$i,25.$i,60.$i" >> ${pipeline.paths.raw_data}/weather.csv
    done
```
Generates sample datasets. In production, this would fetch from APIs, databases, or file systems.

### Stage 3: Parallel Processing
```yaml
- parallel:
    - name: "Process Weather Data"
      run: |
        input="${pipeline.paths.raw_data}/weather.csv"
        output="${pipeline.paths.processed_data}/weather_processed.csv"
        # Data validation and transformation
        
    - name: "Process Sales Data"
      run: |
        input="${pipeline.paths.raw_data}/sales.csv"
        output="${pipeline.paths.processed_data}/sales_processed.csv"
        # Data validation and transformation
```

Each processor:
1. Reads raw data
2. Validates entries
3. Filters invalid records
4. Transforms format
5. Writes to processed directory
6. Logs completion status

### Stage 5: Parallel Report Generation
```yaml
- parallel:
    - name: "Generate Weather Report"
      run: |
        # Calculate statistics
        record_count=$(tail -n +2 $input | wc -l)
        avg_temp=$(tail -n +2 $input | cut -d',' -f2 | awk '{sum+=$1} END {print sum/NR}')
```

Performs analysis and generates formatted reports with:
- Record counts
- Statistical calculations (averages, totals)
- Sample data preview

### Stage 6: Master Report Generation
```yaml
- name: "Generate Master Report"
  run: |
    # Combine all individual reports
    cat ${pipeline.paths.output}/weather_report.txt >> $master
    cat ${pipeline.paths.output}/sales_report.txt >> $master
    cat ${pipeline.paths.output}/activity_report.txt >> $master
```

Aggregates all individual reports into a comprehensive master report.

## Configuration File

```yaml
pipeline:
  name: "Multi-Stage Data Processing Pipeline"
  version: "1.0.0"
  
  paths:
    raw_data: "./data/raw"
    processed_data: "./data/processed"
    output: "./data/output"
  
  settings:
    batch_size: 1000
    parallel_jobs: 3
    retry_count: 3
```

All paths are configurable via variable interpolation, making the pipeline portable and reusable.

## Real-World Use Cases

### 1. ETL Pipeline
```yaml
blocks:
  - name: "Extract from multiple sources"
    run: |
      # Pull from database
      psql -c "COPY table TO '${pipeline.paths.raw_data}/db_export.csv'"
      # Pull from API
      curl https://api.example.com/data > ${pipeline.paths.raw_data}/api_data.json

  - parallel:
      - name: "Transform DB data"
      - name: "Transform API data"
  
  - name: "Load to warehouse"
```

### 2. Log Processing Pipeline
```yaml
blocks:
  - parallel:
      - name: "Collect logs from Server 1"
        run: |
          python3 ../../remotely.py ${servers.web1.user}@${servers.web1.ip} ... \
            "cat /var/log/app.log" \
            ${pipeline.paths.raw_data}/server1.log
      
      - name: "Collect logs from Server 2"
        # Similar for other servers
  
  - parallel:
      - name: "Parse Server 1 logs"
      - name: "Parse Server 2 logs"
  
  - name: "Aggregate and analyze"
```

### 3. Machine Learning Pipeline
```yaml
blocks:
  - name: "Data Collection"
  
  - parallel:
      - name: "Feature Engineering - Dataset A"
      - name: "Feature Engineering - Dataset B"
      - name: "Feature Engineering - Dataset C"
  
  - name: "Combine Features"
  
  - parallel:
      - name: "Train Model 1"
      - name: "Train Model 2"
      - name: "Train Model 3"
  
  - name: "Model Evaluation and Selection"
```

### 4. Image Processing Pipeline
```yaml
blocks:
  - name: "Download Images"
  
  - parallel:
      - name: "Resize Images"
      - name: "Apply Filters"
      - name: "Generate Thumbnails"
  
  - name: "Upload Processed Images"
```

## Pipeline Patterns

### Pattern 1: Fan-Out, Fan-In
```
Single Input → Multiple Parallel Processors → Single Aggregator
```
Used in this example for data processing.

### Pattern 2: Sequential Stages
```
Stage 1 → Stage 2 → Stage 3 → Stage 4
```
Each stage must complete before the next begins.

### Pattern 3: Conditional Processing
```yaml
- name: "Check Data Quality"
  run: |
    if [ quality_score -gt 80 ]; then
      echo "Proceed"
    else
      echo "Skip processing"
    fi
```

### Pattern 4: Retry Logic
```yaml
- name: "Process with Retry"
  run: |
    for i in 1 2 3; do
      if process_data.sh; then
        break
      else
        echo "Retry $i of 3"
        sleep 5
      fi
    done
```

## Performance Optimization

### Parallel Processing Benefits
- **3 processors, 10 seconds each**:
  - Sequential: 30 seconds
  - Parallel: 10 seconds
  - Speedup: 3x

- **10 processors, 5 seconds each**:
  - Sequential: 50 seconds
  - Parallel: 5 seconds
  - Speedup: 10x

### When to Use Parallel Processing
✅ Independent data chunks
✅ Multiple data sources
✅ CPU-intensive transformations
✅ I/O-bound operations (network, disk)

### When to Use Sequential Processing
✅ Data dependencies between stages
✅ Shared resource constraints
✅ Order-dependent operations

## Monitoring and Debugging

### View Processing Logs
```bash
cat ./logs/weather_process.log
cat ./logs/sales_process.log
cat ./logs/activity_process.log
```

### Check Data Quality
```bash
# Count records in processed files
wc -l ./data/processed/*.csv

# View sample records
head -n 10 ./data/processed/weather_processed.csv
```

### Monitor Disk Usage
```bash
du -sh ./data/*
```

## Key Takeaways
- Data pipelines benefit greatly from parallel processing
- Sequential stages ensure proper coordination between pipeline phases
- Variable interpolation makes pipelines configurable and portable
- Logging and verification stages are critical for production pipelines
- The framework handles complex multi-stage workflows elegantly

## Next Steps
- Adapt this pipeline for your own data sources
- Add error handling and retry logic
- Implement data quality checks
- Explore the next example: **07-conditional-logic**

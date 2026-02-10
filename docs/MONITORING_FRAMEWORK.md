# Enterprise-Grade Monitoring Framework

## 🎯 Overview

This monitoring framework implements **structured JSON logging** across the entire pipeline, enabling machine-readable logs that can be ingested by CloudWatch, Elasticsearch, or Splunk without modification.

## 🏗️ Architecture: Three-Layer Safety Net

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING LAYERS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Local Scripts (Generation/Export)                 │
│  ├─ File I/O validation                                     │
│  ├─ Permission checks                                       │
│  └─ Google Drive sync monitoring                            │
│                                                              │
│  Layer 2: Fivetran (Black Box)                              │
│  ├─ Monitor S3 arrival (result-based)                       │
│  ├─ File count validation                                   │
│  └─ Timestamp checks                                        │
│                                                              │
│  Layer 3: Databricks (Processing)                           │
│  ├─ Mount validation                                        │
│  ├─ Input data validation (Circuit Breaker)                 │
│  ├─ Spark job monitoring                                    │
│  └─ Data quality checks                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Components

### 1. Core Logger (`src/utils/logger.py`)

**Purpose**: Centralized structured logging utility

**Features**:
- JSON-formatted output (machine-readable)
- Automatic timestamp (UTC)
- Component identification
- Exception stack traces
- File and line number tracking

**Usage**:
```python
from src.utils.logger import get_logger

log = get_logger("MyComponent")
log.info("Operation started")
log.error("Operation failed", exc_info=True)
```

**Output Example**:
```json
{
  "timestamp": "2026-02-10T05:40:20.123456",
  "level": "INFO",
  "component": "ExportService",
  "message": "Successfully copied file",
  "file": "prepare_for_fivetran.py",
  "line": 42
}
```

### 2. Hardened Export Script (`src/export/prepare_for_fivetran.py`)

**Monitoring Features**:
- ✅ File existence validation
- ✅ Permission error handling
- ✅ Atomic copy operations
- ✅ Structured logging
- ✅ Non-zero exit codes on failure
- ✅ Alert pattern for grep filtering

**Critical Patterns**:
```python
# Fail Fast: Validate before processing
if not os.path.exists(src):
    log.error(f"Source file missing: {src}")
    raise FileNotFoundError(f"{src} not found")

# Alert Pattern: Grepable alerts
except Exception as e:
    log.critical("Pipeline Halted", exc_info=True)
    print(f"!! ALERT: EXPORT PIPELINE FAILURE !! - {str(e)}")
    exit(1)  # Non-zero exit for CI/CD
```

### 3. Hardened ETL Job (`src/processing/etl_job.py`)

**Monitoring Features**:
- ✅ Spark session initialization logging
- ✅ Input path validation
- ✅ Row count tracking
- ✅ Empty dataset detection
- ✅ Transformation logging
- ✅ Output path logging
- ✅ Graceful shutdown

**Key Improvements**:
```python
# Input Validation
if not os.path.exists(RAW_LEASE_PATH):
    log.error(f"Lease path not found: {RAW_LEASE_PATH}")
    raise FileNotFoundError(f"Missing directory: {RAW_LEASE_PATH}")

# Data Quality Check
if row_count == 0:
    log.warning("No lease documents found. Skipping processing.")
    return

# Comprehensive Error Handling
except Exception as e:
    log.critical("ETL Job Failed", exc_info=True)
    print(f"!! ALERT: ETL PIPELINE FAILURE !! - {str(e)}")
    exit(1)
```

### 4. Databricks Notebook (`notebooks/03_S3_to_Databricks_Monitored.py`)

**Monitoring Features**:
- ✅ Mount validation (IAM permission checks)
- ✅ Circuit Breaker pattern (fail fast on no data)
- ✅ Input data validation
- ✅ Row count tracking
- ✅ Data quality checks
- ✅ Graceful job exit
- ✅ Structured JSON logging

**Critical Patterns**:
```python
# Mount Validation
def strict_mount_check(mount_point):
    try:
        files = dbutils.fs.ls(mount_point)
        log_json("INFO", "Mount check passed", file_count=len(files))
    except Exception as e:
        log_json("CRITICAL", "Mount check failed", error=str(e))
        print(f"!! ALERT: MOUNT FAILURE !! - {mount_point}")
        raise e

# Circuit Breaker: Don't process empty data
if not validate_input_data(INPUT_PATH, min_files=1):
    log_json("WARNING", "Job skipped - no data")
    dbutils.notebook.exit("SKIPPED_NO_DATA")

# Data Quality Check
if row_count == 0:
    log_json("ERROR", "Data quality failure", issue="ZERO_ROWS")
    raise ValueError("Empty dataset detected")
```

## 🚨 Alert Patterns

### Grepable Alerts
All critical failures include a grepable alert pattern:

```bash
# Monitor logs for failures
tail -f pipeline.log | grep "!! ALERT"

# Example output:
!! ALERT: EXPORT PIPELINE FAILURE !! - Permission denied
!! ALERT: ETL PIPELINE FAILURE !! - FileNotFoundError
!! ALERT: DATABRICKS ETL FAILURE !! - Mount check failed
!! ALERT: MOUNT FAILURE !! - /mnt/jhb_datalake
```

### Exit Codes
All scripts use proper exit codes for CI/CD integration:

- `exit(0)`: Success
- `exit(1)`: Failure (triggers alerts in schedulers)

## 📊 Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **INFO** | Normal operations | "ETL Job Starting", "Loaded 1000 rows" |
| **WARNING** | Recoverable issues | "No new data found", "Skipping empty file" |
| **ERROR** | Operation failures | "File not found", "Permission denied" |
| **CRITICAL** | Pipeline halted | "ETL Job Failed", "Mount check failed" |

## 🔍 Monitoring Queries

### CloudWatch Insights (if logs are shipped to AWS)

```sql
-- Find all failures in last hour
fields @timestamp, component, message, error
| filter level = "CRITICAL"
| sort @timestamp desc
| limit 100

-- Track row counts processed
fields @timestamp, component, row_count
| filter message like /rows processed/
| stats sum(row_count) by bin(5m)

-- Monitor mount failures
fields @timestamp, mount_point, error
| filter message like /Mount check failed/
| sort @timestamp desc
```

### Local Log Analysis

```bash
# Count errors by component
cat pipeline.log | jq -r 'select(.level=="ERROR") | .component' | sort | uniq -c

# Extract all critical failures
cat pipeline.log | jq -r 'select(.level=="CRITICAL") | {timestamp, component, message, error}'

# Monitor specific component
cat pipeline.log | jq -r 'select(.component=="DatabricksETL")'

# Track processing metrics
cat pipeline.log | jq -r 'select(.row_count) | {timestamp, component, row_count}'
```

## 🎯 Best Practices Implemented

### 1. Fail Fast
- Validate inputs before processing
- Check file existence before reading
- Verify mount access before querying

### 2. Structured Logging
- JSON format for machine parsing
- Consistent field names
- UTC timestamps

### 3. Context Preservation
- Component identification
- File and line numbers
- Full exception stack traces

### 4. Graceful Degradation
- Skip empty datasets (don't fail)
- Log warnings for missing optional data
- Exit cleanly with proper codes

### 5. Alerting Integration
- Grepable alert patterns
- Non-zero exit codes
- Critical log level for failures

## 🚀 Usage Examples

### Running with Monitoring

```bash
# Local ETL with log capture
python src/processing/etl_job.py 2>&1 | tee pipeline.log

# Export with monitoring
python src/export/prepare_for_fivetran.py 2>&1 | tee export.log

# Monitor for failures in real-time
tail -f pipeline.log | grep -E "(ERROR|CRITICAL|ALERT)"

# Parse JSON logs
cat pipeline.log | jq -r 'select(.level=="ERROR")'
```

### Cron Job Integration

```bash
# Add to crontab with logging
0 2 * * * cd /path/to/project && python src/processing/etl_job.py >> /var/log/etl.log 2>&1 || echo "ETL Failed" | mail -s "Pipeline Alert" admin@example.com
```

### Airflow Integration

```python
from airflow.operators.bash import BashOperator

etl_task = BashOperator(
    task_id='run_etl',
    bash_command='python src/processing/etl_job.py',
    # Airflow automatically captures exit codes
    # Non-zero exit triggers failure state
)
```

## 📈 Metrics to Track

### Pipeline Health
- ✅ Job success rate
- ✅ Average execution time
- ✅ Row counts processed
- ✅ Error frequency by component

### Data Quality
- ✅ Empty dataset occurrences
- ✅ Null value percentages
- ✅ Schema validation failures
- ✅ Duplicate record counts

### Infrastructure
- ✅ Mount availability
- ✅ File system errors
- ✅ Permission issues
- ✅ Spark job failures

## 🔧 Troubleshooting

### Common Issues

**Issue**: Logs not appearing
```bash
# Check Python logging configuration
export PYTHONUNBUFFERED=1
python src/processing/etl_job.py
```

**Issue**: JSON parsing errors
```bash
# Validate JSON format
cat pipeline.log | jq empty
```

**Issue**: Missing stack traces
```python
# Ensure exc_info=True is set
log.error("Operation failed", exc_info=True)
```

## 📚 Next Steps

### Immediate Improvements
1. Ship logs to CloudWatch or Elasticsearch
2. Set up email/Slack alerts for CRITICAL logs
3. Create dashboards for key metrics
4. Implement log rotation

### Advanced Monitoring
1. Add distributed tracing (OpenTelemetry)
2. Implement custom metrics (Prometheus)
3. Set up anomaly detection
4. Create SLA monitoring

## 🎓 Interview Talking Points

1. **Structured Logging**: "I implemented JSON logging for machine-readable logs"
2. **Fail Fast**: "Input validation prevents wasting compute on bad data"
3. **Circuit Breaker**: "Graceful degradation when upstream data is missing"
4. **Observability**: "Full stack traces and context for debugging"
5. **Production-Ready**: "Non-zero exit codes for CI/CD integration"
6. **Cost Optimization**: "Fail fast saves Databricks cluster costs"

---

**Status**: ✅ Production-Ready  
**Coverage**: Local Scripts + Databricks  
**Format**: JSON (CloudWatch/Elasticsearch compatible)  
**Alert Method**: Grepable patterns + Exit codes

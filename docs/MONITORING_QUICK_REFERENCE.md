# Monitoring Quick Reference

## 🚀 Quick Start

### 1. Run with Monitoring
```bash
# ETL Job
python src/processing/etl_job.py 2>&1 | tee logs/etl_$(date +%Y%m%d_%H%M%S).log

# Export Job
python src/export/prepare_for_fivetran.py 2>&1 | tee logs/export_$(date +%Y%m%d_%H%M%S).log
```

### 2. Monitor in Real-Time
```bash
# Watch for failures
tail -f logs/etl_*.log | grep -E "(ERROR|CRITICAL|ALERT)"

# Parse JSON logs
tail -f logs/etl_*.log | jq -r 'select(.level=="ERROR")'
```

### 3. Analyze Logs
```bash
# Count errors by component
cat logs/etl_*.log | jq -r 'select(.level=="ERROR") | .component' | sort | uniq -c

# Extract critical failures
cat logs/etl_*.log | jq -r 'select(.level=="CRITICAL")'

# Track row counts
cat logs/etl_*.log | jq -r 'select(.row_count) | {component, row_count}'
```

## 📊 Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `INFO` | Normal operations | "Job started", "Loaded 1000 rows" |
| `WARNING` | Recoverable issues | "No data found", "Skipping file" |
| `ERROR` | Operation failed | "File not found", "Read failed" |
| `CRITICAL` | Pipeline halted | "Job failed", "Mount unavailable" |

## 🚨 Alert Patterns

All critical failures include grepable alerts:

```bash
!! ALERT: EXPORT PIPELINE FAILURE !!
!! ALERT: ETL PIPELINE FAILURE !!
!! ALERT: DATABRICKS ETL FAILURE !!
!! ALERT: MOUNT FAILURE !!
```

**Monitor alerts**:
```bash
tail -f logs/*.log | grep "!! ALERT"
```

## 📝 Log Format

```json
{
  "timestamp": "2026-02-10T05:40:20.123456",
  "level": "INFO",
  "component": "ETLJob",
  "message": "Processing started",
  "file": "etl_job.py",
  "line": 42
}
```

## 🔍 Common Queries

### Find all failures today
```bash
cat logs/etl_$(date +%Y%m%d)*.log | jq -r 'select(.level=="ERROR" or .level=="CRITICAL")'
```

### Count operations by component
```bash
cat logs/*.log | jq -r '.component' | sort | uniq -c
```

### Extract exception stack traces
```bash
cat logs/*.log | jq -r 'select(.exception) | {timestamp, component, exception}'
```

### Monitor specific component
```bash
cat logs/*.log | jq -r 'select(.component=="DatabricksETL")'
```

## 🎯 Exit Codes

- `0` = Success
- `1` = Failure (triggers CI/CD alerts)

**Check last exit code**:
```bash
echo $?
```

## 📁 File Structure

```
jhb-realestate-pipeline/
├── src/
│   ├── utils/
│   │   └── logger.py              # Core logging utility
│   ├── export/
│   │   └── prepare_for_fivetran.py  # Monitored export
│   └── processing/
│       └── etl_job.py             # Monitored ETL
├── notebooks/
│   └── 03_S3_to_Databricks_Monitored.py  # Databricks monitoring
├── logs/                          # Log output directory
└── docs/
    └── MONITORING_FRAMEWORK.md    # Full documentation
```

## 🛠️ Troubleshooting

### Logs not appearing?
```bash
export PYTHONUNBUFFERED=1
python src/processing/etl_job.py
```

### JSON parsing errors?
```bash
# Validate JSON
cat logs/etl.log | jq empty
```

### Missing stack traces?
```python
# Use exc_info=True
log.error("Failed", exc_info=True)
```

## 📚 Documentation

- **Full Guide**: [docs/MONITORING_FRAMEWORK.md](MONITORING_FRAMEWORK.md)
- **Architecture**: [docs/ENTERPRISE_ARCHITECTURE.md](ENTERPRISE_ARCHITECTURE.md)
- **Setup**: [README.md](../README.md)

---

**Quick Help**: `cat docs/MONITORING_QUICK_REFERENCE.md`

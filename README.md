# 🏢 Johannesburg Real Estate Data Lakehouse

**Production-grade, $0-cost data pipeline demonstrating enterprise architecture patterns**

[![License](https://img.shields.io/badge/license-Educational-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PySpark](https://img.shields.io/badge/pyspark-3.5.0-orange.svg)](https://spark.apache.org/)

---

## 🎯 Overview

Modern **data lakehouse** processing Johannesburg real estate data with:
- **Medallion Architecture** (Bronze → Silver → Gold)
- **Decoupled Storage & Compute** (S3 + Databricks)
- **Enterprise Monitoring** (Structured JSON logging)
- **$0.00/month** (Free Tier only)

**Stack**: Python | PySpark | AWS S3 | Databricks | Delta Lake | Fivetran

---

## 🏗️ Architecture

```
Google Drive → Fivetran → AWS S3 (Bronze/Silver/Gold) → Databricks → Analytics
```

### Why This Design?

**Decoupled & Event-Driven**
- No Airflow needed (Fivetran handles scheduling)
- Serverless (no EC2 = $0 compute)
- Independent scaling

**Frugal Engineering**
- $0.00/month using Free Tiers
- Production patterns without production costs
- No vendor lock-in (standard formats)

**Enterprise-Grade**
- Structured JSON logging (CloudWatch-ready)
- Fail-fast pattern (saves compute)
- Full observability

[View Architecture Diagrams →](generated-diagrams/)

---

## ✨ Features

### Data Engineering
✅ Medallion architecture (Bronze/Silver/Gold)  
✅ Partition optimization (10-100x speedup)  
✅ Native Spark functions (no UDFs)  
✅ Delta Lake ready (ACID transactions)

### Monitoring
✅ Structured JSON logging  
✅ Three-layer safety net  
✅ Fail-fast pattern  
✅ Circuit breaker

### Cost
✅ $0.00/month  
✅ S3 lifecycle policies  
✅ Free Tier monitoring

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Java JDK 17
- AWS Account (Free Tier)
- Databricks Community Edition

### Install
```bash
git clone <repo-url>
cd jhb-realestate-pipeline
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Run Locally
```bash
# Generate data
python src/ingestion/generate_mock_data.py

# Run ETL
python src/processing/etl_job.py 2>&1 | tee logs/etl.log

# Generate insights
python src/analysis/generate_insights.py
```

### Deploy to Cloud
See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

## 📁 Structure

```
├── src/
│   ├── utils/logger.py              # Structured logging
│   ├── ingestion/generate_mock_data.py
│   ├── export/prepare_for_fivetran.py
│   ├── processing/etl_job.py        # PySpark ETL
│   └── analysis/generate_insights.py
├── notebooks/
│   ├── 01_ETL_Pipeline.py
│   ├── 02_Analytics_Dashboard.py
│   └── 03_S3_to_Databricks_Monitored.py
├── infrastructure/aws/
│   └── s3-datalake-stack.yaml       # CloudFormation
├── docs/
│   ├── DEPLOYMENT_GUIDE.md          # Step-by-step setup
│   ├── MONITORING_FRAMEWORK.md      # Monitoring guide
│   └── DATABRICKS_SETUP.md
└── generated-diagrams/              # Architecture visuals
```

---

## 🎓 Key Insights

1. **Compliance Audit**: % non-compliant leases
2. **Top Suburbs**: By price per sqm
3. **Luxury Market**: Premium properties (>R3m)
4. **Sales Volume**: Regional activity

---

## 🔍 Monitoring

### Structured Logs
```json
{
  "timestamp": "2026-02-10T06:03:28Z",
  "level": "INFO",
  "component": "ETLJob",
  "message": "Processing completed",
  "row_count": 1000
}
```

### Real-Time
```bash
tail -f logs/etl.log | grep -E "(ERROR|CRITICAL|ALERT)"
cat logs/etl.log | jq -r 'select(.level=="ERROR")'
```

[Full Monitoring Guide →](docs/MONITORING_FRAMEWORK.md)

---

## 💰 Cost

| Component | Cost | Free Tier | Status |
|-----------|------|-----------|--------|
| Databricks | $0 | Community | ✅ |
| AWS S3 | $0.023/GB | 5GB | ✅ |
| Fivetran | $0 | 14-day trial | ⚠️ |
| Google Drive | $0 | 15GB | ✅ |
| **Total** | **$0.00/month** | | ✅ |

---

## 🛠️ Technical Highlights

**Performance**
- Parquet: 10-100x I/O reduction
- Partition pruning: Selective scanning
- Native functions: 10-100x faster than UDFs

**Code Example**
```python
# Compliance check (native Spark)
df.withColumn("compliance_status", 
    when((col("body").contains("defect disclosure")) & 
         (col("body").contains("fica")), 
         "COMPLIANT").otherwise("NON_COMPLIANT"))
```

**Monitoring Example**
```python
from src.utils.logger import get_logger

log = get_logger("ETLJob")
log.info("Processing started")
try:
    # ... processing
    log.info("Completed", row_count=1000)
except Exception as e:
    log.critical("Failed", exc_info=True)
    exit(1)
```

---

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - AWS + Databricks setup
- **[Monitoring](docs/MONITORING_FRAMEWORK.md)** - Enterprise monitoring
- **[Architecture](generated-diagrams/)** - Visual diagrams
- **[Quick Reference](docs/MONITORING_QUICK_REFERENCE.md)** - Cheat sheet

---

## 🎯 Interview Points

1. **Medallion Architecture**: Industry-standard (Databricks, AWS, Azure)
2. **Decoupled Design**: Storage ≠ compute (no vendor lock-in)
3. **Structured Logging**: CloudWatch/Elasticsearch compatible
4. **Fail-Fast Pattern**: Saves compute costs
5. **$0.00/month**: Frugal engineering

---

## 🔧 Troubleshooting

**Java not found**
```bash
winget install Microsoft.OpenJDK.17
```

**Hadoop binaries (Windows)**
Download: https://github.com/cdarlint/winutils  
Place in: `hadoop/bin/`

**Logs not appearing**
```bash
export PYTHONUNBUFFERED=1
```

---

## 📄 License

Educational/Portfolio use

---

## 🙏 Acknowledgments

- AWS EMR patterns
- Databricks best practices
- Apache Spark docs

---

**Built with ❤️ demonstrating production-grade, frugal data engineering**

[Architecture](generated-diagrams/) | [Monitoring](docs/MONITORING_FRAMEWORK.md) | [Deploy](docs/DEPLOYMENT_GUIDE.md)

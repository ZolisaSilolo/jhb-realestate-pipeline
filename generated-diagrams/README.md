# Architecture Diagrams

**Last Updated**: February 10, 2026  
**Total Diagrams**: 6 PNG files

---

## 📊 Available Diagrams

### 1. Enterprise Architecture (`01_enterprise_architecture.png`)
**Shows**: Complete cloud pipeline from Google Drive to Analytics

**Components**:
- Google Drive (15GB free)
- Fivetran (14-day trial)
- AWS S3 (Bronze/Silver/Gold with lifecycle policies)
- Databricks Community Edition (free)
- Analytics Dashboard

**Use For**: Executive presentations, project overview

---

### 2. Local Development (`02_local_development.png`)
**Shows**: Local development workflow and testing

**Components**:
- Python 3.12 + PySpark 3.5
- Mock data generation (Faker)
- Bronze → Silver → Gold layers (local)
- ETL job with structured logging
- Analytics generation

**Use For**: Developer onboarding, local setup

---

### 3. Medallion Architecture (`03_medallion_architecture.png`)
**Shows**: Three-tier data architecture pattern

**Layers**:
- **Bronze**: Raw data, immutable, 30-day lifecycle
- **Silver**: Processed Parquet, cleaned, 90-day lifecycle
- **Gold**: Aggregated insights, IA storage after 30 days

**Use For**: Technical interviews, architecture discussions

---

### 4. Monitoring Architecture (`04_monitoring_architecture.png`)
**Shows**: Enterprise monitoring framework

**Components**:
- Structured JSON logging (all scripts)
- logger.py utility (JSON formatter)
- Local log storage (CloudWatch-ready)
- Databricks monitoring (circuit breaker, mount validation)
- Optional CloudWatch integration

**Use For**: DevOps discussions, observability demos

---

### 5. Infrastructure as Code (`05_infrastructure.png`)
**Shows**: CloudFormation stack and IAM setup

**Components**:
- CloudFormation template (s3-datalake-stack.yaml)
- S3 bucket with lifecycle policies
- IAM role for Databricks (AssumeRole)
- IAM user for Fivetran (Access Keys)
- Least privilege permissions

**Use For**: Infrastructure discussions, security reviews

---

### 6. Complete Data Flow (`06_complete_flow.png`)
**Shows**: End-to-end data pipeline

**Flow**:
1. Python + Faker → Generate mock data
2. Local PySpark ETL → Process to Parquet
3. Export script → Prepare for cloud
4. Google Drive → Fivetran → S3
5. Databricks → Process in cloud

**Use For**: Walkthrough demos, full pipeline explanation

---

## 🎨 Design Principles

### Color Coding
- **Blue**: Compute/Processing (Python, Spark, Databricks)
- **Orange**: Storage (S3, local files)
- **Green**: Analytics/Output
- **Red**: Security (IAM, CloudWatch)

### Layout
- **Direction**: Left-to-right (LR) or Top-to-bottom (TB)
- **Grouping**: Clusters for related components
- **Labels**: Clear edge labels showing data flow

---

## 📐 Technical Details

### File Format
- **Format**: PNG (high-resolution)
- **Size**: 96-146 KB per diagram
- **Resolution**: Optimized for presentations and documentation

### Generation
- **Tool**: Python `diagrams` library
- **Icons**: AWS official icons + on-premise icons
- **Regeneration**: Run diagram generation scripts in project root

---

## 🎯 Usage Guide

### For Presentations
**Recommended**: `01_enterprise_architecture.png`
- Shows complete cloud pipeline
- Easy to understand for non-technical audience

### For Technical Interviews
**Recommended**: `03_medallion_architecture.png`
- Demonstrates industry-standard pattern
- Shows data quality progression

### For Code Reviews
**Recommended**: `04_monitoring_architecture.png`
- Shows observability implementation
- Demonstrates production-ready practices

### For Infrastructure Discussions
**Recommended**: `05_infrastructure.png`
- Shows CloudFormation setup
- Demonstrates IaC best practices

---

## 🔄 Updating Diagrams

To regenerate diagrams:

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3
# ... (see diagram generation code in project)
```

Or use the diagram generation scripts in the project root.

---

## 📚 Related Documentation

- [README.md](../README.md) - Project overview
- [DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md) - Setup instructions
- [MONITORING_FRAMEWORK.md](../docs/MONITORING_FRAMEWORK.md) - Monitoring details
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Current status

---

## 🎓 Interview Tips

### Diagram Walkthrough (5 minutes)
1. **Start with Enterprise Architecture** (1 min)
   - "This shows the complete cloud pipeline"
   - Point out $0/month cost optimization

2. **Show Medallion Architecture** (2 min)
   - "I implemented Bronze/Silver/Gold layers"
   - Explain data quality progression

3. **Highlight Monitoring** (1 min)
   - "I added structured JSON logging"
   - Show fail-fast and circuit breaker patterns

4. **Discuss Infrastructure** (1 min)
   - "I used CloudFormation for IaC"
   - Explain IAM least privilege

### Key Talking Points
- "Medallion architecture is industry-standard (Databricks, AWS, Azure)"
- "Decoupled design prevents vendor lock-in"
- "Structured logging enables CloudWatch integration"
- "$0/month demonstrates frugal engineering"

---

**Total Diagrams**: 6  
**Total Size**: ~713 KB  
**Status**: ✅ Production-ready

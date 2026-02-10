# Databricks Integration Guide

## Overview
This guide explains how to migrate your local PySpark pipeline to Databricks Community Edition.

## Prerequisites
1. Databricks Community Edition account (free): https://community.cloud.databricks.com/
2. Your processed data files or raw data files

## Setup Steps

### 1. Upload Data to DBFS (Databricks File System)

**Option A: Using Databricks UI**
1. Log into Databricks workspace
2. Click "Data" in the left sidebar
3. Click "Create Table" → "Upload File"
4. Upload your files to these paths:
   - Raw contracts: `/FileStore/jhb-realestate/raw/contracts/`
   - Raw market data: `/FileStore/jhb-realestate/raw/market_data/`

**Option B: Using Databricks CLI**
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Upload data
databricks fs cp data/raw/contracts/ dbfs:/FileStore/jhb-realestate/raw/contracts/ --recursive
databricks fs cp data/raw/market_data/ dbfs:/FileStore/jhb-realestate/raw/market_data/ --recursive
```

### 2. Import Notebooks

1. In Databricks workspace, click "Workspace" in left sidebar
2. Right-click on your user folder → "Import"
3. Select "File" and upload:
   - `notebooks/01_ETL_Pipeline.py`
   - `notebooks/02_Analytics_Dashboard.py`

### 3. Create a Cluster

1. Click "Compute" in left sidebar
2. Click "Create Cluster"
3. Configure:
   - **Cluster Name**: jhb-realestate-cluster
   - **Cluster Mode**: Single Node (for Community Edition)
   - **Databricks Runtime**: 13.3 LTS or later
   - **Node Type**: Default (Community Edition has limited options)
4. Click "Create Cluster"

### 4. Run the Pipeline

**Step 1: Run ETL Notebook**
1. Open `01_ETL_Pipeline` notebook
2. Attach to your cluster (dropdown at top)
3. Click "Run All" or run cells individually
4. Verify Delta tables are created

**Step 2: Run Analytics Notebook**
1. Open `02_Analytics_Dashboard` notebook
2. Attach to your cluster
3. Click "Run All"
4. View insights and visualizations

## Key Differences: Local vs Databricks

| Feature | Local PySpark | Databricks |
|---------|---------------|------------|
| Storage Format | Parquet | Delta Lake |
| File System | Local disk | DBFS |
| Cluster Management | Manual | Managed |
| Notebooks | Jupyter (optional) | Built-in |
| Visualization | External tools | Built-in charts |
| Collaboration | Git only | Workspace sharing |
| Version Control | Git | Git + Databricks Repos |

## Delta Lake Benefits

1. **ACID Transactions**: Reliable writes with rollback capability
2. **Time Travel**: Query historical versions of data
3. **Schema Evolution**: Add/modify columns without rewriting data
4. **Unified Batch & Streaming**: Same API for both workloads
5. **Performance**: Optimized file layout and caching

## Example: Time Travel Query

```sql
-- View data as it was 1 hour ago
SELECT * FROM market_analytics VERSION AS OF 1

-- View data at specific timestamp
SELECT * FROM market_analytics TIMESTAMP AS OF '2026-02-07 10:00:00'
```

## Databricks SQL Analytics

After running the notebooks, you can:

1. Create SQL queries in "SQL Editor"
2. Build dashboards with visualizations
3. Schedule automated refreshes
4. Share dashboards with stakeholders

## Next Steps

1. **Optimize Delta Tables**: Run `OPTIMIZE` and `VACUUM` commands
2. **Create Workflows**: Schedule notebooks to run automatically
3. **Add Data Quality Checks**: Use Delta Live Tables
4. **Implement CI/CD**: Connect to GitHub for automated deployments
5. **Add Monitoring**: Set up alerts for pipeline failures

## Troubleshooting

**Issue**: Files not found in DBFS
- **Solution**: Verify upload paths match notebook paths exactly

**Issue**: Cluster won't start
- **Solution**: Community Edition has resource limits; wait and retry

**Issue**: Delta table not found
- **Solution**: Run ETL notebook first to create tables

## Resources

- Databricks Documentation: https://docs.databricks.com/
- Delta Lake Guide: https://docs.delta.io/
- Community Forums: https://community.databricks.com/

# Enterprise Data Pipeline Architecture

## Overview
This pipeline demonstrates a production-grade, decoupled data architecture using industry-standard tools.

## Architecture Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Google Drive │ --> │   Fivetran   │ --> │   AWS S3     │ --> │  Databricks  │
│  (Source)    │     │   (ELT)      │     │ (Data Lake)  │     │  (Compute)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

## Why This Architecture?

### Decoupled Components
- **Source (Google Drive)**: Simulates client file drops
- **Ingestion (Fivetran)**: Automated, no-code ELT
- **Storage (S3)**: Scalable, durable data lake
- **Compute (Databricks)**: Separate processing layer

### Enterprise Benefits
1. **Scalability**: Each component scales independently
2. **Reliability**: Fivetran handles retries and monitoring
3. **Flexibility**: Swap components without rewriting code
4. **Auditability**: Full lineage tracking
5. **Cost Optimization**: Pay only for what you use

## Setup Guide

### Phase 1: Prepare Data for Google Drive

#### 1.1 Export Processed Data
```bash
# Create export directory
mkdir -p exports/for_google_drive

# Copy processed data
cp -r data/processed/* exports/for_google_drive/
```

#### 1.2 Create CSV Exports (Fivetran-friendly format)
Run the export script:
```bash
python src/export/prepare_for_fivetran.py
```

This creates:
- `exports/compliance_report.csv`
- `exports/market_analytics.csv`

### Phase 2: Google Drive Setup

#### 2.1 Create Folder Structure
1. Log into Google Drive
2. Create folder: `JHB-RealEstate-Pipeline`
3. Create subfolders:
   - `raw/contracts/`
   - `raw/market_data/`
   - `processed/compliance/`
   - `processed/market/`

#### 2.2 Upload Files
Upload the CSV files from `exports/` to appropriate Google Drive folders.

### Phase 3: AWS S3 Setup

#### 3.1 Create S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://jhb-realestate-datalake --region us-east-1

# Create folder structure
aws s3api put-object --bucket jhb-realestate-datalake --key raw/
aws s3api put-object --bucket jhb-realestate-datalake --key processed/
aws s3api put-object --bucket jhb-realestate-datalake --key analytics/
```

#### 3.2 Configure Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "FivetranAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::FIVETRAN_ACCOUNT_ID:role/fivetran"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::jhb-realestate-datalake/*",
        "arn:aws:s3:::jhb-realestate-datalake"
      ]
    }
  ]
}
```

#### 3.3 Create IAM User for Databricks
```bash
# Create user
aws iam create-user --user-name databricks-s3-access

# Attach policy
aws iam attach-user-policy \
  --user-name databricks-s3-access \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create access keys
aws iam create-access-key --user-name databricks-s3-access
```

Save the Access Key ID and Secret Access Key for Databricks configuration.

### Phase 4: Fivetran Configuration

#### 4.1 Sign Up
1. Go to https://fivetran.com/
2. Sign up for free trial (14 days)

#### 4.2 Configure Google Drive Connector
1. In Fivetran dashboard, click "+ Connector"
2. Search for "Google Drive"
3. Authenticate with your Google account
4. Select folder: `JHB-RealEstate-Pipeline`
5. Configure sync settings:
   - **Sync Frequency**: Every 6 hours (or manual)
   - **File Format**: CSV
   - **Destination**: Amazon S3

#### 4.3 Configure S3 Destination
1. In Fivetran, go to "Destinations"
2. Click "+ Add Destination"
3. Select "Amazon S3"
4. Enter credentials:
   - **Bucket Name**: `jhb-realestate-datalake`
   - **Region**: `us-east-1`
   - **Access Key ID**: (from IAM user)
   - **Secret Access Key**: (from IAM user)
   - **Prefix**: `fivetran/`

#### 4.4 Start Sync
Click "Start Initial Sync" and monitor progress.

### Phase 5: Databricks Integration with S3

#### 5.1 Configure S3 Access in Databricks
Create a notebook cell:
```python
# Configure AWS credentials
spark.conf.set("fs.s3a.access.key", "YOUR_ACCESS_KEY")
spark.conf.set("fs.s3a.secret.key", "YOUR_SECRET_KEY")
spark.conf.set("fs.s3a.endpoint", "s3.amazonaws.com")
```

**Better approach - Use Databricks Secrets:**
```python
# Store credentials securely
dbutils.secrets.put(scope="aws", key="access-key", string_value="YOUR_ACCESS_KEY")
dbutils.secrets.put(scope="aws", key="secret-key", string_value="YOUR_SECRET_KEY")

# Use in notebook
spark.conf.set("fs.s3a.access.key", dbutils.secrets.get(scope="aws", key="access-key"))
spark.conf.set("fs.s3a.secret.key", dbutils.secrets.get(scope="aws", key="secret-key"))
```

#### 5.2 Mount S3 Bucket (Recommended)
```python
# Mount S3 bucket to DBFS
dbutils.fs.mount(
  source = "s3a://jhb-realestate-datalake",
  mount_point = "/mnt/realestate",
  extra_configs = {
    "fs.s3a.access.key": dbutils.secrets.get(scope="aws", key="access-key"),
    "fs.s3a.secret.key": dbutils.secrets.get(scope="aws", key="secret-key")
  }
)

# Verify mount
display(dbutils.fs.ls("/mnt/realestate"))
```

#### 5.3 Read Data from S3
```python
# Read data from mounted S3
df_market = spark.read.csv("/mnt/realestate/fivetran/market_analytics.csv", header=True, inferSchema=True)
df_compliance = spark.read.csv("/mnt/realestate/fivetran/compliance_report.csv", header=True, inferSchema=True)

# Process and write to Delta Lake
df_market.write.format("delta").mode("overwrite").save("/mnt/realestate/delta/market_analytics")
```

## Data Flow Timeline

1. **T+0**: Upload files to Google Drive
2. **T+5min**: Fivetran detects new files
3. **T+10min**: Fivetran syncs to S3
4. **T+15min**: Databricks reads from S3
5. **T+20min**: Analytics available in Databricks

## Monitoring & Observability

### Fivetran Dashboard
- Sync status and history
- Row counts and data volume
- Error logs and alerts

### AWS CloudWatch
- S3 bucket metrics
- Access logs
- Cost tracking

### Databricks
- Job run history
- Query performance
- Data lineage

## Cost Considerations

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| Google Drive | 15 GB | $0 |
| Fivetran | 14-day trial | $0 (trial) |
| AWS S3 | 5 GB | ~$0.10/month |
| Databricks CE | Limited | $0 |

**Total**: ~$0.10/month during trial period

## Interview Talking Points

1. **Decoupled Architecture**: "I separated ingestion, storage, and compute layers"
2. **Industry Tools**: "Used Fivetran for automated ELT, not custom scripts"
3. **Cloud-Native**: "Leveraged S3 as the central data lake"
4. **Scalability**: "Each component can scale independently"
5. **Security**: "Implemented IAM roles and secret management"
6. **Monitoring**: "Full observability across the pipeline"

## Troubleshooting

### Fivetran Can't Access Google Drive
- Verify OAuth permissions
- Check folder sharing settings

### S3 Access Denied
- Verify IAM policy
- Check bucket policy
- Confirm credentials

### Databricks Can't Read S3
- Verify mount configuration
- Check AWS credentials
- Test with `dbutils.fs.ls()`

## Next Steps

1. Set up automated testing
2. Implement data quality checks
3. Add alerting for pipeline failures
4. Create CI/CD for notebook deployment
5. Document data catalog

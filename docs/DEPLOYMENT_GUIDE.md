# 🚀 Deployment Guide - JHB Real Estate Data Lakehouse

**Complete step-by-step guide to deploy the pipeline to AWS + Databricks**

---

## 📋 Prerequisites

- AWS Account (Free Tier)
- Databricks Community Edition account
- Google Drive account (15GB free)
- Fivetran account (14-day trial)
- AWS CLI installed
- Git installed

---

## 🏗️ Architecture Overview

```
Local → Google Drive → Fivetran → AWS S3 → Databricks → Analytics
```

---

## STEP 1: AWS S3 Setup (5 minutes)

### 1.1 Deploy CloudFormation Stack

```bash
# Navigate to infrastructure directory
cd infrastructure/aws

# Deploy stack (replace UNIQUE-BUCKET-NAME)
aws cloudformation create-stack \
  --stack-name jhb-realestate-datalake \
  --template-body file://s3-datalake-stack.yaml \
  --parameters ParameterKey=BucketName,ParameterValue=jhb-realestate-YOUR-NAME \
  --capabilities CAPABILITY_NAMED_IAM

# Wait for completion (2-3 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name jhb-realestate-datalake

# Get outputs
aws cloudformation describe-stacks \
  --stack-name jhb-realestate-datalake \
  --query 'Stacks[0].Outputs'
```

### 1.2 Create Fivetran IAM Access Keys

```bash
# Get Fivetran user name from stack outputs
FIVETRAN_USER=$(aws cloudformation describe-stacks \
  --stack-name jhb-realestate-datalake \
  --query 'Stacks[0].Outputs[?OutputKey==`FivetranUserArn`].OutputValue' \
  --output text | cut -d'/' -f2)

# Create access keys
aws iam create-access-key --user-name $FIVETRAN_USER

# Save the AccessKeyId and SecretAccessKey (you'll need these for Fivetran)
```

**⚠️ IMPORTANT**: Save these credentials securely. You cannot retrieve the secret key again.

---

## STEP 2: Google Drive Setup (3 minutes)

### 2.1 Create Folder Structure

1. Go to https://drive.google.com/
2. Create folder: `JHB-RealEstate-Pipeline`
3. Create subfolders:
   - `raw/contracts/`
   - `raw/market_data/`

### 2.2 Upload Mock Data

```bash
# Generate mock data locally
python src/ingestion/generate_mock_data.py

# Export for Google Drive
python src/export/prepare_for_fivetran.py

# Manually upload files from exports/for_google_drive/ to Google Drive
```

---

## STEP 3: Fivetran Setup (10 minutes)

### 3.1 Sign Up

1. Go to https://fivetran.com/
2. Sign up for 14-day free trial
3. Verify email

### 3.2 Configure Google Drive Source

1. Click **"+ Connector"**
2. Search for **"Google Drive"**
3. Authenticate with your Google account
4. Select folder: `JHB-RealEstate-Pipeline`
5. Configure:
   - **Sync Frequency**: Every 6 hours (or manual)
   - **File Format**: CSV and TXT
   - **Destination**: Amazon S3

### 3.3 Configure S3 Destination

1. In Fivetran, go to **"Destinations"**
2. Click **"+ Add Destination"**
3. Select **"Amazon S3"**
4. Enter credentials (from Step 1.2):
   - **Bucket Name**: `jhb-realestate-YOUR-NAME`
   - **Region**: `us-east-1` (or your region)
   - **Access Key ID**: (from IAM)
   - **Secret Access Key**: (from IAM)
   - **Prefix**: `fivetran/`

### 3.4 Start Initial Sync

1. Click **"Start Initial Sync"**
2. Monitor progress (5-10 minutes)
3. Verify files in S3:

```bash
aws s3 ls s3://jhb-realestate-YOUR-NAME/fivetran/ --recursive
```

---

## STEP 4: Databricks Setup (15 minutes)

### 4.1 Sign Up for Community Edition

1. Go to https://community.cloud.databricks.com/
2. Sign up for free Community Edition
3. Verify email and log in

### 4.2 Create Cluster

1. Click **"Compute"** in sidebar
2. Click **"Create Cluster"**
3. Configure:
   - **Cluster Name**: `jhb-realestate-cluster`
   - **Cluster Mode**: Single Node
   - **Databricks Runtime**: 13.3 LTS (or latest)
   - **Node Type**: (default - Community Edition has one option)
4. Click **"Create Cluster"** (takes 5-7 minutes to start)

### 4.3 Configure S3 Access

**⚠️ Community Edition Limitation**: Cannot use `dbutils.fs.mount()`. Use direct S3 access instead.

Create a notebook with this configuration:

```python
# Cell 1: Configure S3 Access
spark.conf.set("fs.s3a.access.key", "<YOUR_ACCESS_KEY>")
spark.conf.set("fs.s3a.secret.key", "<YOUR_SECRET_KEY>")
spark.conf.set("fs.s3a.endpoint", "s3.amazonaws.com")

# Test access
df = spark.read.csv("s3a://jhb-realestate-YOUR-NAME/fivetran/market_data.csv", header=True)
display(df.limit(5))
```

**🔒 Security Best Practice**: Use Databricks Secrets (not available in Community Edition). For production, upgrade to Standard tier.

### 4.4 Import Notebooks

1. Click **"Workspace"** in sidebar
2. Right-click your user folder → **"Import"**
3. Select **"File"**
4. Upload notebooks from `notebooks/` directory:
   - `01_ETL_Pipeline.py`
   - `02_Analytics_Dashboard.py`
   - `03_S3_to_Databricks_Monitored.py`

### 4.5 Update Notebook Paths

Edit `03_S3_to_Databricks_Monitored.py`:

```python
# Update these paths to match your S3 bucket
BUCKET_NAME = "jhb-realestate-YOUR-NAME"
INPUT_PATH = f"s3a://{BUCKET_NAME}/fivetran/"
OUTPUT_PATH = f"s3a://{BUCKET_NAME}/processed/"
```

### 4.6 Run ETL Pipeline

1. Open `03_S3_to_Databricks_Monitored.py`
2. Attach to cluster
3. Click **"Run All"**
4. Monitor execution (5-10 minutes)

---

## STEP 5: Verify Deployment (5 minutes)

### 5.1 Check S3 Output

```bash
# Verify processed data
aws s3 ls s3://jhb-realestate-YOUR-NAME/processed/ --recursive

# Expected structure:
# processed/compliance_report/
# processed/market_analytics/region=Sandton/
# processed/market_analytics/region=Rosebank/
```

### 5.2 Check Databricks Output

In Databricks notebook:

```python
# Read processed data
df = spark.read.parquet(f"s3a://{BUCKET_NAME}/processed/market_analytics")
display(df.groupBy("region").count())
```

### 5.3 Check Logs

```bash
# Local logs
cat logs/etl.log | jq -r 'select(.level=="ERROR")'

# Should return empty (no errors)
```

---

## 📊 Monitoring & Maintenance

### Daily Checks

```bash
# Check S3 storage usage (stay under 5GB)
aws s3 ls s3://jhb-realestate-YOUR-NAME --recursive --summarize

# Check Fivetran sync status
# Log into Fivetran dashboard → View connector status
```

### Weekly Maintenance

```bash
# Clean up old data (lifecycle policies handle this automatically)
# Verify lifecycle policies are active:
aws s3api get-bucket-lifecycle-configuration \
  --bucket jhb-realestate-YOUR-NAME
```

---

## 💰 Cost Monitoring

### Free Tier Limits

| Service | Limit | Current Usage | Status |
|---------|-------|---------------|--------|
| S3 Storage | 5GB | Check with `aws s3 ls --summarize` | ✅ |
| S3 GET Requests | 20,000/month | Check CloudWatch | ✅ |
| Databricks | Community Edition | N/A | ✅ |
| Fivetran | 14-day trial | Check dashboard | ⚠️ |

### Check S3 Costs

```bash
# View S3 metrics in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=jhb-realestate-YOUR-NAME \
  --start-time 2026-02-01T00:00:00Z \
  --end-time 2026-02-10T23:59:59Z \
  --period 86400 \
  --statistics Average
```

---

## 🔧 Troubleshooting

### Issue: Fivetran Sync Fails

**Solution**:
```bash
# Verify IAM permissions
aws iam get-user-policy \
  --user-name $FIVETRAN_USER \
  --policy-name jhb-realestate-YOUR-NAME-fivetran-s3-policy

# Test S3 access with Fivetran credentials
aws s3 ls s3://jhb-realestate-YOUR-NAME/ \
  --profile fivetran
```

### Issue: Databricks Can't Read S3

**Solution**:
```python
# Verify credentials in notebook
print(spark.conf.get("fs.s3a.access.key"))  # Should show key
print(spark.conf.get("fs.s3a.secret.key"))  # Should show key

# Test direct S3 access
dbutils.fs.ls("s3a://jhb-realestate-YOUR-NAME/")
```

### Issue: S3 Costs Exceeding Free Tier

**Solution**:
```bash
# Check lifecycle policies
aws s3api get-bucket-lifecycle-configuration \
  --bucket jhb-realestate-YOUR-NAME

# Manually delete old data
aws s3 rm s3://jhb-realestate-YOUR-NAME/raw/ --recursive
```

---

## 🎯 Success Criteria

✅ CloudFormation stack deployed  
✅ S3 bucket created with lifecycle policies  
✅ Fivetran syncing data to S3  
✅ Databricks reading from S3  
✅ ETL pipeline running successfully  
✅ Processed data in S3  
✅ Monitoring logs showing no errors  
✅ Staying within Free Tier limits  

---

## 📚 Next Steps

1. **Set up alerts**: Configure CloudWatch alarms for S3 usage
2. **Automate**: Schedule Databricks jobs (requires Standard tier)
3. **Optimize**: Review query performance and partition strategy
4. **Scale**: Add more data sources or analytics

---

## 🆘 Support

- **AWS Issues**: Check [AWS Documentation](https://docs.aws.amazon.com/)
- **Databricks Issues**: Check [Databricks Community](https://community.databricks.com/)
- **Fivetran Issues**: Check [Fivetran Support](https://fivetran.com/docs)
- **Project Issues**: Review [Monitoring Guide](MONITORING_FRAMEWORK.md)

---

**Deployment Time**: ~40 minutes  
**Cost**: $0.00/month (Free Tier)  
**Status**: Production-Ready ✅

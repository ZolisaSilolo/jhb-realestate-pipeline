# Databricks notebook source
# MAGIC %md
# MAGIC # S3 to Databricks ETL Pipeline with Enterprise Monitoring
# MAGIC 
# MAGIC This notebook demonstrates production-grade error handling and structured logging.

# COMMAND ----------

import logging
import json
from datetime import datetime

# Setup structured JSON logger for Databricks
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DatabricksETL")

def log_json(level, message, **kwargs):
    """Structured JSON logging for machine-readable logs"""
    log_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "component": "DatabricksETL",
        "message": message,
        **kwargs
    }
    print(json.dumps(log_record))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Safety Net: Mount Validation

# COMMAND ----------

def strict_mount_check(mount_point):
    """
    Verifies mount exists AND is readable.
    Many errors happen when a mount 'exists' but the keys are expired.
    """
    try:
        logger.info(f"Verifying mount access: {mount_point}")
        log_json("INFO", "Mount check started", mount_point=mount_point)
        
        files = dbutils.fs.ls(mount_point)
        
        logger.info(f"Mount healthy. Found {len(files)} items.")
        log_json("INFO", "Mount check passed", mount_point=mount_point, file_count=len(files))
        return True
        
    except Exception as e:
        logger.critical(f"Mount check failed! Possible IAM permission issue: {str(e)}")
        log_json("CRITICAL", "Mount check failed", mount_point=mount_point, error=str(e))
        print(f"!! ALERT: MOUNT FAILURE !! - {mount_point}")
        raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ## Input Validation: Circuit Breaker Pattern

# COMMAND ----------

def validate_input_data(path, min_files=1):
    """
    Validates that input data exists before processing.
    Implements 'Fail Fast' pattern to avoid wasting compute.
    """
    try:
        logger.info(f"Validating input data at: {path}")
        files = dbutils.fs.ls(path)
        
        if len(files) < min_files:
            logger.warning(f"Insufficient data found. Expected >= {min_files}, found {len(files)}")
            log_json("WARNING", "Insufficient input data", path=path, expected=min_files, found=len(files))
            return False
        
        logger.info(f"Input validation passed: {len(files)} files found")
        log_json("INFO", "Input validation passed", path=path, file_count=len(files))
        return True
        
    except Exception as e:
        logger.error(f"Input validation failed: {str(e)}")
        log_json("ERROR", "Input validation failed", path=path, error=str(e))
        raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main ETL Execution with Error Handling

# COMMAND ----------

try:
    log_json("INFO", "ETL Job Starting")
    
    # Step 1: Mount Check
    MOUNT_POINT = "/mnt/jhb_datalake"
    strict_mount_check(MOUNT_POINT)
    
    # Step 2: Input Validation (Circuit Breaker)
    INPUT_PATH = f"{MOUNT_POINT}/fivetran/google_drive_raw/"
    
    if not validate_input_data(INPUT_PATH, min_files=1):
        logger.warning("No new data found from Fivetran. Stopping job gracefully.")
        log_json("WARNING", "Job skipped - no data", reason="NO_DATA_FROM_FIVETRAN")
        dbutils.notebook.exit("SKIPPED_NO_DATA")
    
    # Step 3: Read Data
    logger.info("Reading data from S3")
    log_json("INFO", "Data read started", source=INPUT_PATH)
    
    df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(INPUT_PATH)
    
    row_count = df.count()
    logger.info(f"Loaded {row_count} rows")
    log_json("INFO", "Data read completed", row_count=row_count)
    
    # Step 4: Data Quality Check
    if row_count == 0:
        logger.error("Zero rows loaded. Data quality issue detected.")
        log_json("ERROR", "Data quality failure", issue="ZERO_ROWS")
        raise ValueError("Empty dataset detected")
    
    # Step 5: Transform (Your ETL logic here)
    logger.info("Applying transformations")
    log_json("INFO", "Transformation started")
    
    # ... Your transformation logic ...
    
    # Step 6: Write to Delta Lake
    OUTPUT_PATH = f"{MOUNT_POINT}/processed/market_analytics"
    logger.info(f"Writing to Delta Lake: {OUTPUT_PATH}")
    log_json("INFO", "Write started", destination=OUTPUT_PATH)
    
    df.write.format("delta") \
        .mode("overwrite") \
        .save(OUTPUT_PATH)
    
    logger.info("ETL Job Finished Successfully")
    log_json("INFO", "ETL Job Completed", status="SUCCESS", rows_processed=row_count)
    
except Exception as e:
    logger.error("ETL Job Failed", exc_info=True)
    log_json("CRITICAL", "ETL Job Failed", error=str(e), error_type=type(e).__name__)
    print(f"!! ALERT: DATABRICKS ETL FAILURE !! - {str(e)}")
    
    # Mark job as failed in Databricks UI
    raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ## Success Metrics (Optional)

# COMMAND ----------

# Log final metrics for monitoring
log_json("INFO", "Job Metrics", 
         execution_time_seconds=0,  # Calculate actual time
         rows_processed=row_count if 'row_count' in locals() else 0,
         status="COMPLETED")

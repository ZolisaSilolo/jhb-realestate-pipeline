import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, current_timestamp, lit, regexp_extract
from pyspark.sql.types import StringType, DoubleType, BooleanType

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.logger import get_logger

log = get_logger("ETLJob")

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
RAW_LEASE_PATH = os.path.join(BASE_DIR, "data/raw/contracts")
RAW_MARKET_PATH = os.path.join(BASE_DIR, "data/raw/market_data/jhb_sales_history.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data/processed")

def create_spark_session():
    """
    Initializes a Spark Session.
    In a real EMR job, this connects to the cluster manager (YARN).
    Locally, it runs on your machine's cores.
    """
    try:
        log.info("Initializing Spark session")
        import sys
        os.environ['PYSPARK_PYTHON'] = sys.executable
        os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
        
        spark = SparkSession.builder \
            .appName("JHB_RealEstate_Compliance_Pipeline") \
            .master("local[*]") \
            .config("spark.driver.host", "127.0.0.1") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        log.info("Spark session created successfully")
        return spark
    except Exception as e:
        log.critical("Failed to create Spark session", exc_info=True)
        raise

# --- COMPLIANCE LOGIC (The "Smart" Part) ---
def check_compliance_logic(text_content):
    """
    Analyzes lease text for mandatory legal keywords.
    Returns 'COMPLIANT' if safe, 'RISK_FLAGGED' if missing docs.
    """
    if not text_content:
        return "ERROR_EMPTY"
    
    # Convert to lower case for case-insensitive searching
    text = text_content.lower()
    
    # PPRA & FICA Requirements
    has_disclosure = "defect disclosure" in text
    has_fica = "fica" in text or "verification" in text
    
    if has_disclosure and has_fica:
        return "COMPLIANT"
    else:
        return "NON_COMPLIANT"

# Register the function as a UDF (User Defined Function) for Spark
check_compliance_udf = udf(check_compliance_logic, StringType())

def process_leases(spark):
    log.info("Processing Lease Agreements (Unstructured Data)")
    
    try:
        # Validate input path exists
        if not os.path.exists(RAW_LEASE_PATH):
            log.error(f"Lease path not found: {RAW_LEASE_PATH}")
            raise FileNotFoundError(f"Missing directory: {RAW_LEASE_PATH}")
        
        from pyspark.sql.functions import input_file_name, lower, when
        
        raw_leases = spark.read.text(RAW_LEASE_PATH)
        row_count = raw_leases.count()
        log.info(f"Loaded {row_count} lease documents")
        
        if row_count == 0:
            log.warning("No lease documents found. Skipping processing.")
            return
        
        final_leases = raw_leases.withColumnRenamed("value", "document_body") \
            .withColumn("source_file", input_file_name()) \
            .withColumn("ingestion_time", current_timestamp()) \
            .withColumn("body_lower", lower(col("document_body"))) \
            .withColumn("compliance_status", 
                when((col("body_lower").contains("defect disclosure")) & 
                     (col("body_lower").contains("fica") | col("body_lower").contains("verification")), 
                     "COMPLIANT").otherwise("NON_COMPLIANT")) \
            .drop("body_lower")
        
        output_dir = os.path.join(OUTPUT_PATH, "compliance_report")
        final_leases.write.mode("overwrite").parquet(output_dir)
        log.info(f"Lease data processed and saved to {output_dir}")
        
    except Exception as e:
        log.error("Lease processing failed", exc_info=True)
        raise

def process_market_data(spark):
    log.info("Processing Market Data (Structured Data)")
    
    try:
        # Validate input file exists
        if not os.path.exists(RAW_MARKET_PATH):
            log.error(f"Market data file not found: {RAW_MARKET_PATH}")
            raise FileNotFoundError(f"Missing file: {RAW_MARKET_PATH}")
        
        df_market = spark.read.option("header", "true") \
            .option("inferSchema", "true") \
            .csv(RAW_MARKET_PATH)
        
        row_count = df_market.count()
        log.info(f"Loaded {row_count} market records")
        
        if row_count == 0:
            log.warning("No market data found. Skipping processing.")
            return
        
        cleaned_market = df_market.filter(col("price_zar").isNotNull()) \
            .filter(col("sq_meters") > 0) \
            .withColumn("price_per_sqm", col("price_zar") / col("sq_meters")) \
            .withColumn("is_luxury", col("price_zar") > 3000000)
        
        cleaned_count = cleaned_market.count()
        log.info(f"Cleaned data: {cleaned_count} valid records")
        
        output_dir = os.path.join(OUTPUT_PATH, "market_analytics")
        cleaned_market.write.mode("overwrite").partitionBy("region").parquet(output_dir)
        log.info(f"Market data processed and saved to {output_dir}")
        
    except Exception as e:
        log.error("Market data processing failed", exc_info=True)
        raise

if __name__ == "__main__":
    spark = None
    try:
        log.info("ETL Job Starting")
        spark = create_spark_session()
        
        process_leases(spark)
        process_market_data(spark)
        
        log.info("ETL Job Completed Successfully")
        
    except Exception as e:
        log.critical("ETL Job Failed", exc_info=True)
        print(f"!! ALERT: ETL PIPELINE FAILURE !! - {str(e)}")
        exit(1)
    finally:
        if spark:
            spark.stop()
            log.info("Spark session stopped")
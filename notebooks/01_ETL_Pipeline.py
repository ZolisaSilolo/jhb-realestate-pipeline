# Databricks notebook source
# MAGIC %md
# MAGIC # JHB Real Estate Pipeline - Databricks ETL
# MAGIC 
# MAGIC This notebook processes raw lease contracts and market data, applying transformations and writing to Delta Lake format.
# MAGIC 
# MAGIC **Architecture**: Bronze → Silver Layer Transformation

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Set up paths for Databricks File System (DBFS)
RAW_CONTRACTS_PATH = "/FileStore/jhb-realestate/raw/contracts/"
RAW_MARKET_PATH = "/FileStore/jhb-realestate/raw/market_data/"
PROCESSED_COMPLIANCE_PATH = "/FileStore/jhb-realestate/processed/compliance_report"
PROCESSED_MARKET_PATH = "/FileStore/jhb-realestate/processed/market_analytics"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load Raw Data

# COMMAND ----------

from pyspark.sql.functions import *

# Load lease contracts
df_contracts = spark.read.text(RAW_CONTRACTS_PATH)
print(f"Loaded {df_contracts.count()} contract files")

# Load market data
df_market = spark.read.option("header", "true").option("inferSchema", "true").csv(RAW_MARKET_PATH)
print(f"Loaded {df_market.count()} market records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Transform Lease Contracts (Compliance Check)

# COMMAND ----------

# Compliance keywords check using native Spark functions
df_compliance = df_contracts.withColumn(
    "compliance_status",
    when(
        lower(col("value")).contains("defect disclosure") & 
        lower(col("value")).contains("fica"),
        "COMPLIANT"
    ).otherwise("NON_COMPLIANT")
).withColumn("contract_id", monotonically_increasing_id())

# Select relevant columns
df_compliance_final = df_compliance.select("contract_id", "compliance_status")

print("Compliance transformation complete")
df_compliance_final.groupBy("compliance_status").count().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Transform Market Data (Enrichment)

# COMMAND ----------

# Calculate price per square meter and identify luxury properties
df_market_enriched = df_market.withColumn(
    "price_per_sqm", 
    round(col("price_zar") / col("size_sqm"), 2)
).withColumn(
    "is_luxury", 
    col("price_zar") > 3000000
)

print("Market data enrichment complete")
df_market_enriched.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Write to Delta Lake (Silver Layer)

# COMMAND ----------

# Write compliance data
df_compliance_final.write \
    .format("delta") \
    .mode("overwrite") \
    .save(PROCESSED_COMPLIANCE_PATH)

print(f"Compliance data written to {PROCESSED_COMPLIANCE_PATH}")

# COMMAND ----------

# Write market data partitioned by region
df_market_enriched.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("region") \
    .save(PROCESSED_MARKET_PATH)

print(f"Market data written to {PROCESSED_MARKET_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Verify Delta Tables

# COMMAND ----------

# Register as Delta tables for SQL access
spark.sql(f"CREATE TABLE IF NOT EXISTS compliance_report USING DELTA LOCATION '{PROCESSED_COMPLIANCE_PATH}'")
spark.sql(f"CREATE TABLE IF NOT EXISTS market_analytics USING DELTA LOCATION '{PROCESSED_MARKET_PATH}'")

print("Delta tables registered successfully")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verify table creation
# MAGIC SHOW TABLES

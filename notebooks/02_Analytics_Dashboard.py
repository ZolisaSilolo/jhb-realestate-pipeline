# Databricks notebook source
# MAGIC %md
# MAGIC # JHB Real Estate Analytics - Business Intelligence
# MAGIC 
# MAGIC This notebook queries the processed Delta Lake tables to generate business insights.
# MAGIC 
# MAGIC **Layer**: Silver → Gold (Analytics)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Delta Tables

# COMMAND ----------

# Read from Delta Lake
df_market = spark.read.format("delta").load("/FileStore/jhb-realestate/processed/market_analytics")
df_compliance = spark.read.format("delta").load("/FileStore/jhb-realestate/processed/compliance_report")

# Register as temp views for SQL
df_market.createOrReplaceTempView("market_sales")
df_compliance.createOrReplaceTempView("lease_compliance")

print("Data loaded successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Insight 1: Compliance Risk Audit

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     compliance_status,
# MAGIC     count(*) as contract_count,
# MAGIC     round(count(*) * 100.0 / (select count(*) from lease_compliance), 2) as percentage
# MAGIC FROM 
# MAGIC     lease_compliance
# MAGIC GROUP BY 
# MAGIC     compliance_status

# COMMAND ----------

# MAGIC %md
# MAGIC ## Insight 2: Highest Value Suburbs

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     region, 
# MAGIC     suburb, 
# MAGIC     round(avg(price_zar), 0) as avg_price,
# MAGIC     round(avg(price_per_sqm), 0) as avg_price_per_sqm,
# MAGIC     count(*) as sales_volume
# MAGIC FROM 
# MAGIC     market_sales
# MAGIC GROUP BY 
# MAGIC     region, suburb
# MAGIC HAVING 
# MAGIC     sales_volume > 2
# MAGIC ORDER BY 
# MAGIC     avg_price_per_sqm DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Insight 3: Luxury Market Share by Region

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     region,
# MAGIC     count(*) as total_sales,
# MAGIC     sum(case when is_luxury = true then 1 else 0 end) as luxury_sales,
# MAGIC     round(sum(case when is_luxury = true then 1 else 0 end) * 100.0 / count(*), 1) as luxury_pct
# MAGIC FROM 
# MAGIC     market_sales
# MAGIC GROUP BY 
# MAGIC     region
# MAGIC ORDER BY 
# MAGIC     luxury_pct DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Insight 4: Price Distribution by Region (Visualization)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     region,
# MAGIC     price_zar,
# MAGIC     is_luxury
# MAGIC FROM 
# MAGIC     market_sales
# MAGIC ORDER BY 
# MAGIC     region, price_zar

# COMMAND ----------

# MAGIC %md
# MAGIC ## Insight 5: Sales Volume Trends

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     region,
# MAGIC     count(*) as total_sales,
# MAGIC     round(avg(price_zar), 0) as avg_price,
# MAGIC     round(min(price_zar), 0) as min_price,
# MAGIC     round(max(price_zar), 0) as max_price
# MAGIC FROM 
# MAGIC     market_sales
# MAGIC GROUP BY 
# MAGIC     region
# MAGIC ORDER BY 
# MAGIC     total_sales DESC

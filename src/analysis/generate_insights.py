import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc, avg, count

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
MARKET_DATA_PATH = os.path.join(BASE_DIR, "data/processed/market_analytics")
COMPLIANCE_DATA_PATH = os.path.join(BASE_DIR, "data/processed/compliance_report")

def create_spark_session():
    spark = SparkSession.builder \
        .appName("JHB_RealEstate_Analytics") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def run_analytics(spark):
    print("\n--- LOADING PROCESSED DATA (SILVER LAYER) ---")
    
    # 1. Load the Parquet data
    df_market = spark.read.parquet(MARKET_DATA_PATH)
    df_compliance = spark.read.parquet(COMPLIANCE_DATA_PATH)
    
    # 2. Register as Temp Views (This allows us to write pure SQL)
    df_market.createOrReplaceTempView("market_sales")
    df_compliance.createOrReplaceTempView("lease_compliance")
    
    print("Data loaded and registered as SQL Tables.\n")

    # --- INSIGHT 1: COMPLIANCE RISK AUDIT ---
    print("--- INSIGHT 1: COMPLIANCE RISK AUDIT ---")
    risk_query = """
    SELECT 
        compliance_status,
        count(*) as contract_count,
        cast(count(*) * 100.0 / (select count(*) from lease_compliance) as decimal(5,2)) as percentage
    FROM 
        lease_compliance
    GROUP BY 
        compliance_status
    """
    spark.sql(risk_query).show()
    
    # --- INSIGHT 2: LUCRATIVE SUBURBS (JHB MARKET) ---
    print("--- INSIGHT 2: HIGHEST VALUE SUBURBS (Avg Price) ---")
    value_query = """
    SELECT 
        region, 
        suburb, 
        round(avg(price_zar), 0) as avg_price,
        round(avg(price_per_sqm), 0) as avg_price_per_sqm,
        count(*) as sales_volume
    FROM 
        market_sales
    GROUP BY 
        region, suburb
    HAVING 
        sales_volume > 2
    ORDER BY 
        avg_price_per_sqm DESC
    LIMIT 10
    """
    spark.sql(value_query).show(truncate=False)

    # --- INSIGHT 3: LUXURY MARKET SHARE ---
    print("--- INSIGHT 3: LUXURY MARKET SHARE (> R3m) BY REGION ---")
    luxury_query = """
    SELECT 
        region,
        count(*) as total_sales,
        sum(case when is_luxury = true then 1 else 0 end) as luxury_sales,
        round(sum(case when is_luxury = true then 1 else 0 end) * 100.0 / count(*), 1) as luxury_pct
    FROM 
        market_sales
    GROUP BY 
        region
    ORDER BY 
        luxury_pct DESC
    """
    spark.sql(luxury_query).show()

if __name__ == "__main__":
    spark = create_spark_session()
    try:
        run_analytics(spark)
    except Exception as e:
        print(f"Analytics Job Failed: {e}")
    finally:
        spark.stop()

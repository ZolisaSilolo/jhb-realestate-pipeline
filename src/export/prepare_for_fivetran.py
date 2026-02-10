import os
import shutil
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.logger import get_logger

log = get_logger("ExportService")

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPORT_DIR = BASE_DIR / "exports" / "for_google_drive"

def safe_copy(src, dst):
    """Atomic copy operation with logging"""
    try:
        if not os.path.exists(src):
            log.error(f"Source file missing: {src}")
            raise FileNotFoundError(f"{src} not found")
            
        shutil.copy2(src, dst)
        log.info(f"Successfully copied {src} to {dst}")
        
    except PermissionError:
        log.critical(f"Permission denied writing to {dst}. Check folder permissions.")
        raise
    except Exception as e:
        log.error(f"Unexpected copy error: {str(e)}", exc_info=True)
        raise

def prepare_exports():
    log.info("Starting Batch Export Process")
    
    try:
        # Create export directory
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        log.info(f"Export directory ready: {EXPORT_DIR}")
        
        # Export compliance report
        compliance_src = PROCESSED_DIR / "compliance_report"
        if compliance_src.exists():
            parquet_files = list(compliance_src.glob("*.parquet"))
            if parquet_files:
                df = pd.read_parquet(parquet_files[0])
                csv_path = EXPORT_DIR / "compliance_report.csv"
                df.to_csv(csv_path, index=False)
                log.info(f"Exported compliance report: {len(df)} rows")
            else:
                log.warning("No compliance parquet files found")
        
        # Export market analytics
        market_src = PROCESSED_DIR / "market_analytics"
        if market_src.exists():
            parquet_files = list(market_src.rglob("*.parquet"))
            if parquet_files:
                dfs = [pd.read_parquet(f) for f in parquet_files]
                df = pd.concat(dfs, ignore_index=True)
                csv_path = EXPORT_DIR / "market_analytics.csv"
                df.to_csv(csv_path, index=False)
                log.info(f"Exported market analytics: {len(df)} rows")
            else:
                log.warning("No market analytics parquet files found")
        
        log.info("Batch Export Completed Successfully")
        
    except Exception as e:
        log.critical("Pipeline Halted due to unrecoverable error.", exc_info=True)
        print(f"!! ALERT: EXPORT PIPELINE FAILURE !! - {str(e)}")
        exit(1)

if __name__ == "__main__":
    prepare_exports()

import os
import csv
import random
import sys
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.logger import get_logger

log = get_logger("MockDataGenerator")

# Initialize Faker
fake = Faker('en_US')

# Configuration
RAW_DATA_PATH = "data/raw"
NUM_CONTRACTS = 50
NUM_MARKET_RECORDS = 200

def generate_market_csv():
    """Generates structured CSV data simulating property sales."""
    try:
        log.info("Generating market data CSV")
        regions = ['Sandton', 'Rosebank', 'Midrand', 'Fourways', 'Soweto']
        property_types = ['Apartment', 'House', 'Cluster', 'Townhouse']
        
        filepath = os.path.join(RAW_DATA_PATH, "market_data", "jhb_sales_history.csv")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sale_id', 'date', 'region', 'suburb', 'property_type', 'price_zar', 'sq_meters'])
            
            for _ in range(NUM_MARKET_RECORDS):
                region = random.choice(regions)
                sq_m = random.randint(45, 500)
                price_per_sqm = random.randint(8000, 25000)
                price = sq_m * price_per_sqm
                
                writer.writerow([
                    fake.uuid4(),
                    fake.date_between(start_date='-2y', end_date='today'),
                    region,
                    fake.city(),
                    random.choice(property_types),
                    price,
                    sq_m
                ])
        
        log.info(f"Generated {NUM_MARKET_RECORDS} market records at {filepath}")
        
    except PermissionError:
        log.critical(f"Permission denied writing to {filepath}")
        print(f"!! ALERT: DATA GENERATION FAILURE !! - Permission denied")
        exit(1)
    except Exception as e:
        log.error("Market data generation failed", exc_info=True)
        print(f"!! ALERT: DATA GENERATION FAILURE !! - {str(e)}")
        exit(1)

def generate_lease_contracts():
    """Generates unstructured text files simulating lease agreements."""
    try:
        log.info("Generating lease contracts")
        filepath = os.path.join(RAW_DATA_PATH, "contracts")
        os.makedirs(filepath, exist_ok=True)
        
        for i in range(NUM_CONTRACTS):
            is_compliant = random.choice([True, True, False])
            
            filename = f"lease_agreement_{i}_{fake.date_this_year()}.txt"
            full_path = os.path.join(filepath, filename)
            
            with open(full_path, 'w') as f:
                f.write(f"LEASE AGREEMENT\n")
                f.write(f"Date: {fake.date_this_year()}\n")
                f.write(f"Landlord: {fake.name()}\n")
                f.write(f"Tenant: {fake.name()}\n")
                f.write(f"Property: {fake.address()}\n\n")
                f.write("TERMS AND CONDITIONS:\n")
                f.write("1. Rent shall be paid on the 1st of every month.\n")
                f.write("2. The tenant agrees to maintain the property.\n")
                
                if is_compliant:
                    f.write("\nCOMPLIANCE CLAUSE:\n")
                    f.write("The Landlord warrants that the Property is compliant with the Property Practitioners Act.\n")
                    f.write("A 'Defect Disclosure Form' has been signed and attached hereto.\n")
                    f.write("FICA documents for the Tenant have been verified.\n")
                else:
                    f.write("\nNOTE: This is a standard draft agreement.\n")
        
        log.info(f"Generated {NUM_CONTRACTS} lease contracts in {filepath}")
        
    except PermissionError:
        log.critical(f"Permission denied writing to {filepath}")
        print(f"!! ALERT: DATA GENERATION FAILURE !! - Permission denied")
        exit(1)
    except Exception as e:
        log.error("Lease contract generation failed", exc_info=True)
        print(f"!! ALERT: DATA GENERATION FAILURE !! - {str(e)}")
        exit(1)

if __name__ == "__main__":
    try:
        log.info("Starting Data Generation")
        generate_market_csv()
        generate_lease_contracts()
        log.info("Data Generation Complete")
    except Exception as e:
        log.critical("Data generation failed", exc_info=True)
        exit(1)

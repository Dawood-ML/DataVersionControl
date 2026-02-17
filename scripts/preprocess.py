import pandas as pd
import numpy as np
from pathlib import Path

INPUT_PATH  = 'data/raw/customers.csv'
OUTPUT_PATH = 'data/processed/customers_cleaned.csv'

def preprocess_data(input_path: str, output_path: str):
    df = pd.read_csv(input_path)

    initial_count = len(df)
    print("Dropping duplicate values")
    df = df.drop_duplicates(subset=['customer_id'])
    print(f"Removed duplicate values : {initial_count - len(df)}")

    # Missing values
    missing_before = df.isnull().sum().sum()

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"   Filled {col} missing values with median: {median_val:.2f}")
    
    missing_after = df.isnull().sum().sum()
    print(f"\n🔧 Handled {missing_before - missing_after} missing values")
    string_cols = df.select_dtypes(include=['object']).columns
    df.drop(columns=string_cols, inplace=True)
    print(f"   Dropped {len(string_cols)} string columns")
    print(f"Now any string or object dtype columns? : {df.select_dtypes(include=['object']).columns}")
    # WHAT: Create derived features
    # WHY: Better features = better model
    # WHEN: Feature engineering phase
    # WHEN NOT: If baseline model only
    # ALTERNATIVE: Create during training (couples code)
    print(f"\n✨ Creating derived features")
    
    # Average monthly charges
    df['avg_monthly_charge'] = df['total_charges'] / (df['tenure_months'] + 1)
    
    # Customer lifetime value estimate
    df['estimated_lifetime_value'] = df['monthly_charges'] * df['tenure_months']
    
    # Product usage intensity
    df['products_per_tenure_month'] = df['num_products'] / (df['tenure_months'] + 1)
    
    print(f"   Created 3 new features")
    
    # WHAT: Ensure output directory exists
    # WHY: Prevent file not found errors
    # WHEN: Before saving
    # WHEN NOT: If directory guaranteed to exist
    # ALTERNATIVE: Manual directory creation
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # WHAT: Save processed data
    # WHY: DVC tracks this as output
    # WHEN: End of preprocessing
    # WHEN NOT: If passing data in memory (not pipeline)
    # ALTERNATIVE: Return DataFrame (doesn't work with DVC)
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved processed data to: {output_path}")
    print(f"   Final records: {len(df):,}")
    print(f"   Final columns: {len(df.columns)}")
    print("="*60)

if __name__ == "__main__":
    preprocess_data(INPUT_PATH, OUTPUT_PATH)



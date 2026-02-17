import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/customers.csv')

print("="*60)
print("DATASET UPDATE: V1 → V2")
print("="*60)
print(f"\n📊 V1 Stats:")
print(f"   Records: {len(df)}")
print(f"   Churn rate: {df['churn'].mean():.1%}")
print(f"   Age range: {df['age'].min()}-{df['age'].max()}")

# WHAT: Remove outliers (extreme ages)
# WHY: Clean data for better model performance
# WHEN: Data cleaning phase
# WHEN NOT: If outliers are valid
# ALTERNATIVE: Keep all data
print(f"\n🧹 Cleaning: Remove age outliers (>75)")
df = df[df['age'] <= 75]
print(f"   Removed: {10000 - len(df)} records")


print(f"\n➕ Adding: 2,000 new customer records")
np.random.seed(43)  # Different seed for new data
new_records = {
    'customer_id': range(10001, 12001),
    'age': np.random.randint(18, 75, 2000),
    'tenure_months': np.random.randint(0, 120, 2000),
    'monthly_charges': np.random.uniform(20, 150, 2000),
    'total_charges': np.random.uniform(100, 10000, 2000),
    'num_products': np.random.randint(1, 5, 2000),
    'has_phone': np.random.choice([0, 1], 2000),
    'has_internet': np.random.choice([0, 1], 2000),
    'contract_type': np.random.choice(['month', 'year', 'two_year'], 2000),
    'payment_method': np.random.choice(['credit', 'debit', 'bank', 'mail'], 2000),
    'churn': np.random.binomial(1, 0.25, 2000)  # 25% churn (lower)
}

df_new = pd.DataFrame(new_records)
df = pd.concat([df, df_new], ignore_index=True)

# WHAT: Save updated dataset
# WHY: Overwrite old file with new version
# WHEN: Dataset update complete
# WHEN NOT: If want to keep both versions separately
# ALTERNATIVE: Save as customers_v2.csv (bad practice)
df.to_csv('data/raw/customers.csv', index=False)

print(f"\n📊 V2 Stats:")
print(f"   Records: {len(df)}")
print(f"   Churn rate: {df['churn'].mean():.1%}")
print(f"   Age range: {df['age'].min()}-{df['age'].max()}")

print(f"\n✅ Dataset updated and saved to: data/raw/customers.csv")
print("="*60)
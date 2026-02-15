import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 10000

data = {
    'customer_id': range(1, n_samples + 1),
    'age': np.random.randint(18, 80, n_samples),
    'tenure_months': np.random.randint(0, 120, n_samples),
    'monthly_charges': np.random.uniform(20, 150, n_samples),
    'total_charges': np.random.uniform(100, 10000, n_samples),
    'num_products': np.random.randint(1, 5, n_samples),
    'has_phone': np.random.choice([0, 1], n_samples),
    'has_internet': np.random.choice([0, 1], n_samples),
    'contract_type': np.random.choice(['month', 'year', 'two_year'], n_samples),
    'payment_method': np.random.choice(['credit', 'debit', 'bank', 'mail'], n_samples),
    'churn': np.random.binomial(1, 0.3, n_samples)  # 30% churn rate
}

df = pd.DataFrame(data)
output_path = 'data/raw/customers.csv'
df.to_csv(output_path, index=False)

print(f"✅ Generated {len(df)} customer records")
print(f"📁 Saved to: {output_path}")
print(f"📊 File size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"📈 Churn rate: {df['churn'].mean():.1%}")
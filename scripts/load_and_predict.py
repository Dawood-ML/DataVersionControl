# This is what inference / serving code looks like
import mlflow.sklearn
import pandas as pd
import numpy as np

MODEL_NAME = "customer-churn-classifier"


# WHAT: Load model using the @champion alias instead of a version number
# WHY: When you promote v2 to champion, THIS code automatically serves v2
#      without ANY code change. The alias is the indirection layer.
# WHEN: Always load by alias in production code. Never hardcode version numbers.
# WHEN NOT: In debugging/analysis, loading by version is fine ("show me v1's predictions")
# ALTERNATIVE: mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/1") - hardcoded, brittle

model_uri = f"models:/{MODEL_NAME}@champion"
model = mlflow.sklearn.load_model(model_uri)

print(f"Loaded model from URI: {model_uri}")
print(f"Model type: {type(model).__name__}")

# Simulate inference on new data
sample_data = pd.read_csv("/home/dawood-ml/DataVersionControl/data/processed/customers_cleaned.csv").drop("churn", axis=1).head(5)
predictions = model.predict(sample_data)
probabilities = model.predict_proba(sample_data)[:, 1]

print(f"\nSample predictions:")
for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
    label = "CHURN" if pred == 1 else "STAY"
    print(f"  Customer {i+1}: {label} (confidence: {prob:.3f})")

    
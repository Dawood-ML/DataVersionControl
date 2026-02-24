import mlflow
from mlflow import MlflowClient


client = MlflowClient()

MODEL_NAME = "customer-churn-classifier"

# Get all models of a registered model
# Before you promote anything, check what exists and what aliasses are assigned

versions = client.search_model_versions(f"name='{MODEL_NAME}'")

print(f"Model: {MODEL_NAME}")
print(f"{'='*50}")
for v in versions:
    print(f"  Version {v.version}")
    print(f"    Run ID:    {v.run_id}")
    print(f"    Aliases:   {v.aliases}")
    print(f"    Status:    {v.status}")
    print(f"    Created:   {v.creation_timestamp}")
    print()

# Set aliases to versions
# Set alias @champion on verion 1

client.set_registered_model_alias(
    name=MODEL_NAME,
    alias='champion',
    version='1'
)

print(f"Set champion alis to v1 of churn model")

client.update_registered_model(
    name=MODEL_NAME,
    description=
    
        (
        "Random Forest classifier for predicting customer churn. "
        "Trained on telecom dataset. Target metric: ROC AUC > 0.75. "
        "Owner: Dawood. Use @champion alias for production inference."
    )
    
)

# model level tags (searchable meta data)
# Enables querying across models in large orgs

client.set_registered_model_tag(MODEL_NAME, key="team", value="ml-platform")
client.set_registered_model_tag(MODEL_NAME, key='domain', value="customer_churn")
client.set_registered_model_tag(MODEL_NAME, key="framework", value="sklearn")
client.set_registered_model_tag(MODEL_NAME, key="task", value="binary_classification")

# Version level description
# Each version should document what changed from the previous version
client.update_model_version(
    name=MODEL_NAME,
    version="1",
    description=(
        "Baseline model. n_estimators=150, max_depth=12. "
        "ROC AUC: 0.764 on v1 data. class_weight=balanced for imbalanced classes."
        )
)
print(f"✅ Added descriptions and tags")
print(f"\nFinal state:")
versions = client.search_model_versions(f"name='{MODEL_NAME}'")
for v in versions:
    print(f"  v{v.version} | aliases={v.aliases} | {v.description[:60]}...")


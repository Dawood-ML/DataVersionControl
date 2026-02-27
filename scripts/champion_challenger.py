
# Simulates a real model promotion workflow
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from mlflow import MlflowClient

data = pd.read_csv("data/processed/customers_cleaned.csv")
X = data.drop("churn", axis=1)
y = data["churn"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
client = MlflowClient()

MODEL_NAME = "customer-churn-classifier"

mlflow.set_experiment("customer-churn-prediction")


# Step 1
print("Training challenger model (Gradient Boosting)...")

with mlflow.start_run(run_name="GB-challenger-v2") as run:
    mlflow.set_tags(
        {
        "model_type": "gradient_boosting",
        "purpose": "challenger",
        "challenger_to": "v1"
        }
    )
    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "random_state": 42
    }

    mlflow.log_params(params)

    challenger = GradientBoostingClassifier(**params)
    challenger.fit(X_train, y_train)

    challenger_prob = challenger.predict_proba(X_test)[:, 1]
    challenger_roc = roc_auc_score(y_test, challenger_prob)
    mlflow.log_metric("roc_auc", challenger_roc)

    mlflow.sklearn.log_model(
        sk_model=challenger,
        artifact_path='model',
        registered_model_name=MODEL_NAME
    )
    challenger_version = client.search_model_versions(
        f"name='{MODEL_NAME}'"
    )

    # Get the latest version (jsut registered)
    latest_version = max([int(v.version) for v in challenger_version])

    print(f"Challenger registered as version {latest_version}")
    print(f"Challenger ROC AUC: {challenger_roc:.4f}")


# step 2 (Get champions performance to compare)
# Load current champion model to get it's metrics from the tracking server
# we need an apples to apples comparison before any promotion decision


champion_model_info = client.get_model_version_by_alias(name=MODEL_NAME, alias='champion')
champion_run_id  = champion_model_info.run_id

champion_run = client.get_run(champion_run_id)
champion_roc = champion_run.data.metrics.get('roc_auc', 0)

print(f"\nChampion (v{champion_model_info.version}) ROC AUC : {champion_roc}")
print(f"Challenger (v{latest_version}) ROC AUC: {challenger_roc}")

# Step : 3
# Defining a minimum improvement threshold for improvement
#  Noise in evaluation means a model 0.001 better isn't actually better
#      Require meaningful improvement to justify the risk of a model swap
# WHEN: Always have a threshold. Never promote based on raw better/worse alone.

IMPROVEMENT_THRESHOLD = 0.005 # the challenger must beat champion by 0.5%

improvement = challenger_roc - champion_roc
print(f"\nImprovement  : {improvement}")

if improvement >= IMPROVEMENT_THRESHOLD:
    print(f"Challenger beats champion by {improvement:.4f} --- promoted")

    client.set_registered_model_alias(
        name = MODEL_NAME,
        alias='champion',
        version=str(latest_version)
    )
    client.update_model_version(
        name=MODEL_NAME,
        version=champion_model_info.version,
        description=f"Demoted from champion. Replaced by v{latest_version}. ROC AUC was {champion_roc:.4f}."
    )

    print(f" v{latest_version} is now @champion")
    print(f" v{champion_model_info.version} demoted (alias removed automatically)")

else:
    print(f" Challenger improvement insufficient ({improvement:.4f} < {IMPROVEMENT_THRESHOLD})")
    print(f" Current champion (v{champion_model_info.version}) retained")

    # tag challenger as rejected so you know why it wasn't promoted
    client.set_model_version_tag(
        name=MODEL_NAME,
        version=str(latest_version),
        key='pomotion_decision',
        value=f"rejected — improvement {improvement:.4f} below threshold {IMPROVEMENT_THRESHOLD}"
    )

print(f"\n{'='*50}")
print("REGISTRY STATE AFTER DECISION:")
print(f"{'='*50}")
all_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
for v in sorted(all_versions, key=lambda x: int(x.version)):
    alias_str = f" ← @{', @'.join(v.aliases)}" if v.aliases else ""
    print(f"  v{v.version}{alias_str}")
    if v.description:
        print(f"    {v.description[:80]}...")
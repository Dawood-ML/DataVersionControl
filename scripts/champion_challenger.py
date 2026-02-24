
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

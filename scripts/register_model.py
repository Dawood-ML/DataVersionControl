import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score

# ── Load data ──────────────────────────────────────────────────────────────────
data = pd.read_csv("data/processed/customers_cleaned.csv")
X = data.drop("churn", axis=1)
y = data["churn"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

mlflow.set_experiment("customer-churn-prediction")


with mlflow.start_run(run_name="rf_registry_candidate") as run:
    mlflow.set_tags({
        "model_type": "random-forest",
        "data_version": "v1",
        "purpose": "registry_Candidate",
        "engineer": "Muhammad Dawood"    
    })

    params = {
        "n_estimators": 150,
        "max_depth": 12,
        "min_samples_split":5,
        "class_weight":"balanced",
        "random_state":42
    }

    mlflow.log_params(params)

    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob)
    }

    mlflow.log_metrics(metrics)

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path='model',
        registered_model_name="customer-churn-classifier"
    )
    print(f"Model registered as 'customer-churn-classifier'")
    print(f"ROC AUC: {metrics['roc_auc']:.3f}")
    print(f"Run ID: {run.info.run_id}")
    
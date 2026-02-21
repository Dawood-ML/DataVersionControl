import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    recall_score,
    f1_score,
    precision_score
)
from pathlib import Path

DATA_PATH = Path("/home/dawood-ml/DataVersionControl/data/processed/customers_cleaned.csv")

df = pd.read_csv(DATA_PATH)

print("data loaded successfully")

target_col = "churn"
X = df.drop(columns=[target_col])
y = df[target_col]

# Handle non-numeric columns
X = pd.get_dummies(X, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("No problems so far")

# --- Define experiment configurations to test ---
# WHAT: A list of hyperparameter combinations to try
# WHY: Systematic > random guessing. You can justify your final choice.
configs = [
    {"n_estimators": 50,  "max_depth": 3,    "min_samples_leaf": 1, "run_name" : "rf_50_leaves_3_depth"},
    {"n_estimators": 50,  "max_depth": 5,    "min_samples_leaf": 1, "run_name" : "rf_50_leaves_5_depth"},
    {"n_estimators": 50,  "max_depth": 10,   "min_samples_leaf": 2, "run_name" : "rf_50_leaves_10_depth"},
    {"n_estimators": 100, "max_depth": 3,    "min_samples_leaf": 1, "run_name" : "rf_100_leaves_3_depth"},
    {"n_estimators": 100, "max_depth": 5,    "min_samples_leaf": 1, "run_name" : "rf_100_leaves_5_depth"},
    {"n_estimators": 100, "max_depth": 10,   "min_samples_leaf": 2, "run_name" : "rf_100_leaves_10_depth"},
    {"n_estimators": 200, "max_depth": 5,    "min_samples_leaf": 1, "run_name" : "rf_200_leaves_5_depth"},
    {"n_estimators": 200, "max_depth": 10,   "min_samples_leaf": 2, "run_name" : "rf_200_leaves_10_depth"},
    {"n_estimators": 200, "max_depth": None, "min_samples_leaf": 4, "run_name" : "rf_200_leaves_unlimited"},  # None = unlimited depth
    {"n_estimators": 300, "max_depth": 10,   "min_samples_leaf": 2, "run_name" : "rf_300_leaves_10_depth"},
]

mlflow.set_experiment("churn-model-experiment-latest")

print(f"\nRunning {len(configs)} experiments...")

results = []

for exp in configs:
    run_name = exp.pop("run_name")
    params = {**exp, "class_weight": "balanced", "random_state": 42}

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(params)

        model = RandomForestClassifier(
            **params,
            n_jobs=-1
            )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        preds = model.predict(X_test)
        proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy":  accuracy_score(y_test, preds),
            "roc_auc":   roc_auc_score(y_test, proba),
            "recall":    recall_score(y_test, preds),
            "precision": precision_score(y_test, preds),
            "f1":        f1_score(y_test, preds),
        }

        # Logg all the metrics
        mlflow.log_metrics(metrics)

        # Add a tag, tags are searchable labels, not numeric metrics
        mlflow.set_tag("model_type", "random_forest")
        mlflow.set_tag("dataset", "telco-churn")

        mlflow.sklearn.log_model(model, "model")

        results.append({"run": run_name, **metrics})
        # print(f"[{i+1:2d}/10] {run_name}")
        print(f"        accuracy={metrics['accuracy']:.4f}  roc_auc={metrics['roc_auc']:.4f}  recall={metrics['recall']:.4f}")

# --- Print local summary ---
print("\n" + "=" * 60)
print("EXPERIMENT SUMMARY")
print("=" * 60)

results_df = pd.DataFrame(results).sort_values("roc_auc", ascending=False)
print(results_df[["run", "accuracy", "roc_auc", "recall", "f1"]].to_string(index=False))

best = results_df.iloc[0]
print(f"\n🏆 Best by ROC AUC: {best['run']}")
print(f"   ROC AUC:  {best['roc_auc']:.4f}")
print(f"   Recall:   {best['recall']:.4f}")
print(f"   Accuracy: {best['accuracy']:.4f}")
print("\nOpen MLflow UI to compare visually: uv run mlflow ui")
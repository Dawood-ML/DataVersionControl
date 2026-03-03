import mlflow
import pandas as pd
import numpy as np
import pickle
import json
import yaml
import matplotlib.pyplot as plt
import os
from pathlib import Path
from sklearn.metrics import (
    roc_auc_score, accuracy_score, recall_score,
    f1_score, ConfusionMatrixDisplay, RocCurveDisplay,
    classification_report
)
from mlflow import MlflowClient

# load parameters
with open('params.yaml') as f:
    params = yaml.safe_load(f)

mlflow_params = params['mlflow']
data_params   = params['data']

# load model and data
with open('models/random_forest.pkl','rb') as f:
    model = pickle.load(f)

data = pd.read_csv(data_params['data_path'])
target = data_params["target_column"]
X = data.drop(target, axis=1)
y = data[target]
print("I work hete")

from sklearn.model_selection import train_test_split
_, X_test, _, y_test = train_test_split(
    X, y,
    test_size=data_params["test_size"],
    random_state=data_params["random_state"],
    stratify=y
)

run_id_path = "metrics/mlflow_run_id.txt"
if not os.path.exists(run_id_path):
    raise RuntimeError(
        "metrics/mlflow_run_id.txt not found. "
        "Run train.py before evaluate.py."
    )
with open(run_id_path) as f:
    run_id = f.read().strip()

print(f"resuming mlflow run : {run_id}")

# mlflow.start_run with existing run_id resumes the existing run
# Appends to the existing one instead of creating a new one
with mlflow.start_run(run_id=run_id):
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    eval_metrics = {
        "eval_roc_auc":   round(roc_auc_score(y_test, y_prob), 4),
        "eval_accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "eval_recall":    round(recall_score(y_test, y_pred), 4),
        "eval_f1":        round(f1_score(y_test, y_pred), 4),
    }
    mlflow.log_metrics(eval_metrics)

    # ── Confusion matrix ───────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_test, y_pred, ax=ax,
        display_labels=["Stay", "Churn"],
        cmap="Blues"
    )
    ax.set_title(f"Confusion Matrix (ROC AUC: {eval_metrics['eval_roc_auc']:.3f})")
    plt.tight_layout()
    fig.savefig("confusion_matrix.png", dpi=120)
    mlflow.log_artifact("confusion_matrix.png")
    os.remove("confusion_matrix.png")
    plt.close()

    # ── ROC curve ─────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(y_test, y_prob, ax=ax, name="RF v1")
    ax.set_title("ROC Curve")
    ax.plot([0, 1], [0, 1], "k--", label="Random baseline")
    ax.legend()
    plt.tight_layout()
    fig.savefig("roc_curve.png", dpi=120)
    mlflow.log_artifact("roc_curve.png")
    os.remove("roc_curve.png")
    plt.close()

    # ── Feature importance plot ────────────────────────────────────────────────
    feature_importance = pd.Series(
        model.feature_importances_,
        index=X_test.columns
    ).sort_values(ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(8, 6))
    feature_importance.plot(kind="barh", ax=ax, color="steelblue")
    ax.invert_yaxis()
    ax.set_xlabel("Importance")
    ax.set_title("Top 15 Feature Importances")
    plt.tight_layout()
    fig.savefig("feature_importance.png", dpi=120)
    mlflow.log_artifact("feature_importance.png")
    os.remove("feature_importance.png")
    plt.close()

    # ── Classification report ──────────────────────────────────────────────────
    report = classification_report(y_test, y_pred, target_names=["Stay", "Churn"])
    mlflow.log_text(report, "classification_report.txt")

    # Save eval metrics for Dvc
    Path('metrics').mkdir(exist_ok=True)
    with open('metrics/eval_metrics.json', 'w') as f:
              json.dump(eval_metrics, f, indent=2)

    # Champion challenger decision
    client = MlflowClient()
    MODEL_NAME = mlflow_params["model_registry_name"]
    THRESHOLD = mlflow_params["promotion_threshold"]
    new_roc = eval_metrics["eval_roc_auc"]

    # Get current champion ROC if one exists
    try:
        champion_info = client.get_model_version_by_alias(MODEL_NAME, alias='champion')
        champion_run  = client.get_run(champion_info.run_id)
        # Try eval roc_auc first then fall to train roc auc
        champion_roc = champion_run.data.metrics.get(
             'eval_roc_auc',
             champion_run.data.metrics.get('roc_auc', 0)
        )

        improvement = new_roc - champion_roc
        print(f"\nChampion (v{champion_info.version}) ROC AUC: {champion_roc:.4f}")
        print(f"This run ROC AUC:                     {new_roc:.4f}")
        print(f"Improvement:                          {improvement:+.4f}")

        if improvement >= THRESHOLD:
             # Get the version that was just registered in train.py
            versions = client.search_model_versions(f"name='{MODEL_NAME}'")
            latest_version = max(int(v.version) for v in versions)

            client.set_registered_model_alias(MODEL_NAME,alias='champion', version=str(latest_version))
            client.update_model_version(
                 name=MODEL_NAME,
                 version=latest_version,
                 description=(
                    f"Promoted to champion. ROC AUC: {new_roc:.4f} "
                    f"(+{improvement:.4f} vs previous champion v{champion_info.version})"
                )
            )
            mlflow.set_tag("promotion_decision", "promoted_to_champion")
            print(f"\n✅ PROMOTED: v{latest_version} is new @champion")

        else:
            versions = client.search_model_versions(f"name='{MODEL_NAME}'")
            latest_version = max(int(v.version) for v in versions)
            client.set_model_version_tag(
                MODEL_NAME, str(latest_version),
                "promotion_decision",
                f"rejected — delta {improvement:.4f} below threshold {THRESHOLD}"
            )
            mlflow.set_tag("promotion_decision", f"rejected_delta_{improvement:.4f}")
            print(f"\n❌ NOT PROMOTED: improvement {improvement:.4f} < threshold {THRESHOLD}")
            print(f"   Champion remains v{champion_info.version}")

    except mlflow.exceptions.MlflowException:
        # No champion exists yet — first run, crown it automatically
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        latest_version = max(int(v.version) for v in versions)
        client.set_registered_model_alias(MODEL_NAME, "champion", str(latest_version))
        mlflow.set_tag("promotion_decision", "first_champion")
        print(f"\n👑 FIRST CHAMPION: v{latest_version} crowned as @champion (no previous champion)")

    print(f"\n{'='*55}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*55}")
    for k, v in eval_metrics.items():
        print(f"  {k:<20} {v:.4f}")
    print(f"{'='*55}")
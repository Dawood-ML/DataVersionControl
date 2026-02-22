import mlflow
import mlflow.sklearn
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, ConfusionMatrixDisplay,
    RocCurveDisplay, classification_report
)
import os



data = pd.read_csv("/home/dawood-ml/DataVersionControl/data/processed/customers_cleaned.csv")
X = data.drop("churn", axis=1)
y = data["churn"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


mlflow.set_experiment("customer_churn_prediction")


with mlflow.start_run(run_name="rf_with_artifacts"):
    params = {"n_estimators": 100, "max_depth": 10, "class_weight": "balanced", "random_state": 42}
    mlflow.log_params(params)
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    roc = roc_auc_score(y_test, y_prob)

    mlflow.log_metric("roc_auc", roc)

    # generate and log confusion metrix plot
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax)
    ax.set_title("Confusion Matrix")
    plt.tight_layout()

    cm_path = "confusion_matrix.png"
    fig.savefig(cm_path)
    mlflow.log_artifact(cm_path)
    os.remove(cm_path)
    plt.close()


    # --- Generate and log ROC curve ---
    fig, ax = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(y_test, y_prob, ax=ax)
    ax.set_title("ROC Curve")
    plt.tight_layout()

    roc_path = "roc_curve.png"
    fig.savefig(roc_path)
    mlflow.log_artifact(roc_path)
    os.remove(roc_path)
    plt.close()


    # --- Log classification report as text file ---
    report = classification_report(y_test, y_pred)
    report_path = "classification_report.txt"
    with open(report_path, "w") as f:
        f.write(report)

    mlflow.log_artifact(report_path)
    os.remove(report_path)

    # Cleaner way to log text directly (no temp file):
    mlflow.log_text(report, "classification_report_v2.txt")

    mlflow.sklearn.log_model(model, "model")
    print(f"ROC AUC: {roc:.3f} — artifacts logged")

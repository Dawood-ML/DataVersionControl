import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

data = pd.read_csv("/home/dawood-ml/DataVersionControl/data/processed/customers_cleaned.csv")
X = data.drop("churn", axis=1)
y = data["churn"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


mlflow.set_experiment("customer_churn_prediction")


# Run 1 : Random Forest
with mlflow.start_run(run_name="rf-prediction-candidate"):
    mlflow.set_tags({
        "model_type":"random forest",
        "data_version": "v1",
        "purpose":"production_candidate",
        "engineer": "dawood"
    })

    params = {
        "n_estimators": 100, 
        "max_depth": 10, 
        "class_weight": "balanced",
        "random_state": 42
    }
    mlflow.log_params(params)

    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    roc = roc_auc_score(y_test, y_prob)

    mlflow.log_metric('roc_auc', roc)
    mlflow.sklearn.log_model(model, "model")
    print(f"RF ROC AUC: {roc:.3f}")

# --- Run 2: Gradient Boosting (challenger) ---
with mlflow.start_run(run_name="gb-challenger"):
    mlflow.set_tags(
        {
            "model_type":'gradient_boosting',
            "data_version":"V1",
            "purpose": "challenger",
            "engineer":"dawood"
        }
    )

    params = {
        "n_estimators": 100, 
        "max_depth": 3, 
        "random_state": 42
    }

    mlflow.log_params(params)

    model = GradientBoostingClassifier(**params)
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    roc = roc_auc_score(y_test, y_prob)

    mlflow.log_metric('roc_auc', roc)
    mlflow.sklearn.log_model(model, "model")
    print(f"GB ROC AUC: {roc:.3f}")



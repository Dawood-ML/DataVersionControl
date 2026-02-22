import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


data = pd.read_csv("/home/dawood-ml/DataVersionControl/data/processed/customers_cleaned.csv")
X = data.drop("churn", axis=1)
y = data["churn"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlflow.set_experiment("churn-model-experiment-latest_autolooging")
mlflow.sklearn.autolog()

with mlflow.start_run(run_name='rf_auto_log'):
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )
     # WHAT: fit() triggers autologging automatically
    # WHY: MLflow patches sklearn's fit() to intercept and log everything
    model.fit(X_train, y_train)

    # Autolog captured: all params, training metrics, feature importances, model
    # You don't need to call log_params or log_model manually
    score = model.score(X_test, y_test)
    print(f"Test accuracy: {score:.3f}")


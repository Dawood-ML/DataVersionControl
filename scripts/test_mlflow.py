import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

# Dummy data for this test only
X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Tell mlflow which experiment this run belongs to
# creates the experiment if it didn't exist
mlflow.set_experiment("Churn-model-experiments")


# Start a run
# Opens a recording session where everything gets logged
with mlflow.start_run(run_name="rf_baseline"):

    # define parameters or constants
    n_estimators = 50000
    max_depth = 5000

    # Log parameters
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param('random_state', 42)

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        class_weight="balanced",  # important for imbalanced data
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, preds)
    roc_auc = roc_auc_score(y_test, proba)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("roc_auc", roc_auc)

    # Log the model
    # Saves the actual trained model as an artifact
    mlflow.sklearn.log_model(model, "random_forest_model")
    print(f"Run complete!")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  ROC AUC:  {roc_auc:.4f}")
    print(f"\nView in UI: run 'uv run mlflow ui' then open http://localhost:5000")

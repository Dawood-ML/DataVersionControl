import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import pickle
import yaml
import json
import os
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, recall_score, precision_score,
    roc_auc_score, f1_score
)

# load parameters from params.yaml
# read hyperparameters from shared file
#
# DVC watches this file for changes then re-runs this stage if any changes happen
with open('params.yaml') as f:
    params = yaml.safe_load(f)
    
model_params  = params['model']
data_params   = params['data']
mlflow_params = params['mlflow']

data = pd.read_csv("/home/dawood-ml/DataVersionControl/data/processed/customers_cleaned.csv")
target = data_params["target_column"]
X = data.drop(target, axis=1)
y = data[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=data_params["test_size"],
    random_state=data_params["random_state"],
    stratify=y
)
print("I work here")


# Set up mlflow experiment

mlflow.set_experiment(mlflow_params['experiment_name'])

# Get DVC data version info to attach to the mlflow run
dvc_data_hash = "unknown"

try:
    with open('dvc.lock') as f:
        dvc_lock = yaml.safe_load(f)
    # Navigate to the preprocessor stage output hash
    preprocess_outs = dvc_lock.get("stages", {}).get('preprocess', {}).get('outs', [])
    if preprocess_outs:
        dvc_data_hash = preprocess_outs[0].get('md5')

except FileNotFoundError:
    pass

# NOw Train inside the MLFLOW run
with mlflow.start_run(run_name=f"dvc-pipeline-rf") as run:
    # Log everything that identifies this run. Data, Code, environment
    # to reproduce this exact workflow
    mlflow.set_tags({
        "model_type": "random_forest",
        "pipeline":"dvc",
        "data_hash": dvc_data_hash,
        "data_version": "v1",
        "engineer": "Dawood",
        "framework": 'sklearn'
    })

    # Log all hyper parameters from params.yaml
    mlflow.log_params({
        **model_params,
        "test_size": data_params['test_size'],
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test),
        "n_features": X_train.shape[1],
        "class_ratio": float(y_train.mean()) # Fraction of positive classes
    })
    # Train
    model = RandomForestClassifier(
        n_estimators= model_params['n_estimators'],
        max_depth= model_params['max_depth'],
        min_samples_split=model_params['min_sample_split'],
        min_samples_leaf=model_params['min_sample_leaf'],
        class_weight=model_params['class_weight'],
        random_state=model_params['random_state'],
        n_jobs=-1
    )
    model.fit(X_train,y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall":    round(recall_score(y_test, y_pred), 4),
        "f1":        round(f1_score(y_test, y_pred), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_prob), 4),
    }

    mlflow.log_metrics(metrics=metrics)

    # Log feature importances as a custom metric series
    feature_importances = dict(zip(X_train.columns,
                                   model.feature_importances_))
    top_features  = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]
    for feat_name, importance in top_features:
        mlflow.log_metric(f"Importances_{feat_name}", round(float(importance), 4))

    # Log model to mlflow
    # to define model signature, Input schema + output schema
    # MLFLOW will use this to validate inputs at serving time,
    #       catches schema mismatch before they cause failures in production
    from mlflow.models.signature import infer_signature
    signature = infer_signature(model_input=X_train,
                                model_output=model.predict(X_train))
    mlflow.sklearn.log_model(
        sk_model=model,
        name="model",
        signature=signature,
        input_example=X_train.head(3),
        registered_model_name=mlflow_params['model_registry_name']
    )

    # Save run id for evaluation
    Path('metrics').mkdir(exist_ok=True)
    with open("metrics/mlflow_run_id.txt", "w") as f:
        f.write(run.info.run_id)
    
    # Save metrics for DVC (DVC reads JSON not MLFLOW)
    #  MLflow metrics are for the UI. DVC metrics are for CLI comparison.
    #  Both systems get fed the same numbers.

    with open('metrics/train_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    # SAve model as pickle for DVC pipeline
    # Save model on disk so evaluation file can load it
    Path('models').mkdir(exist_ok=True)
    with open('models/random_forest.pkl', 'wb') as f:
        pickle.dump(model, f)

        print(f"\n{'='*55}")
    print(f"TRAINING COMPLETE")
    print(f"{'='*55}")
    print(f"  Run ID:    {run.info.run_id}")
    print(f"  Data hash: {dvc_data_hash}")
    print(f"  ROC AUC:   {metrics['roc_auc']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1:        {metrics['f1']:.4f}")
    print(f"{'='*55}")


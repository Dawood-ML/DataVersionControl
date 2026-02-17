"""
Model evaluation pipeline stage.

WHAT: Compute performance metrics
WHY: Assess model quality before deployment
WHEN: After training
WHEN NOT: During training (use validation set)
ALTERNATIVE: Evaluate inline in train.py (couples concerns)
"""

import pandas as pd
import pickle
import json
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from pathlib import Path

# WHAT: Input and output paths
# WHY: DVC tracks these
# WHEN: Pipeline stage
# WHEN NOT: Ad-hoc evaluation
# ALTERNATIVE: None
DATA_PATH = 'data/processed/customers_cleaned.csv'
MODEL_PATH = 'models/model.pkl'
SCALER_PATH = 'models/scaler.pkl'
METRICS_PATH = 'metrics.json'

def evaluate_model(data_path: str, model_path: str, scaler_path: str, metrics_path: str):
    """
    Evaluate trained model.
    
    WHAT: Load model, compute metrics, save results
    WHY: Quantify model performance
    WHEN: After training
    WHEN NOT: During training
    ALTERNATIVE: Manual evaluation
    """
    print("="*60)
    print("EVALUATING MODEL")
    print("="*60)
    
    # WHAT: Load data
    # WHY: Need test set for evaluation
    # WHEN: Start of evaluation
    # WHEN NOT: If using separate test file
    # ALTERNATIVE: Load test set directly
    print(f"\n📂 Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Recreate train/test split (same random_state as training)
    from sklearn.model_selection import train_test_split
    X = df.drop(columns=['customer_id', 'churn'])
    y = df['churn']
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Test set: {len(X_test):,} samples")
    
    # WHAT: Load model and scaler
    # WHY: Need trained artifacts
    # WHEN: Before prediction
    # WHEN NOT: If training and evaluating in same script
    # ALTERNATIVE: None
    print(f"\n📦 Loading model from: {model_path}")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"📦 Loading scaler from: {scaler_path}")
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # WHAT: Scale test data
    # WHY: Must use same scaling as training
    # WHEN: Before prediction
    # WHEN NOT: If model doesn't need scaling
    # ALTERNATIVE: None - scaling must match training
    X_test_scaled = scaler.transform(X_test)
    
    # WHAT: Make predictions
    # WHY: Need predictions to evaluate
    # WHEN: After loading model
    # WHEN NOT: N/A
    # ALTERNATIVE: None
    print(f"\n🔮 Generating predictions")
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # WHAT: Compute metrics
    # WHY: Quantify model performance
    # WHEN: After predictions
    # WHEN NOT: Never skip evaluation
    # ALTERNATIVE: Different metrics (business-specific)
    print(f"\n📊 Computing metrics")
    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred)),
        'recall': float(recall_score(y_test, y_pred)),
        'f1_score': float(f1_score(y_test, y_pred)),
        'roc_auc': float(roc_auc_score(y_test, y_pred_proba))
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    metrics['confusion_matrix'] = {
        'true_negative': int(tn),
        'false_positive': int(fp),
        'false_negative': int(fn),
        'true_positive': int(tp)
    }
    
    # WHAT: Print metrics
    # WHY: Human-readable output
    # WHEN: After computation
    # WHEN NOT: Silent mode (logs only)
    # ALTERNATIVE: None - always show results
    print(f"\n📈 Results:")
    print(f"   Accuracy:  {metrics['accuracy']:.1%}")
    print(f"   Precision: {metrics['precision']:.1%}")
    print(f"   Recall:    {metrics['recall']:.1%}")
    print(f"   F1 Score:  {metrics['f1_score']:.1%}")
    print(f"   ROC AUC:   {metrics['roc_auc']:.3f}")
    print(f"\n   Confusion Matrix:")
    print(f"      TN: {tn:4d}  |  FP: {fp:4d}")
    print(f"      FN: {fn:4d}  |  TP: {tp:4d}")
    
    # WHAT: Save metrics to JSON
    # WHY: DVC can track and compare metrics
    # WHEN: End of evaluation
    # WHEN NOT: Throwaway experiments
    # ALTERNATIVE: CSV, YAML
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n💾 Saved metrics to: {metrics_path}")
    
    print("="*60)

if __name__ == "__main__":
    evaluate_model(DATA_PATH, MODEL_PATH, SCALER_PATH, METRICS_PATH)
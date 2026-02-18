"""
Model training pipeline stage.

WHAT: Train ML model on processed data
WHY: Create model artifact for deployment
WHEN: After preprocessing
WHEN NOT: For inference (load existing model)
ALTERNATIVE: Train in notebook (not reproducible)
"""

import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# WHAT: Input and output paths
# WHY: DVC tracks these
# WHEN: Pipeline stage
# WHEN NOT: Ad-hoc training
# ALTERNATIVE: Command-line arguments (more flexible, more complex)
INPUT_PATH = 'data/processed/customers_cleaned.csv'
MODEL_PATH = 'models/model.pkl'
SCALER_PATH = 'models/scaler.pkl'

# WHAT: Training hyperparameters
# WHY: Reproducibility (same params = same model)
# WHEN: Always define upfront
# WHEN NOT: For hyperparameter tuning (different flow)
# ALTERNATIVE: Config file (more scalable)
PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'random_state': 42,
    'class_weight': 'balanced',
    'n_jobs': -1,
    'test_size': 0.2
}

def train_model(input_path: str, model_path: str, scaler_path: str, params: dict):
    """
    Train Random Forest classifier.
    
    WHAT: Load data, train model, save artifacts
    WHY: Reproducible training
    WHEN: Pipeline execution
    WHEN NOT: Hyperparameter tuning
    ALTERNATIVE: Train manually (not reproducible)
    """
    print("="*60)
    print("TRAINING MODEL")
    print("="*60)
    
    # WHAT: Load processed data
    # WHY: Training needs clean data
    # WHEN: Start of training
    # WHEN NOT: If data in memory
    # ALTERNATIVE: None
    print(f"\n📂 Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"   Loaded {len(df):,} records")
    
    # WHAT: Separate features and target
    # WHY: X = inputs, y = output
    # WHEN: Before training
    # WHEN NOT: Unsupervised learning
    # ALTERNATIVE: None
    print(f"\n🎯 Preparing features and target")
    X = df.drop(columns=['customer_id', 'churn'])
    y = df['churn']
    print(f"   Features: {X.shape[1]}")
    print(f"   Samples: {len(X):,}")
    print(f"   Churn rate: {y.mean():.1%}")
    
    # WHAT: Train/test split
    # WHY: Evaluate model on unseen data
    # WHEN: Always split before training
    # WHEN NOT: Cross-validation (different approach)
    # ALTERNATIVE: K-fold CV (more robust)
    print(f"\n✂️ Splitting data (test size: {params['test_size']:.0%})")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=params['test_size'],
        random_state=params['random_state'],
        stratify=y
    )
    print(f"   Train: {len(X_train):,} samples")
    print(f"   Test: {len(X_test):,} samples")
    
    # WHAT: Scale features
    # WHY: Some features on different scales (age vs charges)
    # WHEN: Before training (especially for neural nets, SVM)
    # WHEN NOT: Tree-based models (optional but doesn't hurt)
    # ALTERNATIVE: Normalization, no scaling
    print(f"\n📊 Scaling features")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print(f"   Fitted StandardScaler on training data")
    
    # WHAT: Train model
    # WHY: Create model artifact
    # WHEN: After data prep
    # WHEN NOT: If loading pre-trained
    # ALTERNATIVE: Different algorithms (XGBoost, Neural Net)
    print(f"\n🤖 Training Random Forest")
    print(f"   Hyperparameters:")
    for key, value in params.items():
        if key != 'test_size':
            print(f"      {key}: {value}")
    
    model = RandomForestClassifier(
        n_estimators=params['n_estimators'],
        max_depth=params['max_depth'],
        min_samples_split=params['min_samples_split'],
        random_state=params['random_state'],
        class_weight=params['class_weight'],
        n_jobs=-1  # Use all CPU cores
    )
    
    model.fit(X_train_scaled, y_train)
    print(f"   Training complete!")
    
    # WHAT: Quick evaluation
    # WHY: Sanity check model isn't broken
    # WHEN: After training
    # WHEN NOT: Full evaluation in separate stage
    # ALTERNATIVE: None - always check
    train_acc = model.score(X_train_scaled, y_train)
    test_acc = model.score(X_test_scaled, y_test)
    print(f"\n📈 Quick evaluation:")
    print(f"   Train accuracy: {train_acc:.1%}")
    print(f"   Test accuracy: {test_acc:.1%}")
    
    if test_acc < 0.6:
        print(f"   ⚠️ WARNING: Test accuracy very low!")
    
    # WHAT: Save model and scaler
    # WHY: DVC tracks these as outputs
    # WHEN: End of training
    # WHEN NOT: Throwaway experiments
    # ALTERNATIVE: joblib (alternative to pickle)
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"\n💾 Saved model to: {model_path}")
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"💾 Saved scaler to: {scaler_path}")
    
    print("="*60)

if __name__ == "__main__":
    train_model(INPUT_PATH, MODEL_PATH, SCALER_PATH, PARAMS)
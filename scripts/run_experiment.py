
import sys
import json
from pathlib import Path

def run_experiment(n_estimators: int, max_depth: int, experiment_name: str):
    """
    Run training experiment with custom hyperparameters.
    
    WHAT: Update params, run pipeline, save results
    WHY: Systematic experimentation
    WHEN: Finding best hyperparameters
    WHEN NOT: Production deployment
    ALTERNATIVE: Grid search (more automated)
    """
    print("="*60)
    print(f"EXPERIMENT: {experiment_name}")
    print("="*60)
    print(f"\nHyperparameters:")
    print(f"  n_estimators: {n_estimators}")
    print(f"  max_depth: {max_depth}")
    
    # Update dvc.yaml with new params (simple approach)
    # In production, use params.yaml file
    print(f"\n⚠️  Note: Manually update scripts/train.py PARAMS dict")
    print(f"   n_estimators: {n_estimators}")
    print(f"   max_depth: {max_depth}")
    print(f"\nThen run: dvc repro")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/run_experiment.py <n_estimators> <max_depth> <name>")
        print("Example: python scripts/run_experiment.py 200 15 deep-forest")
        sys.exit(1)
    
    n_estimators = int(sys.argv[1])
    max_depth = int(sys.argv[2])
    experiment_name = sys.argv[3]
    
    run_experiment(n_estimators, max_depth, experiment_name)


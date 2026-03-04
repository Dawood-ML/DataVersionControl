# Customer Churn Prediction: Learning DVC and MLflow

**A hands-on educational project demonstrating MLOps fundamentals through data version control, experiment tracking, and model management—built on synthetic data for learning purposes.**

[![DVC](https://img.shields.io/badge/DVC-Data%20Version%20Control-blue)](https://dvc.org)
[![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-green)](https://mlflow.org)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)

---

## Project Overview

This repository serves as a practical exploration of MLOps tools, focusing on building a reproducible machine learning pipeline for predicting customer churn. It started with DVC for data versioning and pipeline orchestration, and has since expanded to integrate MLflow for experiment tracking, model registry, and advanced concepts like model aliases, champion/challenger patterns.

**Important Note:** This is purely an educational project using synthetic (fake) data generated for demonstration. It's not based on real-world datasets or intended for production use—think of it as a sandbox where I've experimented with these tools to deepen my understanding. The goal is to show how DVC and MLflow can work together in a grounded, step-by-step way, highlighting their strengths without overhyping the results.

Key elements:
- **Data versioning and pipelines** via DVC for reproducibility.
- **Experiment tracking and model management** via MLflow, including logging runs, registering models, and handling deployment patterns like champion/challenger.
- **Reproducible workflows:** Rebuild everything from Git commits.
- **Collaboration-friendly:** Easy sharing of data, models, and experiments.

Through this, I've learned how these tools make ML projects more organized and reliable, even in a simple setup like this.

---

## Current Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 69.8% |
| **Precision** | 54.2% |
| **Recall** | 67.8% |
| **F1 Score** | 60.2% |
| **ROC AUC** | 0.764 |

**Business Impact (Simulated):** The model identifies about 68% of potential churners, improving on a random baseline of 30%. These metrics come from experiments tracked in MLflow—feel free to explore variations in the UI.

---

## Tech Stack

### Core ML
- **scikit-learn** - Random Forest classifier
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### MLOps Tools
- **DVC** - Data version control + pipeline orchestration
- **MLflow** - Experiment tracking, model registry, and serving
- **Git** - Code version control
- **UV** - Python dependency management

### Pipeline Stages
1. **Preprocess** - Clean data, handle missing values, feature engineering (DVC-tracked).
2. **Train** - Train Random Forest with class balancing (logged to MLflow).
3. **Evaluate** - Compute metrics, confusion matrix (results in MLflow).
4. **Register Model** - Add trained models to MLflow registry with aliases (e.g., "champion" for production, "challenger" for testing).

---

## Quick Start

### Prerequisites
- Python 3.11+
- UV package manager ([install](https://github.com/astral-sh/uv))
- Git
- MLflow (installed via UV)

### Installation
```bash
# Clone repository
git clone https://github.com/Dawood-ML/DataVersionControl.git
cd DataVersionControl

# Install dependencies
uv sync

# Pull data from DVC remote
uv run dvc pull

# Start MLflow UI (optional, for viewing experiments)
uv run mlflow ui --host 0.0.0.0 &

# Run complete pipeline
uv run dvc repro
```

This runs the DVC pipeline, which now integrates MLflow for tracking. Check the MLflow UI at `http://localhost:5000` to see experiments.

---

## Project Structure
```
DataVersionControl/
├── LICENSE
├── README.md
├── data/
│   ├── raw/                    # Original synthetic data (DVC-tracked)                    
│   └── processed/              # Cleaned data (DVC-tracked)
├── scripts/
│   ├── champion_challenger.py
│   ├── compare_experiments.py
│   ├── compare_versions.py
│   ├── evaluate.py             # Model evaluation with MLflow
│   ├── generate_data.py
│   ├── load_and_predict.py
│   ├── manage_registry.py
│   ├── preprocess.py           # Data cleaning pipeline
│   ├── register_model.py       # MLflow model registry script
│   ├── run_experiment.py       # Helper for MLflow experiments
│   ├── show_data_history.py
│   ├── test_mlflow.py
│   ├── train.py                # Model training with MLflow logging
│   ├── train_autolog.py
│   ├── train_tagged.py
│   ├── train_with_artifacts.py
│   └── update_data_v2.py 
├── docs/                       # Documentation
├── models/                     # Trained models (DVC-tracked, also in MLflow)
│   ├── model.pkl
│   ├── random_forest.pkl
│   └── scaler.pkl
├── experiments/
│   └── README.md               # Manual experiment notes (supplemented by MLflow)
├── metrics/
│   ├── eval_metrics.json
│   ├── mlflow_run_id.txt
│   └── train_metrics.json
├── main.py
├── metrics.json                # Model metrics (DVC-tracked, also in MLflow)
├── mlflow.db
├── mlruns/                     # MLflow tracking artifacts (git-ignored)
├── params.yaml
├── pyproject.toml              # Python dependencies
└── uv.lock
├── dvc.lock                    # Pipeline lockfile
├── dvc.yaml                    # DVC pipeline definition

166 directories, 411 files
```

---

## Pipeline Visualization

### DVC + MLflow Integration
```
data/raw/customers.csv (synthetic)
         ↓
    [preprocess] (DVC)
         ↓
data/processed/customers_cleaned.csv
         ↓
      [train] (DVC + MLflow logging)
         ↓
   models/model.pkl (registered in MLflow)
         ↓
     [evaluate] (DVC + MLflow metrics)
         ↓
    metrics.json
```

### View DVC Pipeline
```bash
uv run dvc dag
```

### Run Pipeline
```bash
uv run dvc repro
```

DVC handles caching; MLflow logs runs automatically during train/evaluate.

---

## Model Development

### Current Approach
- **Algorithm:** Random Forest Classifier
- **Class Balancing:** `class_weight='balanced'`
- **Features:** 10 customer attributes + 3 derived features
- **Train/Test Split:** 80/20 with stratification

### Experiment Tracking with MLflow
All runs are logged to MLflow, including parameters, metrics, and artifacts. View in the UI to compare experiments.

### Model Registry
Models are registered in MLflow with stages (e.g., Staging, Production) and aliases like "champion" (current best) and "challenger" (new contender for A/B testing).

### Key Learning
**Initial Challenge:** Poor recall (0.3%) on imbalanced data.  
**Solution:** Added balancing and tracked iterations in MLflow.  
**Result:** 67.8% recall—a solid improvement, visible across experiment runs.

See [experiments/README.md](experiments/README.md) for notes, or MLflow UI for full details.

---

## Data Versioning with DVC

### Why DVC?
- ✅ Tracks dataset versions alongside code.
- ✅ Enables rollbacks and sharing without bloating Git.
- ✅ Ensures reproducibility in ML experiments.

### Example: Version Control
```bash
# Track new dataset version
uv run dvc add data/raw/customers.csv
git add data/raw/customers.csv.dvc
git commit -m "Update synthetic dataset v2"

# Pull exact data
git pull
uv run dvc pull
```

Integrates seamlessly with MLflow for end-to-end tracking.

---

## 🤝 Collaboration Workflow

### New Teammate Setup
```bash
git clone <repo-url>
uv sync
uv run dvc pull  # Get data
uv run mlflow ui &  # View experiments
uv run dvc repro # Run pipeline
```

### Make Changes
```bash
# Edit code or data
vim scripts/train.py

# Run and track
uv run dvc repro

# Push DVC artifacts
uv run dvc push

# Commit
git add dvc.lock scripts/train.py
git commit -m "New experiment with deeper trees"
git push
```

Share MLflow runs via the tracking server for team reviews.

---

## 🧪 Running Experiments

### With MLflow
Edit parameters in `scripts/train.py`:
```python
PARAMS = {
    'n_estimators': 200,
    'max_depth': 15,
    # ...
}
```

Run:
```bash
uv run dvc repro
uv run mlflow ui  # Compare runs
```

DVC caches unchanged stages; MLflow logs everything. Try registering a challenger model:
```bash
uv run python scripts/register_model.py --alias challenger
```

---

## 📝 MLOps Practices Demonstrated

### Data Management
- [x] Version control (DVC)
- [x] Lineage tracking
- [x] Remote storage
- [x] Rollback

### Experiment & Model Management
- [x] Tracking runs (MLflow)
- [x] Model registry with stages/aliases
- [x] Champion/challenger patterns
- [x] Metrics logging

### Pipeline Management
- [x] Reproducible pipelines (DVC + MLflow)
- [x] Caching and dependencies
- [x] Modular code

### Code Quality
- [x] Virtual environments (UV)
- [x] Git integration
- [x] Documentation

---

## 🔮 Future Improvements

### Model
- [ ] Hyperparameter tuning
- [ ] Advanced algorithms (e.g., XGBoost)
- [ ] Interpretability (SHAP)

### MLOps
- [ ] CI/CD (GitHub Actions)
- [ ] MLflow model serving
- [ ] A/B testing integration
- [ ] Monitoring

### Infrastructure
- [ ] Docker for consistency
- [ ] Cloud storage (S3)
- [ ] Full deployment (FastAPI/Kubernetes)

---

## 📚 Documentation

- [DVC Remotes](docs/dvc_remotes_explained.md)
- [DVC Workflow](docs/dvc_team_workflow.md)
- [DVC Cheatsheet](docs/dvc_commands_cheatsheet.md)
- [DVC Pipelines](docs/dvc_pipeline_concepts.md)
- [MLflow Basics](docs/mlflow_basics.md)  # New: Covering tracking, registry, etc.

---

## 🎓 Learning Outcomes

This project highlights:
1. **Data versioning** with DVC for reliable ML foundations.
2. **Experiment tracking** with MLflow to document iterations.
3. **Model management** including registries and patterns like champion/challenger.
4. **Integrated workflows** combining DVC and MLflow.
5. **Reproducibility and collaboration** in a simple, educational context.

**Core Insight:** Tools like DVC and MLflow make ML more approachable and structured, even for learning on synthetic data.

---

## 📄 License

MIT

---

## 👤 Author

**Dawood** - An ML enthusiast exploring MLOps through hands-on projects.

[GitHub](https://github.com/Dawood-ML) | [LinkedIn](https://www.linkedin.com/in/muhammad-dawood-khan-5a3292329/)

---

## 🙏 Acknowledgments

- DVC and MLflow teams for accessible tools.
- UV for efficient dependency handling.
- The MLOps community for sharing practical insights.

---

**⭐ If this helps your learning journey, consider starring the repo!**
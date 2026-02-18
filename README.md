# Customer Churn Prediction with DVC

**Production-ready ML pipeline with complete data version control and reproducible workflows.**

[![DVC](https://img.shields.io/badge/DVC-Data%20Version%20Control-blue)](https://dvc.org)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)

---

## Project Overview

Machine learning pipeline to predict customer churn with focus on:
- **Data versioning** (DVC tracks all data versions)
- **Reproducible pipelines** (One command rebuilds everything)
- **Remote storage** (Team can share data seamlessly)
- **Experiment tracking** (Every model iteration documented)

**Key Innovation:** Entire ML workflow (data → model) is reproducible from Git commits.

---

## Current Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 69.8% |
| **Precision** | 54.2% |
| **Recall** | 67.8% |
| **F1 Score** | 60.2% |
| **ROC AUC** | 0.764 |

**Business Impact:** Model catches 68% of churners vs 30% baseline (random).

---

## Tech Stack

### Core ML
- **scikit-learn** - Random Forest classifier
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### MLOps Tools
- **DVC** - Data version control + pipeline orchestration
- **Git** - Code version control
- **UV** - Python dependency management

### Pipeline Stages
1. **Preprocess** - Clean data, handle missing values, feature engineering
2. **Train** - Train Random Forest with class balancing
3. **Evaluate** - Compute metrics, confusion matrix

---

## Quick Start

### Prerequisites
- Python 3.11+
- UV package manager ([install](https://github.com/astral-sh/uv))
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/Dawood-ML/DataVersionControl.git
cd DataVersionControl

# Install dependencies
uv sync

# Pull data from DVC remote
uv run dvc pull

# Run complete ML pipeline
uv run dvc repro
```

**That's it!** Pipeline runs: preprocess → train → evaluate.

---

## Project Structure
```
DataVersionControl/
├── data/
│   ├── raw/                    # Original data (DVC-tracked)
│   └── processed/              # Cleaned data (DVC-tracked)
├── models/                     # Trained models (DVC-tracked)
│   ├── model.pkl
│   └── scaler.pkl
├── scripts/
│   ├── generate_data.py        # Synthetic data generation
│   ├── preprocess.py           # Data cleaning pipeline
│   ├── train.py                # Model training pipeline
│   ├── evaluate.py             # Model evaluation pipeline
│   └── run_experiment.py       # Experiment helper
├── experiments/
│   └── README.md               # Experiment log
├── docs/                       # Documentation
├── dvc.yaml                    # DVC pipeline definition
├── dvc.lock                    # Pipeline lockfile (exact hashes)
├── metrics.json                # Model metrics (tracked by DVC)
└── pyproject.toml              # Python dependencies
```

---

## DVC Pipeline

### Pipeline Visualization
```
data/raw/customers.csv
         ↓
    [preprocess]
         ↓
data/processed/customers_cleaned.csv
         ↓
      [train]
         ↓
   models/model.pkl
         ↓
     [evaluate]
         ↓
    metrics.json
```

### View Pipeline
```bash
uv run dvc dag
```

### Run Pipeline
```bash
uv run dvc repro
```

**Smart Caching:** Only reruns changed stages. If nothing changed, completes instantly.

---

## Model Development

### Current Approach
- **Algorithm:** Random Forest Classifier
- **Class Balancing:** `class_weight='balanced'`
- **Features:** 10 customer attributes + 3 derived features
- **Train/Test Split:** 80/20 with stratification

### Experiment Log
See [experiments/README.md](experiments/README.md) for full experiment history.

### Key Learning
**Problem:** Initial model had 0.3% recall (caught 2 churners out of 677)  
**Solution:** Added `class_weight='balanced'`  
**Result:** 67.8% recall (226x improvement!)

---

## Data Versioning

### Why DVC?
- ✅ Track dataset versions (like Git for data)
- ✅ Rollback to previous data versions
- ✅ Share large files without Git bloat
- ✅ Reproducible ML experiments

### Example: Version Control
```bash
# Track new dataset version
uv run dvc add data/raw/customers.csv
git add data/raw/customers.csv.dvc
git commit -m "Update dataset v2"

# Teammate gets exact same data
git pull
uv run dvc pull
```

### Rollback to Previous Version
```bash
# Go back to previous data version
git checkout HEAD~1 data/raw/customers.csv.dvc
uv run dvc checkout data/raw/customers.csv.dvc
```

---

## 🤝 Collaboration Workflow

### New Teammate Setup
```bash
git clone <repo-url>
uv sync
uv run dvc pull  # Download data from remote
uv run dvc repro # Run pipeline (uses cache if nothing changed)
```

### Make Changes
```bash
# Modify code or data
vim scripts/train.py

# Run pipeline
uv run dvc repro

# Push data artifacts
uv run dvc push

# Commit code + pipeline changes
git add dvc.lock scripts/train.py
git commit -m "Increase model depth"
git push
```

---

## 🧪 Running Experiments

### Try Different Hyperparameters

Edit `scripts/train.py`:
```python
PARAMS = {
    'n_estimators': 200,  # Increase from 100
    'max_depth': 15,       # Increase from 10
    # ...
}
```

Then run:
```bash
uv run dvc repro
uv run dvc metrics show
```

DVC only reruns `train` and `evaluate` stages (preprocessed data cached).

---

## 📝 MLOps Practices Demonstrated

### Data Management
- [x] Data version control (DVC)
- [x] Data lineage tracking
- [x] Remote storage backup
- [x] Data rollback capability

### Pipeline Management
- [x] Reproducible pipelines (dvc.yaml)
- [x] Dependency tracking
- [x] Smart caching (skip unchanged stages)
- [x] Metrics tracking

### Code Quality
- [x] Modular code structure
- [x] Virtual environment isolation (UV)
- [x] Dependency locking (uv.lock)
- [x] Git version control

### Documentation
- [x] Comprehensive README
- [x] Inline code comments (WHAT/WHY/WHEN)
- [x] Experiment logging
- [x] Architecture docs

---

## 🔮 Future Improvements

### Model
- [ ] Hyperparameter tuning (GridSearchCV)
- [ ] Try XGBoost/LightGBM
- [ ] Feature importance analysis
- [ ] SHAP values for interpretability

### MLOps
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Model registry (MLflow)
- [ ] A/B testing framework
- [ ] Production monitoring

### Infrastructure
- [ ] Migrate to S3 remote storage
- [ ] Containerization (Docker)
- [ ] API serving (FastAPI)
- [ ] Kubernetes deployment

---

## 📚 Documentation

- [DVC Remotes Explained](docs/dvc_remotes_explained.md)
- [DVC Team Workflow](docs/dvc_team_workflow.md)
- [DVC Commands Cheatsheet](docs/dvc_commands_cheatsheet.md)
- [DVC Pipeline Concepts](docs/dvc_pipeline_concepts.md)

---

## 🎓 Learning Outcomes

This project demonstrates:
1. **Data versioning** - Track datasets like code
2. **Pipeline automation** - One command runs entire workflow
3. **Reproducibility** - Same commit = same model
4. **Collaboration** - Team shares data seamlessly
5. **Experiment tracking** - Document all iterations

**Key Insight:** DVC makes ML projects reproducible and collaborative without cloud lock-in.

---

## 📄 License

MIT

---

## 👤 Author

**Dawood** - ML Engineer specializing in production MLOps

[GitHub](https://github.com/Dawood-ML) | [LinkedIn](https://www.linkedin.com/in/muhammad-dawood-khan-5a3292329/)

---

## 🙏 Acknowledgments

- DVC for making data version control accessible
- UV for blazing-fast Python dependency management
- The MLOps community for best practices

---

**⭐ Star this repo if you learned something!**
```

---

## PART 4: Final Polish (5 min)

### Add .gitattributes for Better Diffs

Create `.gitattributes`:
```
# Mark DVC files as binary (don't show diffs)
*.dvc binary
dvc.lock binary

# Python files are text
*.py text

# Markdown files are text
*.md text

# JSON files are text
*.json text

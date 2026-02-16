# Why DVC Pipelines?

## Problems with Manual Scripts

### Problem 1: Forget Steps
```bash
# You:
python generate_data.py
python train.py  # ← Forgot preprocess.py!

# Model:
# Trained on raw data (wrong!)
# Accuracy: 67% (should be 92%)
# Deployed to production
# Client: "Why is it so bad?"
# You: "... I forgot preprocessing."
```

---

### Problem 2: Run Everything (Slow)
```bash
# You changed one line in evaluate.py
# But you run entire workflow:
python generate_data.py    # 2 minutes (unnecessary)
python preprocess.py       # 5 minutes (unnecessary)
python train.py            # 30 minutes (unnecessary)
python evaluate.py         # 1 minute (needed!)

# Total: 38 minutes
# Should be: 1 minute
```

---

### Problem 3: "What Changed?"
```bash
# Teammate: "Model accuracy dropped from 92% to 85%"
# You: "What changed?"
# Teammate: "I don't know... I ran all the scripts"

# Investigation:
# - Did data change? Maybe?
# - Did preprocessing change? Not sure...
# - Did training hyperparameters change? Could be...
# - Did evaluation metrics change? Possibly...

# No way to know what caused the drop
```

---

### Problem 4: Reproducibility
```bash
# Client: "Reproduce the model from March 15"
# You: "Uh... let me see..."
# 
# Questions:
# - Which data version?
# - Which preprocessing?
# - Which hyperparameters?
# - Which scripts?
# - In what order?
# 
# You: "I... don't remember."
# Client: "We need that model for compliance."
# You: "I'm screwed."
```

---

## What DVC Pipelines Do

### Automatic Dependency Tracking
```yaml
# dvc.yaml (DVC pipeline)
stages:
  preprocess:
    cmd: python scripts/preprocess.py
    deps:
      - data/raw/customers.csv
    outs:
      - data/processed/customers_clean.csv
  
  train:
    cmd: python scripts/train.py
    deps:
      - data/processed/customers_clean.csv
      - scripts/train.py
    outs:
      - models/model.pkl
```

DVC knows:
- ✅ train depends on preprocess output
- ✅ If customers.csv changes → rerun everything
- ✅ If train.py changes → rerun train only
- ✅ If nothing changed → use cache (instant)

---

### Smart Caching
```bash
# First run:
dvc repro
# Runs: preprocess (5 min) + train (30 min) = 35 min

# Second run (nothing changed):
dvc repro
# Output: "Everything is up to date"
# Time: 0 seconds

# Change evaluate.py:
dvc repro
# Runs: evaluate only (1 min)
# Skips: preprocess + train (cached)
```

---

### One Command to Rule Them All
```bash
# Manual:
python generate_data.py
python preprocess.py
python train.py
python evaluate.py

# With DVC pipeline:
dvc repro

# DVC:
# 1. Checks dependencies
# 2. Skips unchanged stages (cache)
# 3. Runs only what's needed
# 4. Runs in correct order
# 5. Tracks all inputs/outputs
```

---

### Reproducibility Built-In
```bash
# Reproduce model from March 15:

# 1. Checkout code + data from that date
git checkout <commit-march-15>
dvc checkout

# 2. Run pipeline
dvc repro

# Done! Exact same model reproduced.
# All dependencies, all versions, all hyperparameters.
```

---

## DVC Pipeline Benefits

| Benefit | Description |
|---------|-------------|
| **Automation** | One command runs entire workflow |
| **Dependency tracking** | DVC knows what depends on what |
| **Smart caching** | Only reruns changed stages |
| **Reproducibility** | Pipeline = recipe for your model |
| **Versioning** | dvc.yaml in Git tracks pipeline evolution |
| **Parallelization** | Independent stages run in parallel |
| **Collaboration** | Team shares same pipeline definition |
| **Documentation** | Pipeline is self-documenting |

---

## When to Use DVC Pipelines

### Use DVC Pipelines When:
- ✅ Multi-step ML workflow
- ✅ Long-running stages (>5 minutes)
- ✅ Need reproducibility
- ✅ Team collaboration
- ✅ Frequent experimentation

### Don't Use When:
- ❌ Single script (no dependencies)
- ❌ Ad-hoc exploration (notebooks)
- ❌ One-off analysis
- ❌ Interactive workflows

**Rule of thumb:** >3 steps = use pipeline
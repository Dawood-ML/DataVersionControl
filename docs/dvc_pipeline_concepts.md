# DVC Pipeline Concepts

## Dependency Graph
```
data/raw/customers.csv
         ↓
    [preprocess]
         ↓
data/processed/customers_clean.csv
         ↓
      [train]
         ↓
   models/model.pkl
   models/scaler.pkl
         ↓
     [evaluate]
         ↓
    metrics.json
```

**DVC knows:**
- evaluate depends on train output
- train depends on preprocess output
- preprocess depends on raw data

**Result:**
- Change raw data → rerun everything
- Change train.py → rerun train + evaluate only
- Change evaluate.py → rerun evaluate only

---

## Cache Behavior

### First Run
```bash
dvc repro

# All stages run:
# 1. preprocess: 5 minutes
# 2. train: 30 minutes
# 3. evaluate: 1 minute
# Total: 36 minutes

# DVC caches:
# - customers_clean.csv
# - model.pkl
# - scaler.pkl
```

---

### Second Run (Nothing Changed)
```bash
dvc repro

# Output: "Stage 'preprocess' didn't change, skipping"
#         "Stage 'train' didn't change, skipping"
#         "Stage 'evaluate' didn't change, skipping"

# Time: 0 seconds (instant!)
```

---

### Modify evaluate.py
```bash
# Change evaluation metrics

dvc repro

# Output: "Stage 'preprocess' didn't change, skipping"
#         "Stage 'train' didn't change, skipping"
#         "Running stage 'evaluate'"

# Time: 1 minute (only evaluate runs)
```

---

### Modify train.py
```bash
# Change hyperparameters

dvc repro

# Output: "Stage 'preprocess' didn't change, skipping"
#         "Running stage 'train'"
#         "Running stage 'evaluate'"

# Time: 31 minutes (train + evaluate)
# preprocess skipped (cached)
```

---

### Modify raw data
```bash
# Update customers.csv

dvc repro

# Output: "Running stage 'preprocess'"
#         "Running stage 'train'"
#         "Running stage 'evaluate'"

# Time: 36 minutes (everything reruns)
```

---

## How DVC Detects Changes

### Dependency Hashing
```yaml
stages:
  train:
    deps:
      - data/processed/customers_clean.csv  # ← DVC hashes this
      - scripts/train.py                     # ← And this
```

**Process:**
1. DVC computes MD5 of each dependency
2. Compares to hash from last run
3. If any hash changed → rerun stage
4. If all hashes same → skip stage (use cache)

**Example:**
```
Last run:
- customers_clean.csv: hash abc123
- train.py: hash def456

Current:
- customers_clean.csv: hash abc123  ✅ Same
- train.py: hash xyz789              ❌ Changed!

Result: Rerun train stage
```

---

## Metrics Tracking

### Regular Output vs Metrics
```yaml
outs:
  - models/model.pkl  # Regular output, moved to cache

metrics:
  - metrics.json:
      cache: false    # Stays in working directory
```

**Why cache: false?**
- Metrics are small (KB)
- Need to be readable without `dvc checkout`
- Used for comparison across experiments

**DVC Metrics Commands:**
```bash
# Show current metrics
dvc metrics show

# Compare with previous run
dvc metrics diff
```

---

## Pipeline Visualization
```bash
# Show pipeline as DAG
dvc dag

# Output (ASCII art):
#           +-------+
#           | data/ |
#           | raw/  |
#           +-------+
#                *
#                *
#                *
#         +-----------+
#         | preprocess|
#         +-----------+
#                *
#                *
#                *
#            +-------+
#            | train |
#            +-------+
#                *
#                *
#                *
#          +----------+
#          | evaluate |
#          +----------+
```
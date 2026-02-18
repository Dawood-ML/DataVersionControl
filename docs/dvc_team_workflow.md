# DVC Team Collaboration Workflow

## Setup (Once per Teammate)

### Teammate Joins Project
```bash
# 1. Clone Git repository
git clone https://github.com/you/ml-project.git
cd ml-project

# 2. Setup Python environment
uv sync

# 3. Pull data from DVC remote
uv run dvc pull

# Done! Teammate has:
# ✅ Code (from Git)
# ✅ Data (from DVC remote)
# ✅ Environment (from uv.lock)
```

---

## Daily Workflow

### You Update Dataset
```bash
# 1. Modify data
python scripts/update_data.py

# 2. Update DVC tracking
uv run dvc add data/raw/customers.csv

# 3. Push data to remote
uv run dvc push

# 4. Commit pointer to Git
git add data/raw/customers.csv.dvc
git commit -m "Update dataset: removed outliers"
git push
```

---

### Teammate Gets Your Update
```bash
# 1. Pull latest code
git pull

# Git output shows:
# modified:   data/raw/customers.csv.dvc  ← Pointer changed

# 2. Pull updated data
uv run dvc pull

# DVC downloads new version of customers.csv

# Done! Teammate has your exact data
```

---

## Pipeline Updates

### You Modify Pipeline
```bash
# 1. Change training script
vim scripts/train.py

# 2. Run pipeline
uv run dvc repro

# 3. Push new artifacts
uv run dvc push

# 4. Commit everything
git add dvc.lock scripts/train.py
git commit -m "Increase Random Forest depth to 15"
git push
```

---

### Teammate Syncs
```bash
# 1. Pull code changes
git pull

# 2. Pull updated artifacts
uv run dvc pull

# 3. Verify pipeline up to date
uv run dvc status

# Output: "Data and pipelines are up to date."

# Teammate can now run:
uv run dvc repro  # Instant (everything cached)
```

---

## Conflict Resolution

### Scenario: Both Modify Same Data

**You:**
```bash
# Modify customers.csv
python update_data.py
dvc add data/raw/customers.csv
git add data/raw/customers.csv.dvc
git commit -m "Add 1000 new customers"
git push
```

**Teammate (at same time):**
```bash
# Also modifies customers.csv (different way)
python clean_outliers.py
dvc add data/raw/customers.csv
git add data/raw/customers.csv.dvc
git commit -m "Remove age outliers"
git push  # ← CONFLICT!
```

**Resolution:**
```bash
# Git conflict on customers.csv.dvc
# Teammate must:
# 1. Pull your changes
git pull  # Conflict in customers.csv.dvc

# 2. Decide which version to keep
# Option A: Keep your version
git checkout --theirs data/raw/customers.csv.dvc
dvc checkout data/raw/customers.csv.dvc

# Option B: Keep their version
git checkout --ours data/raw/customers.csv.dvc
# (Already have this data locally)

# Option C: Merge both (manually)
# Combine both changes, create new version
# dvc add data/raw/customers.csv

# 3. Commit resolution
git add data/raw/customers.csv.dvc
git commit -m "Resolve data conflict"
git push
```

**Best Practice:** Coordinate data updates in team chat to avoid conflicts.

---

## Branch Workflow

### Feature Branch with Data Changes
```bash
# 1. Create feature branch
git checkout -b experiment/new-features

# 2. Modify data + code
python add_features.py
dvc add data/processed/features.csv

# 3. Run pipeline
dvc repro

# 4. Push data to remote
dvc push

# 5. Commit
git add .
git commit -m "Add derived features"
git push -u origin experiment/new-features

# 6. Create PR on GitHub
# 7. After merge, main branch has new data version
```

---

## Data Versioning Best Practices

### DO:
- ✅ `dvc push` after every `dvc add`
- ✅ Commit `.dvc` files to Git immediately
- ✅ Use descriptive commit messages
- ✅ Run `dvc pull` after `git pull`
- ✅ Keep `dvc repro` in your workflow

### DON'T:
- ❌ Forget to `dvc push` (teammates can't get data)
- ❌ Commit large files to Git (use DVC)
- ❌ Manually edit `.dvc` files
- ❌ Skip `dvc pull` after Git updates
- ❌ Delete `.dvc/cache` (breaks workflow)

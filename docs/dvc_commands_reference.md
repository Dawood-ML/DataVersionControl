# DVC Commands Reference

## Essential Commands

### Check DVC Status
```bash
# WHAT: See which files are out of sync
# WHY: Know what needs updating
# WHEN: After modifying tracked files
# WHEN NOT: No changes made
# ALTERNATIVE: None

uv run dvc status

# Output examples:
# (No output)  ← Everything in sync ✅
# 
# data/raw/customers.csv.dvc:
#     changed deps:
#         modified: data/raw/customers.csv  ← File changed, needs re-tracking
```

---

### Add/Update Tracking
```bash
# WHAT: Track new file or update existing tracking
# WHY: Version data with DVC
# WHEN: New file or after modifications
# WHEN NOT: File already tracked and unchanged
# ALTERNATIVE: None

uv run dvc add data/raw/customers.csv

# What it does:
# 1. Computes MD5 hash of file
# 2. Moves file to .dvc/cache/
# 3. Updates/creates .dvc pointer file
# 4. Updates .gitignore
```

---

### Checkout Data
```bash
# WHAT: Update working directory to match .dvc file
# WHY: Get data version that matches current Git commit
# WHEN: After git checkout, or when out of sync
# WHEN NOT: Already in sync
# ALTERNATIVE: None

uv run dvc checkout

# What it does:
# 1. Reads all .dvc files
# 2. Looks up hashes in cache
# 3. Updates working directory files to match
# 
# Specific file:
uv run dvc checkout data/raw/customers.csv.dvc

# All files:
uv run dvc checkout
```

---

### Pull Data from Remote
```bash
# WHAT: Download data from remote storage
# WHY: Get data after git clone or checkout
# WHEN: Missing data locally
# WHEN NOT: All data already cached
# ALTERNATIVE: None

uv run dvc pull

# What it does:
# 1. Reads .dvc files
# 2. Checks if files in local cache
# 3. Downloads missing files from remote (S3/GCS/Azure)
# 4. Updates working directory

# Specific file:
uv run dvc pull data/raw/customers.csv.dvc
```

---

### Push Data to Remote
```bash
# WHAT: Upload data to remote storage
# WHY: Backup data, share with team
# WHEN: After dvc add (new/updated data)
# WHEN NOT: Data already on remote
# ALTERNATIVE: None

uv run dvc push

# What it does:
# 1. Reads .dvc files
# 2. Checks what's in local cache but not remote
# 3. Uploads missing files to remote
# 
# Note: Requires remote storage configured (Sub-chunk 4.5)
```

---

## Common Workflows

### Workflow 1: Update Dataset
```bash
# 1. Modify data file
python scripts/update_data.py

# 2. Update DVC tracking
uv run dvc add data/raw/customers.csv

# 3. Commit pointer to Git
git add data/raw/customers.csv.dvc
git commit -m "Update dataset: describe changes"

# 4. Push to remote (when configured)
uv run dvc push
git push
```

---

### Workflow 2: Rollback to Previous Version
```bash
# 1. Checkout old .dvc file from Git
git checkout HEAD~2 data/raw/customers.csv.dvc

# 2. Get corresponding data
uv run dvc checkout data/raw/customers.csv.dvc

# Now data/raw/customers.csv is the old version

# To return to latest:
git checkout main data/raw/customers.csv.dvc
uv run dvc checkout data/raw/customers.csv.dvc
```

---

### Workflow 3: Clone Repo and Get Data
```bash
# Teammate clones repo
git clone <repo-url>
cd repo

# Has code + .dvc files, but NO data yet

# Get all data
uv run dvc pull

# Now has all data files
```

---

### Workflow 4: Switch Git Branches (with different data)
```bash
# Branch A has customers.csv v1
# Branch B has customers.csv v2

git checkout branch-a
# .dvc files switched to branch-a versions

uv run dvc checkout
# Data files now match branch-a

git checkout branch-b
uv run dvc checkout
# Data files now match branch-b
```

---

## DVC Status Output Explained

### "Everything is up to date"
```bash
uv run dvc status
# (No output)
```
Meaning: All data files match their .dvc pointers ✅

---

### "changed deps: modified"
```bash
data/raw/customers.csv.dvc:
    changed deps:
        modified: data/raw/customers.csv
```
Meaning:
- customers.csv changed since last `dvc add`
- Hash doesn't match .dvc file
- Need to run `dvc add` to update tracking

---

### "always changed"
```bash
data/model.pkl.dvc:
    always changed: data/model.pkl
```
Meaning:
- File not in cache
- DVC can't verify it
- Usually after git clone before dvc pull
- Run `dvc pull` to download

---

## Troubleshooting

### Problem: File missing after git checkout
```bash
# Error:
# FileNotFoundError: data/raw/customers.csv

# Solution:
uv run dvc checkout data/raw/customers.csv.dvc

# Why:
# Git checkout updated .dvc file
# But didn't update actual data file
# DVC checkout syncs data to match pointer
```

---

### Problem: "file hash changed" after dvc checkout
```bash
# This is normal after modifying file
# Run dvc add to update tracking
uv run dvc add data/raw/customers.csv
git add data/raw/customers.csv.dvc
git commit -m "Update data"
```

---

### Problem: Can't checkout, file modified
```bash
# Error:
# error: Your local changes would be overwritten by checkout

# Solution 1: Commit changes first
dvc add data/raw/customers.csv
git add data/raw/customers.csv.dvc
git commit -m "Save current version"

# Solution 2: Discard changes
git checkout -- data/raw/customers.csv.dvc
dvc checkout data/raw/customers.csv.dvc --force
```
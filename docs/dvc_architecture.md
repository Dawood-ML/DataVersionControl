# DVC Architecture: How It Works

## The Two-Layer System

DVC works alongside Git, not replacing it.

### Layer 1: Git (Tracks Pointers)
```
Git Repository (.git/)
├── data/raw/customers.csv.dvc  ← 100 bytes, tracked
├── src/train.py                 ← Code, tracked
├── .dvc/config                  ← DVC config, tracked
└── .gitignore                   ← Ignores actual data
```

**What Git tracks:**
- ✅ Code files
- ✅ DVC pointer files (`.dvc`)
- ✅ DVC configuration
- ❌ Actual data (ignored)

---

### Layer 2: DVC (Tracks Data)
```
DVC Cache (.dvc/cache/)
└── files/md5/
    └── a1/
        └── b2c3d4e5f6g7h8...  ← 1.2MB, actual data

Remote Storage (S3/GCS/Azure - configured later)
└── a1/
    └── b2c3d4e5f6g7h8...  ← 1.2MB, backup
```

**What DVC tracks:**
- ✅ Data files (by content hash)
- ✅ Model files
- ✅ Large binary artifacts
- ❌ Code (Git handles that)

---

## How They Work Together

### Scenario: Adding Data
```bash
# Step 1: Create data file
echo "data" > data/file.csv

# Step 2: Track with DVC
dvc add data/file.csv

# What happens:
# 1. DVC computes MD5 hash of file.csv
# 2. DVC moves file.csv → .dvc/cache/files/md5/ab/cd...
# 3. DVC creates file.csv.dvc (pointer with hash)
# 4. DVC updates .gitignore to ignore file.csv

# Step 3: Commit pointer to Git
git add data/file.csv.dvc data/.gitignore
git commit -m "Track data with DVC"

# Result:
# Git: Tracks 100-byte pointer file
# DVC: Stores 1.2MB actual data
```

---

### Scenario: Teammate Clones Repo
```bash
# Teammate runs:
git clone <repo-url>
cd repo

# What they get:
# ✅ All code
# ✅ DVC pointer files (.dvc)
# ❌ Actual data (not downloaded yet)

# Data structure:
data/raw/customers.csv.dvc  ← Pointer file present
data/raw/customers.csv      ← File missing! (not downloaded)

# Teammate downloads data:
dvc pull data/raw/customers.csv.dvc

# What happens:
# 1. DVC reads hash from .dvc file
# 2. DVC downloads from remote storage
# 3. DVC saves to .dvc/cache/
# 4. DVC creates link: data/raw/customers.csv → cache

# Now they have:
data/raw/customers.csv      ← Present! (linked from cache)
```

---

## File Flow Diagram
```
┌─────────────────────────────────────────────────────────┐
│ 1. CREATE DATA FILE                                     │
│    data/raw/customers.csv (1.2MB)                       │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 2. DVC ADD (uv run dvc add data/raw/customers.csv)     │
│                                                         │
│    a) Compute MD5 hash                                  │
│    b) Move to cache: .dvc/cache/files/md5/a1/b2c3...   │
│    c) Create pointer: data/raw/customers.csv.dvc        │
│    d) Add to .gitignore                                 │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 3. GIT COMMIT                                           │
│                                                         │
│    Git tracks:                                          │
│    - data/raw/customers.csv.dvc (100 bytes)             │
│    - data/raw/.gitignore                                │
│                                                         │
│    Git ignores:                                         │
│    - data/raw/customers.csv (1.2MB)                     │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 4. DVC PUSH (later, with remote storage)               │
│                                                         │
│    Upload to S3/GCS/Azure:                              │
│    .dvc/cache/files/md5/a1/b2c3... → s3://bucket/...   │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 5. TEAMMATE CLONES REPO                                 │
│                                                         │
│    Git clone downloads:                                 │
│    - Code                                               │
│    - .dvc pointer files                                 │
│                                                         │
│    Data NOT downloaded (yet)                            │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 6. TEAMMATE RUNS DVC PULL                               │
│                                                         │
│    DVC downloads from S3:                               │
│    s3://bucket/a1/b2c3... → .dvc/cache/files/md5/...    │
│                                                         │
│    DVC creates link:                                    │
│    data/raw/customers.csv → .dvc/cache/...              │
│                                                         │
│    Teammate now has exact same data!                    │
└─────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Content-Addressable Storage

**WHAT:** Files stored by hash of contents, not filename  
**WHY:** Same content = same hash = deduplicated storage  
**WHEN:** DVC stores files  
**EXAMPLE:**
```
data/v1/customers.csv (hash: a1b2c3...)
data/v2/customers.csv (hash: a1b2c3...)  ← Same hash!

DVC storage:
.dvc/cache/a1/b2c3...  ← Only stored ONCE

Saved: 1.2MB (no duplication)
```

---

### Symlinks / Hardlinks

**WHAT:** DVC creates links from working dir to cache  
**WHY:** Avoid duplicating data (save disk space)  
**WHEN:** After `dvc pull` or `dvc checkout`  
**EXAMPLE:**
```
data/raw/customers.csv → .dvc/cache/files/md5/a1/b2c3...
                         (link, not copy)

Disk usage:
data/raw/customers.csv: 0 bytes (link)
.dvc/cache/...: 1.2MB (actual file)
Total: 1.2MB (not 2.4MB)
```

---

## DVC vs Git Comparison

| Aspect | Git | DVC |
|--------|-----|-----|
| **Designed for** | Code (text files) | Data (binary files) |
| **File size limit** | ~100MB (practical) | Unlimited |
| **Storage** | .git/ directory | .dvc/cache/ + remote |
| **Tracks** | File content line-by-line | File hash (MD5) |
| **Diffs** | Line-by-line changes | Hash changed or not |
| **Clone speed** | Downloads all history | Downloads pointers only |
| **Cost** | Free (self-hosted) | Free + storage costs |

---

## When to Use What

### Use Git for:
- ✅ Source code (.py, .js, .java)
- ✅ Configuration files (.yaml, .json)
- ✅ Documentation (.md, .txt)
- ✅ DVC pointer files (.dvc)
- ✅ Small data (<1MB)

### Use DVC for:
- ✅ Datasets (CSV, Parquet, HDF5)
- ✅ Model files (.pkl, .h5, .pt)
- ✅ Images, videos, audio
- ✅ Any file >10MB
- ✅ Binary artifacts

### Use Both Together:
```
Git tracks:
├── src/train.py                    ← Code
├── data/raw/customers.csv.dvc      ← Pointer (100 bytes)
└── models/model.pkl.dvc            ← Pointer (100 bytes)

DVC tracks (in cache):
├── .dvc/cache/.../customers.csv    ← Data (1.2MB)
└── .dvc/cache/.../model.pkl        ← Model (50MB)
```

**Result:** Git stays fast, data properly versioned.

# DVC Commands Cheatsheet

## Data Versioning
```bash
# Track file with DVC
dvc add data/file.csv

# Update tracking (after modifying file)
dvc add data/file.csv

# Restore file from cache
dvc checkout data/file.csv.dvc

# Check status
dvc status
```

---

## Remote Storage
```bash
# Add remote
dvc remote add -d storage /path/to/remote
dvc remote add -d storage s3://bucket/path

# List remotes
dvc remote list

# Remove remote
dvc remote remove storage

# Push to remote (backup)
dvc push

# Pull from remote (download)
dvc pull

# Push specific file
dvc push data/file.csv.dvc

# Pull specific file
dvc pull data/file.csv.dvc
```

---

## Pipelines
```bash
# Run pipeline
dvc repro

# Run specific stage
dvc repro train

# Show pipeline DAG
dvc dag

# Show metrics
dvc metrics show

# Compare metrics with previous run
dvc metrics diff

# Show pipeline status
dvc status
```

---

## Cleanup
```bash
# Remove unused cache files
dvc gc

# Remove all cache
rm -rf .dvc/cache

# Remove workspace files (keep cache)
dvc checkout --relink
```

---

## Configuration
```bash
# Set default remote
dvc remote default storage

# Enable autostage
dvc config core.autostage true

# View all config
dvc config --list

# Set cache directory
dvc cache dir /path/to/cache
```

---

## Troubleshooting
```bash
# Verify data integrity
dvc status --cloud

# Force checkout (overwrite local changes)
dvc checkout --force

# Show DVC version
dvc version

# Show verbose output
dvc push -v

# Fetch but don't checkout
dvc fetch
```

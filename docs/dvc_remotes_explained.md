# DVC Remote Storage

## The Problem
```
Current state:
- Data in .dvc/cache/ (local only)
- If laptop dies → data gone
- Teammate can't download your data
- No backup
```

---

## The Solution: Remote Storage
```
DVC Remote:
- Backup of .dvc/cache/ in cloud (S3/GCS/Azure)
- OR on shared network drive
- OR on SSH server
- Team can `dvc pull` to download
- You can `dvc push` to backup
```

---

## Remote Storage Types

### 1. Amazon S3 (Most Common)
```bash
dvc remote add -d storage s3://my-bucket/dvc-storage
dvc remote modify storage region us-east-1
```

**Pros:**
- ✅ Cheap ($0.023/GB/month)
- ✅ Fast
- ✅ Reliable
- ✅ Industry standard

**Cons:**
- ❌ Requires AWS account
- ❌ Setup complexity (IAM, credentials)

**Cost example:**
- 100GB data: $2.30/month
- 1TB data: $23/month

---

### 2. Google Cloud Storage
```bash
dvc remote add -d storage gs://my-bucket/dvc-storage
```

**Pros:**
- ✅ Similar pricing to S3
- ✅ Good if using GCP

**Cons:**
- ❌ Requires GCP account

---

### 3. Azure Blob Storage
```bash
dvc remote add -d storage azure://mycontainer/path
```

**Pros:**
- ✅ Good if using Azure

**Cons:**
- ❌ Requires Azure account

---

### 4. Local/Network Drive (Free!)
```bash
dvc remote add -d storage /path/to/shared/drive
# Or network path:
dvc remote add -d storage //server/share/dvc-storage
```

**Pros:**
- ✅ Free
- ✅ No cloud account needed
- ✅ Fast (local network)

**Cons:**
- ❌ No off-site backup
- ❌ Limited to local network
- ❌ You manage storage

**Best for:**
- Learning
- Small teams on same network
- Testing DVC workflow

---

### 5. SSH/SFTP
```bash
dvc remote add -d storage ssh://user@server/path
```

**Pros:**
- ✅ Works with any SSH server
- ✅ Good for self-hosted

**Cons:**
- ❌ Slower than S3
- ❌ You manage server

---

## Workflow with Remote
```
Local Development:
1. dvc add data/file.csv         → Add to local cache
2. git commit                     → Commit .dvc file
3. dvc push                       → Upload to remote storage
4. git push                       → Upload code to GitHub

Teammate Clones:
1. git clone <repo>               → Get code + .dvc files
2. dvc pull                       → Download data from remote
3. Work on project                → Has exact same data
```

---

## Cost Comparison

For 100GB ML project:

| Storage | Setup | Monthly Cost | Bandwidth Cost |
|---------|-------|--------------|----------------|
| **Local** | Easy | $0 | $0 |
| **S3** | Medium | $2.30 | $0.09/GB out |
| **GCS** | Medium | $2.00 | $0.12/GB out |
| **Azure** | Medium | $2.00 | $0.087/GB out |

**Bandwidth matters for teams:**
- 10 teammates × 100GB pull = 1TB bandwidth
- S3: $90 one-time
- After first pull, incremental only

---

## Recommendation

### For Learning (You):
- **Use local remote** (free, simple)
- `/tmp/dvc-remote` or `~/dvc-remote`

### For Solo Production:
- **Use S3** (cheap, reliable, industry standard)
- $2-5/month for most projects

### For Teams:
- **Use S3/GCS** (team can share data)
- Consider Git LFS if budget tight

### For Self-Hosted:
- **Use SSH remote** (your own server)

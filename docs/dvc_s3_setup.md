# DVC with Amazon S3 (Production)

## When You're Ready for Production

**For now (learning):** Use local remote  
**Later (production/team):** Use S3

---

## S3 Setup Steps

### 1. Create S3 Bucket
```bash
# AWS CLI (if installed):
aws s3 mb s3://my-ml-project-dvc

# Or use AWS Console:
# https://console.aws.amazon.com/s3/
```

---

### 2. Configure DVC Remote
```bash
# Add S3 remote
uv run dvc remote add -d storage s3://my-ml-project-dvc/dvc-storage

# Set region (important for speed)
uv run dvc remote modify storage region us-east-1

# Optional: Set profile (if using AWS CLI profiles)
uv run dvc remote modify storage profile myprofile
```

---

### 3. Setup AWS Credentials

**Option A: AWS CLI (Recommended)**
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region (us-east-1)
# - Output format (json)
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Option C: IAM Role (EC2/Lambda)**
- Assign IAM role to compute instance
- DVC uses instance role automatically

---

### 4. Test Connection
```bash
# Push data to S3
uv run dvc push

# If successful:
# ✅ Data uploaded to s3://my-ml-project-dvc/dvc-storage/
```

---

### 5. Cost Optimization

**Use S3 Lifecycle Policies:**
```json
{
  "Rules": [{
    "Id": "Move old data to Glacier",
    "Status": "Enabled",
    "Transitions": [{
      "Days": 90,
      "StorageClass": "GLACIER"
    }]
  }]
}
```

**Result:** Data unused for 90 days moves to Glacier ($0.004/GB vs $0.023/GB)

---

## S3 Permissions (IAM Policy)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-ml-project-dvc/*",
        "arn:aws:s3:::my-ml-project-dvc"
      ]
    }
  ]
}
```

---

## Switching from Local to S3
```bash
# Remove local remote
uv run dvc remote remove local

# Add S3 remote
uv run dvc remote add -d storage s3://my-bucket/dvc

# Push existing data to S3
uv run dvc push

# Update .dvc/config in Git
git add .dvc/config
git commit -m "Switch to S3 remote storage"
git push

# Team updates:
git pull  # Get new remote config
dvc pull  # Download from S3
```

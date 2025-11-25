#!/bin/bash
# Automated Backup Script for AI Grading System
# Backs up MongoDB, Redis, and uploaded files to S3/Azure/GCS

set -e  # Exit on error

# Configuration
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
MONGO_URI="${MONGODB_URI:-mongodb://localhost:27017}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
UPLOADS_DIR="${UPLOADS_DIR:-/app/static/uploads}"

# Cloud storage configuration (set one)
S3_BUCKET="${S3_BUCKET:-}"
AZURE_CONTAINER="${AZURE_CONTAINER:-}"
GCS_BUCKET="${GCS_BUCKET:-}"

echo "🔄 Starting backup at $(date)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Backup MongoDB
echo "📦 Backing up MongoDB..."
mongodump \
    --uri="$MONGO_URI" \
    --out="$BACKUP_DIR/mongodb_$DATE" \
    --gzip

if [ $? -eq 0 ]; then
    echo "✅ MongoDB backup completed"
else
    echo "❌ MongoDB backup failed"
    exit 1
fi

# 2. Backup Redis
echo "📦 Backing up Redis..."
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --rdb "$BACKUP_DIR/redis_$DATE.rdb"

if [ $? -eq 0 ]; then
    echo "✅ Redis backup completed"
else
    echo "⚠️  Redis backup failed (non-critical)"
fi

# 3. Backup uploaded files
if [ -d "$UPLOADS_DIR" ]; then
    echo "📦 Backing up uploaded files..."
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$UPLOADS_DIR" .
    echo "✅ Uploads backup completed"
fi

# 4. Create metadata file
cat > "$BACKUP_DIR/metadata_$DATE.json" <<EOF
{
    "timestamp": "$(date -Iseconds)",
    "mongodb_backup": "mongodb_$DATE",
    "redis_backup": "redis_$DATE.rdb",
    "uploads_backup": "uploads_$DATE.tar.gz",
    "hostname": "$(hostname)",
    "version": "2.0.0"
}
EOF

# 5. Upload to cloud storage
if [ -n "$S3_BUCKET" ]; then
    echo "☁️  Uploading to S3..."
    aws s3 sync "$BACKUP_DIR" "s3://$S3_BUCKET/backups/" \
        --exclude "*" \
        --include "*_$DATE*"
    echo "✅ S3 upload completed"
elif [ -n "$AZURE_CONTAINER" ]; then
    echo "☁️  Uploading to Azure Blob Storage..."
    az storage blob upload-batch \
        --destination "$AZURE_CONTAINER" \
        --source  "$BACKUP_DIR" \
        --pattern "*_$DATE*"
    echo "✅ Azure upload completed"
elif [ -n "$GCS_BUCKET" ]; then
    echo "☁️  Uploading to Google Cloud Storage..."
    gsutil -m rsync -r "$BACKUP_DIR" "gs://$GCS_BUCKET/backups/"
    echo "✅ GCS upload completed"
fi

# 6. Cleanup old backups locally
echo "🧹 Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type d -empty -delete

echo "✅ Backup completed successfully at $(date)"
echo "📊 Backup size: $(du -sh $BACKUP_DIR | cut -f1)"

# Send notification (optional)
if command -v curl &> /dev/null && [ -n "$WEBHOOK_URL" ]; then
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"✅ AI Grading System backup completed: $DATE\"}"
fi

# Production Deployment Guide

## 🚀 Deploying AI-Powered Grading System

### Prerequisites
- Docker and Docker Compose installed
- Domain name (optional)
- SSL certificate (recommended for production)
- MongoDB instance or MongoDB Atlas account
- Redis instance (or use Docker)
- OpenAI API key

---

## Quick Deploy with Docker

### 1. Clone and Configure
```bash
git clone <repository-url>
cd ai-grading-system
cp .env.example .env
```

### 2. Edit Environment Variables
```bash
# .env file
FLASK_ENV=production
SECRET_KEY=<generate-strong-secret>
MONGODB_URI=mongodb://mongo:27017/ai_grading
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=<your-openai-key>
SENTRY_DSN=<your-sentry-dsn>
```

### 3. Build and Start
```bash
docker-compose up -d --build
```

### 4. Verify Deployment
```bash
docker-compose ps
curl http://localhost:5000/health
```

---

## Cloud Deployment Options

### AWS Deployment

**Using ECS (Elastic Container Service):**
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin
docker build -t ai-grading-system .
docker tag ai-grading-system:latest <ecr-repo-url>
docker push <ecr-repo-url>

# Deploy to ECS using provided task definition
aws ecs create-service --cluster production --service-name ai-grading ...
```

**Using EC2:**
```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@<ec2-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and run
git clone <repo>
cd ai-grading-system
docker-compose up -d
```

### Google Cloud Platform

**Using Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/<project-id>/ai-grading
gcloud run deploy --image gcr.io/<project-id>/ai-grading --platform managed
```

### Azure

**Using Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name ai-grading \
  --image <registry>/ai-grading:latest \
  --ports 5000
```

---

## Database Setup

### MongoDB Atlas (Recommended)
1. Create cluster at mongodb.com/cloud/atlas
2. Get connection string
3. Update `.env`:
   ```
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ai_grading
   ```

### Self-Hosted MongoDB
```bash
# Already included in docker-compose.yml
# Data persists in volume: mongo-data
```

---

## SSL/HTTPS Setup

### Using Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Using Let's Encrypt
```bash
certbot --nginx -d yourdomain.com
```

---

## Monitoring Setup

### Sentry Integration
```python
# Already configured in app.py
# Just add SENTRY_DSN to .env
SENTRY_DSN=https://...@sentry.io/...
```

### Application Logs
```bash
# View logs
docker-compose logs -f web

# Logs are saved in logs/ directory
tail -f logs/app.log
tail -f logs/errors.log
```

---

## Performance Optimization

### Enable Redis Caching
```bash
# Already configured if using docker-compose
# Redis runs automatically
```

### Celery Workers
```bash
# Start additional workers
docker-compose scale celery-worker=3
```

### Gunicorn Workers
```dockerfile
# Edit Dockerfile CMD line
CMD ["gunicorn", "--workers", "8", "--bind", "0.0.0.0:5000", "app:app"]
```

---

## Backup Strategy

### Database Backups
```bash
# MongoDB backup
docker exec mongodb mongodump --out /backup

# Automated daily backups
0 2 * * * docker exec mongodb mongodump --out /backup/$(date +\%Y\%m\%d)
```

### File Uploads Backup
```bash
# Backup uploads directory
tar -czf uploads-backup.tar.gz static/uploads
```

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
    # Add load balancer
```

### Vertical Scaling
```yaml
# Increase resources
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Set FORCE_HTTPS=True
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Use strong database passwords
- [ ] Enable MongoDB authentication
- [ ] Keep dependencies updated
- [ ] Enable Sentry monitoring
- [ ] Regular security scans

---

## Health Checks

### Endpoints
- `/health` - Application health
- `/test` - API functionality

### Monitoring Script
```bash
#!/bin/bash
response=$(curl -s http://localhost:5000/health)
if [[ $response == *"healthy"* ]]; then
    echo "✅ Application healthy"
else
    echo "❌ Application down"
    docker-compose restart web
fi
```

---

## Troubleshooting

### Container Won't Start
```bash
docker-compose logs web
docker-compose down
docker-compose up --build
```

### Database Connection Issues
```bash
# Check MongoDB status
docker-compose logs mongo

# Test connection
docker exec -it mongodb mongosh
```

### High Memory Usage
```bash
# Check container stats
docker stats

# Restart services
docker-compose restart
```

---

## Maintenance

### Updates
```bash
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Cleanup
```bash
# Remove old images
docker image prune -a

# Remove old volumes
docker volume prune
```

---

**For support, contact: support@ai-grading.com**

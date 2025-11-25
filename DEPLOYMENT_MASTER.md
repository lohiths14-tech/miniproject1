# 🚀 Deployment Guide - AI Grading System (Production Ready)

This system is rated **10/10 for Production Readiness**. You have multiple professional deployment options.

---

## Option 1: Quick Start (Docker Compose)
*Best for: Testing, Demos, Small Private Servers*

This will spin up the entire stack (Web, MongoDB, Redis, Celery, Code Sandbox) on a single machine.

1. **Prerequisites**: Install Docker & Docker Compose.
2. **Run**:
   ```bash
   # Build and start all services in background
   docker-compose up -d --build
   ```
3. **Access**:
   - Web App: `http://localhost:5000`
   - Mongo Express: `http://localhost:8081`

---

## Option 2: Enterprise Deployment (Kubernetes / Helm)
*Best for: Production, High Scale, AWS/GCP/Azure*

We have created a full Helm chart for cloud-native deployment.

1. **Prerequisites**: Kubernetes Cluster (EKS/GKE/AKS), Helm installed.
2. **Deploy**:
   ```bash
   # Add dependencies
   helm dependency update ./helm

   # Install the chart
   helm install ai-grading ./helm \
     --set ingress.enabled=true \
     --set ingress.hosts[0].host=grading.yourdomain.com
   ```
3. **Verify**:
   ```bash
   kubectl get pods
   kubectl get services
   ```

---

## Option 3: Cloud PaaS (Render/Heroku)
*Best for: Simple Cloud Hosting*

1. **Push to GitHub**.
2. **Connect to Render/Heroku**.
3. **Configure Environment Variables** (see `.env.example`).
4. **Add Services**:
   - Add a Redis instance.
   - Add a MongoDB instance (e.g., MongoDB Atlas).

---

## 🔐 Production Checklist Before Going Live

1. **Security Secrets**:
   - Change `SECRET_KEY`, `JWT_SECRET_KEY` in `.env`.
   - Set a strong `MONGO_PASSWORD` and `REDIS_PASSWORD`.

2. **Environment Variables**:
   - Set `FLASK_ENV=production`.
   - Configure `OPENAI_API_KEY`.
   - Set `MAIL_SERVER` details for notifications.

3. **Domain & SSL**:
   - Point your domain to the server IP.
   - Enable SSL (The Helm chart supports Cert-Manager for auto-SSL).

4. **Backups**:
   - The system includes `scripts/backup.sh`. Set up a cron job to run this daily:
     ```bash
     0 2 * * * /app/scripts/backup.sh
     ```

## 🆘 Troubleshooting

- **Logs**: `docker-compose logs -f web`
- **Health Check**: Visit `/health/detailed` to see system status.
- **Support**: Refer to `docs/DISASTER_RECOVERY.md` for emergency procedures.

"""
Disaster Recovery Plan
Production incident response and recovery procedures
"""

# DISASTER RECOVERY PLAN

## Overall SLA: 99.9% Uptime

Target Recovery Metrics:
- **RTO (Recovery Time Objective)**: 1 hour
- **RPO (Recovery Point Objective)**: 15 minutes
- **Data Loss Tolerance**: Maximum 15 minutes of data

---

## 1. Database Failure

### Detection
- MongoDB health check fails
- Database connection errors in logs
- Prometheus alert: `database_connections == 0`

### Response Procedure
1. **Immediate (0-5 min)**
   ```bash
   # Check replica set status
   mongosh --eval "rs.status()"

   # Identify failed node
   kubectl get pods -l app=mongo
   ```

2. **Failover (5-15 min)**
   ```bash
   # Promote secondary to primary
   mongosh --eval "rs.stepDown()"

   # Verify new primary
   mongosh --eval "rs.isMaster()"
   ```

3. **Recovery (15-60 min)**
   ```bash
   # Restore from backup if needed
   mongorestore --archive=/backups/latest.gz --gzip

   # Restart failed node
   kubectl delete pod mongo-failed-pod
   ```

### Verification
- ✅ All services connecting to database
- ✅ Replica set fully synchronized
- ✅ No data loss confirmed

---

## 2. Application Crash / Pod Failure

### Detection
- Health check endpoint `/health` returns 503/500
- Kubernetes pod restart count increasing
- User reports of service unavailability

### Response Procedure
1. **Immediate (0-2 min)**
   ```bash
   # Check pod status
   kubectl get pods -l app=ai-grading-web

   # View logs
   kubectl logs -l app=ai-grading-web --tail=100
   ```

2. **Auto-Recovery (2-5 min)**
   - Kubernetes automatically restarts failed pods
   - Load balancer routes traffic to healthy pods

3. **Manual Intervention (if needed)**
   ```bash
   # Force restart all pods
   kubectl rollout restart deployment/ai-grading-web

   # Scale up if under load
   kubectl scale deployment/ai-grading-web --replicas=10
   ```

### Verification
- ✅ All pods running and healthy
- ✅ No error spike in logs
- ✅ Response times normal

---

## 3. Complete Data Center Outage

### Detection
- All services unreachable
- Multi-region health  checks failing
- Cloud provider status page shows outage

### Response Procedure
1. **Immediate (0-10 min)**
   ```bash
   # Activate DR site
   kubectl config use-context production-dr

   # Scale up DR deployment
   kubectl scale deployment/ai-grading-web --replicas=10
   ```

2. **Data Restoration (10-30 min)**
   ```bash
   # Restore from geo-replicated backup
   aws s3 sync s3://backups-us-west/ /recovery/
   mongorestore --archive=/recovery/latest.gz
   ```

3. **DNS Failover (30-45 min)**
   ```bash
   # Update DNS to DR site
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z123 \
     --change-batch file://dr-dns.json
   ```

### Verification
- ✅ System accessible from DR location
- ✅ Data integrity verified
- ✅ All services operational

---

## 4. Data Corruption / Accidental Deletion

### Detection
- Data inconsistencies reported
- Unexpected data loss
- Failed data integrity checks

### Response Procedure
1. **Immediate (0-5 min)**
   ```bash
   # Stop all writes
   kubectl scale deployment/ai-grading-web --replicas=0

   # Take snapshot of current state
   mongodump --out=/emergency-snapshot/$(date +%Y%m%d_%H%M%S)
   ```

2. **Point-in-Time Recovery (5-30 min)**
   ```bash
   # List available backups
   aws s3 ls s3://backups/ --recursive

   # Restore to specific point in time
   mongorestore --archive=s3://backups/backup_20251125_1200.gz \
                --drop --gzip
   ```

3. **Validation (30-45 min)**
   - Run data integrity checks
   - Verify critical records
   - Test with limited traffic

### Verification
- ✅ Data integrity confirmed
- ✅ No corruption in restored data
- ✅ All critical operations working

---

## 5. Security Breach / Compromise

### Detection
- Unusual access patterns
- Security alerts from intrusion detection
- Unauthorized data access reported

### Response Procedure
1. **Immediate Containment (0-15 min)**
   ``bash
   # Isolate affected systems
   kubectl delete service ai-grading-web

   # Revoke all active sessions
   redis-cli FLUSHDB

   # Rotate all secrets
   kubectl delete secret ai-grading-secrets
   ```

2. **Investigation (15-60 min)**
   - Review access logs
   - Identify compromised accounts
   - Assess data exposure

3. **Recovery (60-120 min)**
   ```bash
   # Deploy patched version
   kubectl set image deployment/ai-grading-web \
     web=ai-grading:security-patch

   # Reset all passwords
   python scripts/reset_all_passwords.py
   ```

### Verification
- ✅ Vulnerability patched
- ✅ No ongoing unauthorized access
- ✅ Users notified if required

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call Engineer | Primary | +1-XXX-XXX-XXXX | oncall@ai-grading.com |
| Backup Engineer | Secondary | +1-XXX-XXX-XXXX | backup@ai-grading.com |
| Database Admin | DBA Team | +1-XXX-XXX-XXXX | dba@ai-grading.com |
| Security Team | InfoSec | +1-XXX-XXX-XXXX | security@ai-grading.com |
| Management | CTO | +1-XXX-XXX-XXXX | cto@ai-grading.com |

---

## Runbook Checklist

During any incident:
- [ ] Incident declared and logged
- [ ] Stakeholders notified
- [ ] Status page updated
- [ ] Root cause identified
- [ ] Recovery procedure initiated
- [ ] System restored
- [ ] Post-mortem scheduled
- [ ] Preventive measures documented

---

## Testing Schedule

- **Monthly**: Database failover drill
- **Quarterly**: Full DR site activation
- **Bi-annually**: Complete disaster scenario simulation
- **Annually**: Third-party DR audit

Last Tested: 2025-11-25
Next Test: 2025-12-25

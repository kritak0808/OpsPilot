# OpsPilot AI — Operations Runbook

> This runbook is the authoritative reference for on-call SRE engineers operating OpsPilot AI in production. It covers incident response, health monitoring, deployment procedures, rollbacks, and common failure scenarios.

---

## Table of Contents

1. [On-Call Responsibilities](#on-call-responsibilities)
2. [Service Health Dashboard](#service-health-dashboard)
3. [Alert Severity Definitions](#alert-severity-definitions)
4. [Incident Response Playbook](#incident-response-playbook)
5. [Common Failure Scenarios](#common-failure-scenarios)
6. [Deployment & Rollback Procedures](#deployment--rollback-procedures)
7. [Database Operations](#database-operations)
8. [Kubernetes Operations](#kubernetes-operations)
9. [Log Investigation Guide](#log-investigation-guide)
10. [Escalation Matrix](#escalation-matrix)

---

## On-Call Responsibilities

The on-call SRE is responsible for:
- Monitoring PagerDuty / Slack `#ops-alerts` channel during their rotation
- Acknowledging P0/P1 alerts within **5 minutes**
- Achieving mitigation for P0 incidents within **30 minutes**
- Writing incident postmortems within **48 hours** of resolution
- Handing off open incidents during rotation change with context notes

---

## Service Health Dashboard

| Service | Health URL | Expected Response |
|---|---|---|
| Backend API | `GET /health` | `{"status": "healthy"}` |
| AI Orchestrator | `GET /health` | `{"status": "healthy"}` |
| Frontend | `GET /` | HTTP 200 |
| PostgreSQL | `pg_isready -h postgres -p 5432` | `accepting connections` |
| Redis | `redis-cli ping` | `PONG` |

### Quick health check script

```bash
#!/bin/bash
echo "=== OpsPilot Health Check ==="
echo "Backend:"; curl -s http://localhost:8000/health | jq .status
echo "AI Orchestrator:"; curl -s http://localhost:8002/health | jq .status
echo "PostgreSQL:"; pg_isready -h localhost -p 5432
echo "Redis:"; redis-cli ping
echo "==========================="
```

---

## Alert Severity Definitions

| Priority | SLA | Definition |
|---|---|---|
| **P0 — Critical** | Mitigate in 30 min | Full service outage. All users affected. Revenue impact. |
| **P1 — High** | Mitigate in 2 hours | Major feature broken. Significant user impact. |
| **P2 — Medium** | Resolve in 8 hours | Partial degradation. Workaround available. |
| **P3 — Low** | Resolve in 48 hours | Minor UX issue. No data impact. |

---

## Incident Response Playbook

### Phase 1: Alert → Acknowledge (< 5 minutes)

1. Acknowledge alert in PagerDuty
2. Post in `#incidents`: `🚨 Investigating: [alert name]`
3. Open incident record via `/api/v1/observability/incidents` or `/observability`

### Phase 2: Investigate (< 15 minutes)

```bash
# Check pod status
kubectl get pods -n opspilot

# Check recent events
kubectl get events -n opspilot --sort-by='.lastTimestamp'

# Check pod logs (backend)
kubectl logs -l app=opspilot-backend -n opspilot --tail=200

# Check pod logs (frontend)
kubectl logs -l app=opspilot-frontend -n opspilot --tail=100

# Check resource usage
kubectl top pods -n opspilot
kubectl top nodes
```

**Use AI RCA for incident diagnosis:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/diagnose \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"incident_id": "<uuid>"}'
```

### Phase 3: Mitigate

Select the appropriate mitigation strategy from [Common Failure Scenarios](#common-failure-scenarios).

### Phase 4: Communicate

Post updates every 15 minutes to `#incidents`:
```
Update [HH:MM]: Billing service degraded. Root cause identified: PostgreSQL connection pool exhausted.
Mitigation in progress: Restarting backend pods + increasing max_connections.
```

### Phase 5: Resolve & Postmortem

1. Resolve the incident in OpsPilot
2. Close PagerDuty alert
3. Generate AI postmortem:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/ai/postmortem?incident_id=<uuid>" \
     -H "Authorization: Bearer <token>"
   ```
4. Review and publish postmortem within 48 hours

---

## Common Failure Scenarios

### Scenario 1: Backend API returning 502 Bad Gateway

**Symptoms:** Frontend shows errors, all `/api/*` requests fail.

**Investigate:**
```bash
kubectl get pods -n opspilot -l app=opspilot-backend
kubectl describe pod <pod-name> -n opspilot
kubectl logs <pod-name> -n opspilot --tail=50
```

**Mitigation:**
```bash
# Restart backend deployment
kubectl rollout restart deployment/opspilot-backend -n opspilot

# Watch rollout progress
kubectl rollout status deployment/opspilot-backend -n opspilot
```

---

### Scenario 2: Database Connection Exhaustion

**Symptoms:** Backend logs show `asyncpg.exceptions.TooManyConnectionsError`.

**Investigate:**
```sql
-- Check active connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Check max connections setting
SHOW max_connections;

-- Identify long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 minute'
ORDER BY duration DESC;
```

**Mitigation:**
```sql
-- Terminate idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND now() - state_change > interval '5 minutes';
```

Long-term: Deploy PgBouncer as a connection pooler.

---

### Scenario 3: Redis Unavailable / Pipeline Queue Stalled

**Symptoms:** Pipeline runs stuck in `PENDING`. Celery workers show connection errors.

**Investigate:**
```bash
redis-cli ping                     # Should return PONG
redis-cli info replication         # Check master/replica status
redis-cli llen celery              # Check queue depth
```

**Mitigation:**
```bash
# Restart Redis pod
kubectl rollout restart statefulset/redis -n opspilot

# Or restart Celery worker
kubectl rollout restart deployment/celery-worker -n opspilot
```

---

### Scenario 4: AI Orchestrator Not Responding

**Symptoms:** AI chat returns 503. Backend logs show `ConnectionRefusedError` to port 8002.

**Investigate:**
```bash
kubectl get pods -n opspilot -l app=ai-orchestrator
kubectl logs -l app=ai-orchestrator -n opspilot --tail=50
```

**Mitigation:**
```bash
kubectl rollout restart deployment/ai-orchestrator -n opspilot
```

The AI features will gracefully degrade — the rest of the platform continues to function.

---

### Scenario 5: Persistent Volume Full

**Symptoms:** PostgreSQL or Loki log writes failing. Storage alerts firing.

**Investigate:**
```bash
kubectl exec -it postgres-0 -n opspilot -- df -h /var/lib/postgresql/data
```

**Mitigation:**
```bash
# Expand PVC (if cloud storage supports expansion)
kubectl patch pvc postgres-data -n opspilot \
  -p '{"spec": {"resources": {"requests": {"storage": "100Gi"}}}}'

# Emergency: Delete old WAL files (use with caution)
kubectl exec -it postgres-0 -n opspilot -- \
  find /var/lib/postgresql/data/pg_wal -mtime +7 -delete
```

---

## Deployment & Rollback Procedures

### Standard Deployment

```bash
# Tag a new release
git tag v1.1.0 && git push --tags

# GitHub Actions will build and push Docker images automatically

# Deploy via Helm
helm upgrade opspilot ./infrastructure/helm \
  --namespace opspilot \
  --set image.tag=1.1.0 \
  --atomic \
  --timeout 5m
```

### Emergency Rollback (Helm)

```bash
# View history
helm history opspilot -n opspilot

# Rollback to previous revision
helm rollback opspilot -n opspilot

# Rollback to specific revision
helm rollback opspilot 3 -n opspilot
```

### Database Migration Rollback

```bash
cd apps/backend

# Check current version
poetry run alembic current

# Roll back one migration
poetry run alembic downgrade -1

# Roll back to specific revision
poetry run alembic downgrade <revision_id>
```

---

## Database Operations

### Manual Backup

```bash
# Full backup
kubectl exec -n opspilot postgres-0 -- \
  pg_dump -U opspilot opspilot | gzip > opspilot_$(date +%Y%m%d_%H%M%S).sql.gz

# Upload to S3
aws s3 cp opspilot_*.sql.gz s3://opspilot-backups/manual/
```

### Restore from Backup

```bash
# Download backup
aws s3 cp s3://opspilot-backups/manual/opspilot_20260710.sql.gz .

# Scale down backend to stop writes
kubectl scale deployment opspilot-backend --replicas=0 -n opspilot

# Restore
gunzip -c opspilot_20260710.sql.gz | \
  kubectl exec -i -n opspilot postgres-0 -- \
    psql -U opspilot -d opspilot

# Restart backend
kubectl scale deployment opspilot-backend --replicas=2 -n opspilot
```

---

## Kubernetes Operations

### Useful Day-to-Day Commands

```bash
# List all resources in namespace
kubectl get all -n opspilot

# Describe a failing pod
kubectl describe pod <name> -n opspilot

# Force delete a stuck pod
kubectl delete pod <name> -n opspilot --grace-period=0 --force

# Scale a deployment
kubectl scale deployment opspilot-backend --replicas=3 -n opspilot

# Run an interactive debug pod
kubectl run debug --image=busybox:1.35 -it --rm -n opspilot -- sh

# Port-forward for local debugging
kubectl port-forward svc/opspilot-backend 8000:8000 -n opspilot

# Edit a ConfigMap live
kubectl edit configmap opspilot-config -n opspilot
```

---

## Log Investigation Guide

OpsPilot emits structured JSON logs via `structlog`. All log entries include:
- `timestamp`
- `level`
- `service`
- `event`
- `trace_id`
- `user_id` (when applicable)

### Tail production logs

```bash
# Backend logs
kubectl logs -l app=opspilot-backend -n opspilot --tail=100 -f

# Filter for errors only
kubectl logs -l app=opspilot-backend -n opspilot | jq 'select(.level == "error")'

# Find logs by trace ID
kubectl logs -l app=opspilot-backend -n opspilot | \
  jq 'select(.trace_id == "abc123xyz")'

# Find all errors in the last hour
kubectl logs -l app=opspilot-backend -n opspilot --since=1h | \
  jq 'select(.level == "error")'
```

---

## Escalation Matrix

| Severity | First Responder | Escalation (30 min) | Exec Escalation (1 hr) |
|---|---|---|---|
| P0 | On-call SRE | SRE Lead + Backend Lead | CTO |
| P1 | On-call SRE | SRE Lead | Engineering Manager |
| P2 | On-call SRE | Domain Lead | — |
| P3 | Domain Owner | — | — |

**Slack channels:**
- `#ops-alerts` — Automated alerts
- `#incidents` — Active incident coordination
- `#on-call` — On-call handoffs

**PagerDuty escalation policy:** `opspilot-production-oncall`

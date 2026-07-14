# OpsPilot AI — Deployment Guide

> This guide covers all deployment paths for OpsPilot AI: local Docker Compose, Terraform-provisioned AWS infrastructure, and production Kubernetes via Helm.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Compose (Local / Staging)](#docker-compose)
3. [Production Dockerfiles](#production-dockerfiles)
4. [Environment Configuration](#environment-configuration)
5. [Terraform: AWS Infrastructure](#terraform-aws-infrastructure)
6. [Helm: Kubernetes Deployment](#helm-kubernetes-deployment)
7. [Production Kubernetes Checklist](#production-kubernetes-checklist)
8. [Scaling Guidelines](#scaling-guidelines)
9. [Health Checks & Readiness Probes](#health-checks--readiness-probes)
10. [Zero-Downtime Deployments](#zero-downtime-deployments)

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker | 24.x+ | Container runtime |
| Docker Compose | 2.x+ | Multi-container orchestration |
| kubectl | 1.28+ | Kubernetes CLI |
| Helm | 3.13+ | Kubernetes package manager |
| Terraform | 1.5+ | Infrastructure provisioning |
| AWS CLI | 2.x | AWS resource management |

---

## Docker Compose

The `docker-compose.yml` at the repository root orchestrates the full local stack.

### Start the full platform

```bash
# Build all images and start all services
docker compose up --build -d

# View logs for all services
docker compose logs -f

# View logs for a specific service
docker compose logs -f backend

# Stop all services
docker compose down

# Stop and remove volumes (wipe database)
docker compose down -v
```

### Service URLs after compose up

| Service | URL | Credentials |
|---|---|---|
| Frontend | http://localhost:3000 | See seed data |
| Backend API | http://localhost:8000/docs | JWT required |
| AI Orchestrator | http://localhost:8002/docs | No auth |
| PostgreSQL | localhost:5432 | `opspilot / opspilot` |
| Redis | localhost:6379 | No auth |

### Running Migrations After Compose Up

```bash
docker compose exec backend poetry run alembic upgrade head
docker compose exec backend poetry run python src/database/seed.py
```

---

## Production Dockerfiles

Multi-stage builds are defined in `infrastructure/docker/`.

### Backend Dockerfile pattern

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry export -f requirements.txt > requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim as production
WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Image Size Optimization

- Use `python:3.11-slim` (not `python:3.11`)
- Use `.dockerignore` to exclude `tests/`, `docs/`, `.git/`
- Multi-stage builds reduce final image size by ~60%

---

## Environment Configuration

### Required Variables per Service

#### Backend (`apps/backend/.env`)

```env
# ─── Database ───────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://opspilot:password@postgres:5432/opspilot

# ─── Redis ──────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ─── Authentication ─────────────────────────────────────
JWT_SECRET_KEY=<256-bit-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ─── Service Discovery ──────────────────────────────────
AI_ORCHESTRATOR_URL=http://ai-orchestrator:8002

# ─── Application ────────────────────────────────────────
PROJECT_NAME=OpsPilot AI
ENVIRONMENT=production
DEBUG=false
```

**Generating a secure JWT secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Production Secret Injection

In production, never store secrets in `.env` files. Inject via:

**Kubernetes Secrets:**
```bash
kubectl create secret generic opspilot-secrets \
  --from-literal=JWT_SECRET_KEY=<value> \
  --from-literal=DATABASE_URL=<value> \
  --namespace opspilot
```

**HashiCorp Vault (recommended):**
```bash
vault kv put secret/opspilot \
  JWT_SECRET_KEY=<value> \
  DATABASE_URL=<value>
```

---

## Terraform: AWS Infrastructure

Terraform modules are located in `infrastructure/terraform/`.

### Initialize and Apply

```bash
cd infrastructure/terraform

# Initialize Terraform providers and backend
terraform init

# Preview planned changes
terraform plan \
  -var="environment=production" \
  -var="aws_region=us-east-1"

# Apply infrastructure changes
terraform apply \
  -var="environment=production" \
  -var="aws_region=us-east-1"
```

### Remote State (S3 Backend)

The Terraform state is stored remotely in S3 to enable team collaboration:

```hcl
backend "s3" {
  bucket         = "opspilot-terraform-state"
  key            = "production/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "opspilot-lock-table"   # State locking
}
```

Create the S3 bucket and DynamoDB table before first init:
```bash
aws s3 mb s3://opspilot-terraform-state --region us-east-1
aws dynamodb create-table \
  --table-name opspilot-lock-table \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Key Variables

| Variable | Default | Description |
|---|---|---|
| `aws_region` | `us-east-1` | AWS deployment region |
| `environment` | `production` | Environment tag |

---

## Helm: Kubernetes Deployment

The OpsPilot Helm chart is located at `infrastructure/helm/`.

### First-time Installation

```bash
# Update chart dependencies (PostgreSQL, Redis bitnami charts)
helm dependency update ./infrastructure/helm

# Install in dedicated namespace
helm install opspilot ./infrastructure/helm \
  --namespace opspilot \
  --create-namespace \
  --values ./infrastructure/helm/values.yaml \
  --set image.tag=1.0.0
```

### Upgrade an Existing Release

```bash
helm upgrade opspilot ./infrastructure/helm \
  --namespace opspilot \
  --values ./infrastructure/helm/values.yaml \
  --set image.tag=1.1.0 \
  --atomic \
  --timeout 5m
```

The `--atomic` flag automatically rolls back if the upgrade fails.

### Environment-Specific Value Overrides

Create `values-production.yaml`:
```yaml
replicaCount: 3

resources:
  limits:
    cpu: 2000m
    memory: 2048Mi
  requests:
    cpu: 500m
    memory: 512Mi

ingress:
  hosts:
    - host: opspilot.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
```

```bash
helm upgrade opspilot ./infrastructure/helm \
  -f values.yaml \
  -f values-production.yaml
```

### Useful Helm Commands

```bash
# List all releases
helm list -n opspilot

# View release history
helm history opspilot -n opspilot

# Rollback to previous revision
helm rollback opspilot 1 -n opspilot

# Uninstall release
helm uninstall opspilot -n opspilot
```

---

## Production Kubernetes Checklist

Before going live, verify:

- [ ] **Namespace isolation** — All resources in `opspilot` namespace
- [ ] **Resource limits** — CPU and memory limits set on all containers
- [ ] **Liveness probes** — `/health` endpoint configured on all pods
- [ ] **Readiness probes** — `/health` endpoint used for traffic routing
- [ ] **Secret management** — Vault Agent Injector configured, no plaintext secrets in manifests
- [ ] **Ingress TLS** — cert-manager issuing Let's Encrypt certificates
- [ ] **HPA configured** — HorizontalPodAutoscaler on backend and frontend
- [ ] **PDB configured** — PodDisruptionBudget ensures availability during node maintenance
- [ ] **Network policies** — Egress/ingress rules limit blast radius
- [ ] **RBAC** — ServiceAccount with least-privilege ClusterRole
- [ ] **Image tags** — Pinned versions, never `latest` in production

---

## Scaling Guidelines

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: opspilot-backend-hpa
  namespace: opspilot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: opspilot-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Database Scaling

- Use **PgBouncer** connection pooler for high-concurrency workloads
- Enable **PostgreSQL read replicas** for analytics queries
- Set `max_connections=200` in PostgreSQL config

---

## Health Checks & Readiness Probes

All services expose `/health` endpoints:

```bash
# Backend health check
curl http://localhost:8000/health
# → {"status": "healthy", "service": "backend", "db": "connected"}

# AI Orchestrator health check
curl http://localhost:8002/health
# → {"status": "healthy", "service": "ai-orchestrator"}
```

---

## Zero-Downtime Deployments

Use Helm's `RollingUpdate` strategy (default):

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0    # Never reduce capacity below desired
    maxSurge: 1          # Allow 1 extra pod during upgrade
```

Combine with `--atomic` flag in Helm to auto-rollback on failure.

<![CDATA[<div align="center">

<img src="https://img.shields.io/badge/OpsPilot%20AI-v1.0.0-6C63FF?style=for-the-badge&logo=rocket&logoColor=white" alt="OpsPilot AI" />

# ✈️ OpsPilot AI

### Enterprise AI-Integrated DevSecOps Operations Platform

*Monitor. Deploy. Diagnose. Orchestrate. Automatically.*

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.115-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015-black.svg?style=flat-square&logo=next.js)](https://nextjs.org)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat-square&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph-brightgreen.svg?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg?style=flat-square&logo=docker)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5.svg?style=flat-square&logo=kubernetes)](https://kubernetes.io)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg?style=flat-square&logo=github-actions)](https://github.com/features/actions)
[![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178C6.svg?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![SQLModel](https://img.shields.io/badge/ORM-SQLModel-00BCD4.svg?style=flat-square)](https://sqlmodel.tiangolo.com)
[![Redis](https://img.shields.io/badge/Cache-Redis-DC382D.svg?style=flat-square&logo=redis)](https://redis.io)

---

[**Documentation**](docs/) • [**Developer Guide**](docs/developer_guide.md) • [**API Reference**](docs/api_documentation.md) • [**Deployment Guide**](docs/deployment_guide.md) • [**Contributing**](docs/contributing_guide.md)

</div>

---

## 🌟 What is OpsPilot AI?

OpsPilot AI is a **production-grade, enterprise DevSecOps operations platform** that combines real-time infrastructure observability, AI-powered incident diagnosis, Kubernetes lifecycle management, and full-spectrum CI/CD pipeline automation into a unified command center.

It is designed for engineering teams that need to:
- **Monitor** clusters, services, and pipelines from a single pane of glass
- **Diagnose** production failures using multi-agent AI root-cause analysis
- **Deploy** applications with Helm-driven Kubernetes release management
- **Govern** secrets, API keys, audit trails, and feature flags at enterprise scale

---

## ✨ Core Features

| Domain | Capabilities |
|---|---|
| 🔐 **Identity & RBAC** | Multi-tenant orgs, JWT auth, role scopes (OrgOwner → Viewer), API keys, MFA-ready |
| 🧬 **Project Management** | Projects, applications, environments, GitHub/GitLab integration, webhook receivers |
| ⚙️ **CI/CD Engine** | Pipeline definitions, stage/job execution, Celery workers, artifact storage, log streaming |
| ⚓ **Kubernetes Platform** | Cluster manager, pods/deployments/services, ReplicaSets, real-time status polling |
| 📊 **Observability** | Metrics dashboards, Loki log explorer, distributed traces, incident management, SLOs |
| 🤖 **AI Operations** | LangGraph supervisor, 10 specialized agents, ChatOps interface, root-cause analysis |
| 🔒 **Governance** | Vault KMS secrets, feature flags, audit log trails, usage analytics, billing foundation |
| 🚀 **Production Ready** | Helm charts, Terraform IaC, GitHub Actions CI/CD, Docker multi-stage builds |

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer"]
        Browser([Web Browser])
    end

    subgraph Frontend["⚛️ Frontend — Next.js 15"]
        WebApp[Next.js App Router]
        AuthCtx[Auth Provider / JWT]
        Components[React Components]
    end

    subgraph Gateway["🔌 API Gateway — FastAPI"]
        Router[FastAPI Router]
        AuthMW[Auth Middleware]
        RBAC[RBAC Guards]
        API[REST Endpoints]
    end

    subgraph Services["⚙️ Backend Services"]
        Pipelines[Pipeline Engine]
        K8sClient[Kubernetes Client]
        ObsSvc[Observability Service]
        GovernanceSvc[Governance Service]
    end

    subgraph DataLayer["🗄️ Data Layer"]
        Postgres[(PostgreSQL)]
        Redis[(Redis Cache)]
        Alembic[Alembic Migrations]
    end

    subgraph AI["🧠 AI Orchestrator — LangGraph"]
        Supervisor[Supervisor Router]
        K8sAgent[Kubernetes Agent]
        DeployAgent[Deployment Agent]
        PipelineAgent[Pipeline Agent]
        MonitorAgent[Monitoring Agent]
        RCAAgent[Root Cause Agent]
        SecurityAgent[Security Agent]
        CostAgent[Cost Agent]
    end

    subgraph Infra["☁️ Infrastructure"]
        Helm[Helm Charts]
        Terraform[Terraform IaC]
        Docker[Docker Images]
        GHA[GitHub Actions]
    end

    Browser --> WebApp
    WebApp --> Router
    Router --> AuthMW --> RBAC --> API
    API --> Services
    Services --> Postgres
    Services --> Redis
    API --> Supervisor
    Supervisor --> K8sAgent & DeployAgent & PipelineAgent & MonitorAgent & RCAAgent & SecurityAgent & CostAgent
```

---

## 🤖 AI Agent Architecture

OpsPilot uses a **LangGraph Supervisor** pattern — a stateful multi-agent graph where a central Supervisor routes incoming requests to the most appropriate specialized DevOps agent.

```mermaid
graph LR
    UserQuery([💬 User Query]) --> Supervisor

    subgraph Graph["LangGraph State Machine"]
        Supervisor{🎯 Supervisor\nRouter}
        Supervisor -->|kube/pod| K8s[⚓ KubernetesAgent]
        Supervisor -->|deploy/helm| Deploy[🚀 DeploymentAgent]
        Supervisor -->|pipeline/build| Pipeline[⚙️ PipelineAgent]
        Supervisor -->|alert/metric| Monitor[📊 MonitoringAgent]
        Supervisor -->|incident/outage| Incident[🚨 IncidentAgent]
        Supervisor -->|cost/billing| Cost[💰 CostAgent]
        Supervisor -->|security/cve| Security[🔒 SecurityAgent]
        Supervisor -->|infra/terraform| Infra[🏗️ InfraAgent]
        Supervisor -->|doc/guide| Docs[📚 DocumentationAgent]
        Supervisor -->|default| RCA[🔍 RootCauseAgent]
    end

    K8s & Deploy & Pipeline & Monitor & Incident & Cost & Security & Infra & Docs & RCA --> END([✅ Response\n+ Reasoning Timeline])
```

**AgentState** carries typed context across the graph:
- `messages` — conversation thread history
- `active_agent` — currently executing agent
- `reasoning_timeline` — chain-of-thought trace log
- `tool_outputs` — agent execution results
- `confidence_score` — result confidence (0.0–1.0)

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js 15 (App Router) | Web console UI |
| **Styling** | Tailwind CSS | Component styling system |
| **Backend** | FastAPI 0.115 | REST API gateway |
| **ORM** | SQLModel + Alembic | Database models & migrations |
| **Database** | PostgreSQL 16 | Relational data storage |
| **Cache / Queue** | Redis + Celery | Task queue and session cache |
| **AI Framework** | LangGraph + LangChain | Multi-agent orchestration |
| **Containers** | Docker (multi-stage) | Image packaging |
| **Orchestration** | Kubernetes + Helm | Production deployment |
| **IaC** | Terraform (AWS) | Cloud infrastructure |
| **CI/CD** | GitHub Actions | Automated pipelines |
| **Observability** | Prometheus + Loki | Metrics & log aggregation |
| **Secrets** | HashiCorp Vault (KMS) | Secret management |

---

## 📂 Folder Structure

```text
OpsPilot/
├── .github/
│   └── workflows/
│       └── production-release.yaml   # CI/CD pipeline
├── apps/
│   ├── backend/                      # FastAPI application
│   │   ├── src/
│   │   │   ├── models/               # SQLModel database models
│   │   │   ├── routers/              # FastAPI route handlers
│   │   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── database/             # Alembic migrations + seed scripts
│   │   │   ├── dependencies/         # Auth, session injection
│   │   │   └── main.py               # FastAPI app factory
│   │   ├── tests/                    # Pytest test suites
│   │   └── pyproject.toml
│   ├── frontend/                     # Next.js 15 web console
│   │   ├── src/
│   │   │   ├── app/                  # App Router pages
│   │   │   ├── components/           # Reusable UI components
│   │   │   └── providers/            # Auth, theme providers
│   │   └── package.json
│   └── ai-orchestrator/              # LangGraph agent service
│       ├── src/
│       │   ├── agents/               # Specialized agent definitions
│       │   ├── langgraph/            # Graph, state, nodes
│       │   ├── tools/                # Agent tool integrations
│       │   └── main.py               # Orchestrator FastAPI entry
│       └── pyproject.toml
├── infrastructure/
│   ├── docker/                       # Production Dockerfiles
│   ├── helm/                         # Kubernetes Helm chart
│   │   ├── Chart.yaml
│   │   └── values.yaml
│   └── terraform/                    # AWS IaC modules
│       └── main.tf
├── docs/                             # Documentation library
│   ├── developer_guide.md
│   ├── architecture_guide.md
│   ├── deployment_guide.md
│   ├── api_documentation.md
│   ├── ai_documentation.md
│   ├── operations_runbook.md
│   ├── security_guide.md
│   └── contributing_guide.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── docker-compose.yml
└── pnpm-workspace.yaml
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| Node.js | 18.x | [nodejs.org](https://nodejs.org) |
| PNPM | 8.x | `npm install -g pnpm` |
| Python | 3.11+ | [python.org](https://python.org) |
| Poetry | 1.7+ | [python-poetry.org](https://python-poetry.org) |
| Docker | 24.x | [docker.com](https://docker.com) |
| Docker Compose | 2.x | bundled with Docker Desktop |

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/opspilot.git
cd opspilot
```

### 2. Install All Dependencies

```bash
# Install JavaScript monorepo dependencies
pnpm install

# Install Python backend dependencies
cd apps/backend && poetry install && cd ../..

# Install AI orchestrator dependencies
cd apps/ai-orchestrator && poetry install && cd ../..
```

### 3. Configure Environment Variables

```bash
cp apps/backend/.env.example apps/backend/.env
```

Edit `apps/backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://opspilot:opspilot@localhost:5432/opspilot

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Orchestrator
AI_ORCHESTRATOR_URL=http://localhost:8002

# Project
PROJECT_NAME=OpsPilot AI
ENVIRONMENT=development
DEBUG=true
```

### 4. Start Infrastructure Services

```bash
docker compose up -d
```

This starts PostgreSQL and Redis containers.

### 5. Run Database Migrations & Seed

```bash
cd apps/backend
poetry run alembic upgrade head
poetry run python src/database/seed.py
```

### 6. Start All Services

Open three terminal windows:

```bash
# Terminal 1 — Backend API
cd apps/backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — AI Orchestrator
cd apps/ai-orchestrator
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8002

# Terminal 3 — Frontend
pnpm --filter frontend dev
```

Access the platform at **http://localhost:3000**

---

## 🐳 Docker Deployment

### Build & Run with Docker Compose

```bash
# Build all service images
docker compose build

# Start the full platform stack
docker compose up -d

# View running containers
docker compose ps

# Follow aggregated logs
docker compose logs -f
```

### Docker Compose Services

| Service | Port | Description |
|---|---|---|
| `frontend` | 3000 | Next.js web console |
| `backend` | 8000 | FastAPI gateway |
| `ai-orchestrator` | 8002 | LangGraph agent service |
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache + task queue |

---

## ☁️ Production Deployment

### Kubernetes with Helm

```bash
# Add dependencies
helm dependency update ./infrastructure/helm

# Install release
helm install opspilot ./infrastructure/helm \
  --namespace opspilot \
  --create-namespace \
  -f ./infrastructure/helm/values.yaml

# Upgrade existing release
helm upgrade opspilot ./infrastructure/helm \
  --namespace opspilot \
  -f ./infrastructure/helm/values.yaml

# Check rollout status
kubectl rollout status deployment/opspilot -n opspilot
```

### Terraform Infrastructure (AWS)

```bash
cd infrastructure/terraform
terraform init
terraform plan -var="environment=production"
terraform apply -var="environment=production"
```

---

## 🔄 CI/CD Pipeline

OpsPilot uses GitHub Actions for automated validation on every push to `main`:

| Stage | Action |
|---|---|
| **Backend Validation** | Install Poetry → Run `pytest tests/` |
| **Frontend Build** | Install PNPM → Run `next build` |
| **Docker Build** | Build multi-stage production images |
| **Release** | Tag version and publish artifacts |

See [`.github/workflows/production-release.yaml`](.github/workflows/production-release.yaml).

---

## 📊 Observability

OpsPilot includes a built-in observability suite:

| Feature | Path | Description |
|---|---|---|
| **Metrics Dashboard** | `/observability` | Prometheus-style resource counters |
| **Log Explorer** | `/observability/logs` | Loki-style structured log viewer |
| **Distributed Traces** | `/observability/traces` | OpenTelemetry spans viewer |
| **Incident Manager** | `/observability/incidents` | Alert routing + incident lifecycle |
| **Health Endpoints** | `/health` | Liveness + readiness probes |

---

## 🔐 Security

| Feature | Implementation |
|---|---|
| **Authentication** | JWT HS256, 60-minute token expiry |
| **Authorization** | 5-tier RBAC (OrgOwner → Viewer) |
| **API Keys** | SHA-256 hashed, prefix-tagged tokens (`op_`) |
| **Secrets** | HashiCorp Vault KMS envelope encryption |
| **Audit Logs** | All actions logged with actor, IP, timestamp |
| **Feature Flags** | Gradual rollouts, kill-switches, org-scoped toggles |

See [Security Guide](docs/security_guide.md) for the complete policy.

---

## 🗺️ Roadmap

| Version | Feature |
|---|---|
| **v1.1** | Playwright E2E test suite + Schemathesis contract testing |
| **v1.2** | Qdrant vector memory for AI agent long-term context |
| **v1.3** | MCP (Model Context Protocol) tool server integration |
| **v1.4** | GitOps reconciliation loop (ArgoCD-style) |
| **v1.5** | Multi-cloud support (GCP GKE + Azure AKS) |
| **v2.0** | AI-driven self-healing cluster remediation |

---

## 🤝 Contributing

We welcome contributions! Please read the [Contributing Guide](docs/contributing_guide.md) for:
- Branch naming conventions
- Commit message standards
- Pull request process
- Code review guidelines
- Testing requirements

---

## 📜 License

OpsPilot AI is released under the [MIT License](LICENSE).

---

<div align="center">

Built with ❤️ by the OpsPilot Engineering Team

**[Documentation](docs/)** • **[Issues](https://github.com/your-org/opspilot/issues)** • **[Discussions](https://github.com/your-org/opspilot/discussions)**

</div>
]]>

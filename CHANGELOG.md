# Changelog

All notable changes to OpsPilot AI are documented here.

This project adheres to [Semantic Versioning](https://semver.org) and [Conventional Commits](https://www.conventionalcommits.org).

---

## [1.0.0] — 2026-07-10

### 🚀 Initial Public Release

**OpsPilot AI v1.0.0** is the first production-ready release of the enterprise AI-integrated DevSecOps platform.

---

### ✨ Features

#### Identity & Access Management
- Multi-tenant organization model with invitation-based membership
- 5-tier RBAC: `OrgOwner`, `Admin`, `DevOpsEngineer`, `Developer`, `Viewer`
- JWT-based authentication (HS256, 60-minute expiry)
- API key management with SHA-256 hashing and prefix tagging (`op_*`)
- Team management with scoped membership roles

#### Project Management
- Projects with slug-based routing
- Multi-environment support (Development, Staging, Production)
- Application and service tracking
- GitHub/GitLab repository integration with webhook receivers
- Git provider credential management

#### CI/CD Engine
- Pipeline definitions with stage/job/step hierarchy
- Pipeline run execution via Celery task queue (Redis)
- Real-time execution status (`PENDING` → `RUNNING` → `SUCCESS` / `FAILED`)
- Pipeline variables and secrets injection
- Artifact storage and retrieval
- Execution log streaming

#### Kubernetes Platform
- Cluster import and lifecycle management
- Node, namespace, deployment, pod tracking
- ReplicaSet, Service, Ingress, ConfigMap management
- Job, CronJob, DaemonSet, StatefulSet support
- PersistentVolume and PersistentVolumeClaim tracking

#### Observability Platform
- Metrics dashboard with counter tracking
- Log explorer (Loki-style structured log viewer)
- Distributed trace viewer (OpenTelemetry)
- Incident lifecycle management (create, triage, resolve)
- Alert routing with severity classification
- SLO and SLI configuration
- Health check monitoring
- Service topology view
- APM error tracking

#### AI Operations Platform
- LangGraph Supervisor multi-agent orchestration
- 10 specialized DevOps agents:
  - KubernetesAgent, DeploymentAgent, PipelineAgent
  - MonitoringAgent, IncidentAgent, CostAgent
  - SecurityAgent, InfraAgent, DocumentationAgent, RootCauseAgent
- Natural language ChatOps interface
- AI Advisor with structured recommendations
- Incident diagnosis with confidence scoring
- AI-generated postmortem reports
- Reasoning timeline / thought chain visualization

#### Enterprise Governance
- Notification center (placeholder channels: Slack, Email, PagerDuty)
- HashiCorp Vault KMS secret management
- Immutable audit log trail
- System and organization settings management
- Feature flags with toggle and rollout control
- Usage analytics dashboard
- Billing foundation (tier tracking)
- License management

#### Production Infrastructure
- Multi-stage Docker builds for all services
- Kubernetes Helm chart (`infrastructure/helm/`)
- Terraform AWS modules (VPC, S3 state) (`infrastructure/terraform/`)
- GitHub Actions CI/CD pipeline (`.github/workflows/production-release.yaml`)
- PostgreSQL migrations via Alembic
- Comprehensive Pytest test suites

#### Documentation
- README.md with hero section, badges, architecture diagrams
- Developer Guide (extending the platform, coding standards)
- Architecture Guide (8 Mermaid diagrams)
- Deployment Guide (Docker, Terraform, Helm)
- API Documentation (full REST reference)
- AI Platform Documentation (LangGraph design)
- Operations Runbook (incident response playbook)
- Security Guide (RBAC, JWT, Vault, hardening checklist)
- Contributing Guide (Conventional Commits, PR process)

---

### 🗄️ Database Schema

Initial schema covers 25+ tables across 7 domains:
- `users`, `organizations`, `teams`, `team_memberships`, `sessions`
- `projects`, `applications`, `environments`, `repositories`, `git_credentials`
- `pipelines`, `pipeline_runs`, `pipeline_steps`, `pipeline_artifacts`, `pipeline_logs`
- `clusters`, `nodes`, `namespaces`, `kubernetes_deployments`, `pods`
- `incidents`, `alerts`, `metrics`, `traces`, `slos`
- `ai_conversations`, `ai_messages`
- `audit_logs`, `api_keys`, `feature_flags`, `usage_statistics`, `secrets`

---

### 🛡️ Security

- bcrypt password hashing (cost factor 12)
- JWT tokens signed with HS256
- API keys stored as SHA-256 hashes only
- CORS restricted to explicit origin lists
- Container security: non-root user, read-only filesystem

---

### ⚠️ Known Limitations (v1.0.0)

- Kubernetes agent uses simulated responses — real `kubectl` integration planned for v1.1
- AI agents use keyword routing (not LLM routing) — LLM-based supervisor planned for v1.5
- Notification channels are defined but delivery integration requires external webhook config
- Streaming responses (SSE) not yet implemented for AI chat — planned for v1.1

---

## Upcoming

### [1.1.0] — Planned

- Playwright E2E test suite
- Schemathesis API contract testing
- Real Kubernetes API integration via `kubernetes-asyncio`
- SSE streaming for AI chat responses

### [1.2.0] — Planned

- Qdrant vector memory for AI agent context
- Long-term conversation memory

### [1.3.0] — Planned

- MCP (Model Context Protocol) tool server integration

### [1.4.0] — Planned

- GitOps reconciliation loop (ArgoCD-style)

### [2.0.0] — Planned

- AI-driven self-healing Kubernetes remediation
- Multi-cloud support (GCP GKE, Azure AKS)

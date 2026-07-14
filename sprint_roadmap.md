# OpsPilot AI: Phase 6 Enterprise Sprint Implementation Roadmap

This document outlines the development lifecycle for **OpsPilot AI**, detailing the files, modules, database tables, and validation tests for each implementation sprint.

---

## Sprint 0: Project Bootstrap
* **Focus**: Set up the monorepo workspace, package managers, and development runtime containers.
* **Monorepo Folders**:
  - [`/apps/frontend/`](file:///c:/Users/krita/Desktop/OpsPilot/monorepo_blueprint.md#L45) -> Initialize Next.js 15 template.
  - [`/apps/backend/`](file:///c:/Users/krita/Desktop/OpsPilot/monorepo_blueprint.md#L83) -> Initialize FastAPI template.
  - [`/apps/ai-orchestrator/`](file:///c:/Users/krita/Desktop/OpsPilot/monorepo_blueprint.md#L104) -> Initialize LangGraph/FastAPI service template.
* **Configuration Files**:
  - `pnpm-workspace.yaml` (PNPM configuration)
  - `pyproject.toml` (Poetry package mappings)
  - `/infrastructure/compose/docker-compose.yml` (Local runtime)
* **Testing Scope**: Run baseline health check checks (`/health` routes).

---

## Sprint 1: Identity & Multi-Tenancy Foundation
* **Focus**: Establish user registration, organizations, Multi-Factor Authentication (MFA), and RBAC controls.
* **Database Tables**: `Users`, `Organizations`, `TeamMembers`, `APIKeys`.
* **API Endpoints**:
  - `POST /api/v1/auth/login` (Auth validation)
  - `POST /api/v1/auth/mfa/verify` (MFA validation)
  - `GET /api/v1/organizations` (Multi-tenant context lookup)
* **UX Deliverables**: Auth screens, MFA validation views, Organization switcher component.
* **Testing Scope**: Unit tests for JWT signature validation and integration tests for RBAC role checking.

---

## Sprint 2: Core Platform Workspace
* **Focus**: Set up project structures, applications configurations, and git credentials integrations.
* **Database Tables**: `Projects`, `Applications`, `Environments`, `Repositories`.
* **API Endpoints**:
  - `POST /api/v1/projects` (Create project grouping)
  - `POST /api/v1/applications` (Create app configurations)
  - `POST /api/v1/repositories/connect` (Save encrypted VCS secrets)
  - `POST /api/v1/webhooks/github` (Webhook receiver)
* **UX Deliverables**: Projects listing panel, Application configurations view, Repository setup tab.
* **Testing Scope**: Integration checks for webhooks validation and KMS database encryption tests.

---

## Sprint 3: Automation & Task Queue Engine
* **Focus**: Set up runner engines, build tools, and asynchronous Celery workers.
* **Database Tables**: `Pipelines`, `PipelineRuns`.
* **API Endpoints**:
  - `POST /api/v1/pipelines` (Define steps)
  - `POST /api/v1/pipelines/{id}/run` (Trigger execution)
  - `GET /api/v1/pipelines/runs/{run_id}/logs` (Fetch build logs)
* **Background Tasks**:
  - `execute_pipeline(pipeline_run_id)` -> Docker build and ECR push tasks.
* **UX Deliverables**: Pipeline execution viewer, logs aggregator console widget.
* **Testing Scope**: Celery worker integration tests and pipeline execution mocks.

---

## Sprint 4: Orchestrated Release Engine
* **Focus**: Integrate target clusters, deployment configurations, and Helm rollout workflows.
* **Database Tables**: `Clusters`, `Pods`, `Services`, `Deployments`.
* **API Endpoints**:
  - `POST /api/v1/clusters/import` (Import cluster configs)
  - `POST /api/v1/environments/{env_id}/deploy` (Trigger Helm rollout)
  - `GET /api/v1/clusters/{cluster_id}/pods` (Fetch active pod lists)
* **UX Deliverables**: Kubernetes cluster dashboard, namespace filter menus, deployment rollback buttons.
* **Testing Scope**: K8s Client mock validation, Helm dry-run contract verification.

---

## Sprint 5: Platform Observability & Telemetry
* **Focus**: Set up Prometheus collectors, Vector daemonsets, Loki aggregators, and PagerDuty endpoints.
* **Database Tables**: `Metrics`, `Logs`, `Incidents`, `Alerts`.
* **API Endpoints**:
  - `GET /api/v1/metrics/query` (Fetch metrics graphs)
  - `GET /api/v1/logs/query` (Query Loki logs)
  - `POST /api/v1/alerts/receiver` (Ingest Prometheus alarms)
* **UX Deliverables**: Executive dashboard metrics, log query terminal, P0 red-badge alerts panel.
* **Testing Scope**: Loki query engine validation, alarm trigger integration tests.

---

## Sprint 6: Intelligence & ChatOps
* **Focus**: Multi-agent orchestration, incident triage graphs, and automated root cause analysis.
* **Database Tables**: `AIConversations`.
* **API Endpoints**:
  - `POST /api/v1/incidents/{id}/diagnose` (Trigger AI triage run)
  - `GET /api/v1/ai/conversations/{id}` (Chat context list)
* **AI Agent Models**:
  - Root Cause Agent, Kubernetes Agent, Incident Response Agent, and Supervisor Graph.
* **UX Deliverables**: Side-by-side diagnostic log chat drawer, inline error explanation overlays.
* **Testing Scope**: Agent Ragas accuracy metrics evaluation and prompt injection guardrail tests.

---

## Sprint 7: Platform Administration & Secrets
* **Focus**: Multi-channel notifications, KMS key storage, settings profiles, and audit log generation.
* **Database Tables**: `Notifications`, `Secrets`, `AuditLogs`.
* **API Endpoints**:
  - `POST /api/v1/settings` (Update system parameters)
  - `GET /api/v1/audit-logs` (Fetch audit log search queries)
* **Background Tasks**:
  - `dispatch_notification(event_type)` -> Sends Slack and PagerDuty messages.
* **UX Deliverables**: Audit log search grids, notification preference toggle panels.
* **Testing Scope**: Audit logging validation tests and notification template formatting tests.

---

## Sprint 8: Production Readiness & Release
* **Focus**: Load testing, continuous integration rules, and staging-to-production deployment release promotions.
* **Configuration Files**:
  - `.github/workflows/production-release.yaml` (Release CI/CD)
* **Testing Scope**: Run end-to-end load tests using k6, verify Trivy image vulnerability metrics, run Playwright E2E suites.
* **Release Checklist**: Validate definition of done compliance files, compile final README documentation guides.

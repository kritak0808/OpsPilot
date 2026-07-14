# OpsPilot AI — API Reference Documentation

> Complete REST API reference for OpsPilot AI v1.0.0. All endpoints require a valid JWT Bearer token unless marked public.

---

## Table of Contents

1. [Base URL & Versioning](#base-url--versioning)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Identity: Auth & Users](#identity-auth--users)
6. [Organizations & Teams](#organizations--teams)
7. [Projects & Environments](#projects--environments)
8. [Repositories](#repositories)
9. [Pipelines](#pipelines)
10. [Kubernetes](#kubernetes)
11. [Observability](#observability)
12. [AI Operations](#ai-operations)
13. [Governance](#governance)

---

## Base URL & Versioning

```
http://localhost:8000          (local)
https://api.opspilot.io        (production)
```

All endpoints are prefixed with `/api/v1/`.

Interactive API documentation (Swagger UI) is available at:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

---

## Authentication

### Obtaining a Token

```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include in all subsequent requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Context Headers

| Header | Required For | Example |
|---|---|---|
| `Authorization` | All protected endpoints | `Bearer <token>` |
| `X-Project-ID` | Project-scoped endpoints | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |
| `X-Org-ID` | Org-scoped endpoints | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |

### Token Expiry & Refresh

Tokens expire after **60 minutes**. Re-authenticate via `POST /api/v1/auth/token`.

---

## Error Handling

All error responses follow the RFC 7807 Problem Details format:

```json
{
  "detail": "Human-readable error description"
}
```

### HTTP Status Codes

| Code | Meaning | Common Cause |
|---|---|---|
| `200` | OK | Request succeeded |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Malformed request body or headers |
| `401` | Unauthorized | Missing or invalid JWT token |
| `403` | Forbidden | Valid token but insufficient RBAC role |
| `404` | Not Found | Resource UUID does not exist |
| `409` | Conflict | Duplicate unique constraint violation |
| `422` | Unprocessable Entity | Pydantic validation failure |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server-side failure |

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

| Tier | Limit | Window |
|---|---|---|
| Anonymous | 20 req/min | Rolling 60s |
| Authenticated | 300 req/min | Rolling 60s |
| AI endpoints | 60 req/min | Rolling 60s |

Rate limit headers are returned on every response:
```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 297
X-RateLimit-Reset: 1720000060
```

---

## Identity: Auth & Users

### Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Jane Smith"
}
```

**Response `201`:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "Jane Smith",
  "created_at": "2026-07-10T17:00:00Z"
}
```

### Get Current User

```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**Response `200`:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "Jane Smith",
  "created_at": "2026-07-10T17:00:00Z"
}
```

### Update User Profile

```http
PATCH /api/v1/users/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Jane A. Smith"
}
```

---

## Organizations & Teams

### Create Organization

```http
POST /api/v1/organizations
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Acme Corp",
  "slug": "acme-corp"
}
```

### List Organizations

```http
GET /api/v1/organizations
Authorization: Bearer <token>
```

### Invite Member

```http
POST /api/v1/organizations/{org_id}/members
Authorization: Bearer <token>
X-Org-ID: {org_id}
Content-Type: application/json

{
  "email": "colleague@example.com",
  "role_name": "DevOpsEngineer"
}
```

**Available roles:** `OrgOwner` | `Admin` | `DevOpsEngineer` | `Developer` | `Viewer`

### Create Team

```http
POST /api/v1/teams
Authorization: Bearer <token>
X-Org-ID: {org_id}
Content-Type: application/json

{
  "name": "SRE Platform",
  "slug": "sre-platform",
  "description": "Site Reliability Engineers"
}
```

---

## Projects & Environments

### Create Project

```http
POST /api/v1/projects
Authorization: Bearer <token>
X-Org-ID: {org_id}
Content-Type: application/json

{
  "name": "Checkout Service",
  "slug": "checkout-service"
}
```

**Response `201`:**
```json
{
  "id": "...",
  "name": "Checkout Service",
  "slug": "checkout-service",
  "organization_id": "...",
  "created_at": "2026-07-10T17:00:00Z"
}
```

### List Projects

```http
GET /api/v1/projects
Authorization: Bearer <token>
X-Org-ID: {org_id}
```

### Create Environment

```http
POST /api/v1/environments
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "name": "Production",
  "slug": "production"
}
```

---

## Repositories

### Connect Repository

```http
POST /api/v1/repositories
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "name": "checkout-service",
  "url": "https://github.com/acme/checkout-service",
  "provider": "github"
}
```

### List Repositories

```http
GET /api/v1/repositories
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

---

## Pipelines

### Create Pipeline

```http
POST /api/v1/pipelines
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "name": "Main Build Pipeline",
  "repository_id": "{repo_id}"
}
```

### Trigger Pipeline Run

```http
POST /api/v1/pipelines/runs
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "pipeline_id": "{pipeline_id}",
  "branch": "main"
}
```

**Response `201`:**
```json
{
  "id": "...",
  "pipeline_id": "...",
  "status": "PENDING",
  "started_at": "2026-07-10T17:00:00Z"
}
```

### Get Pipeline Run

```http
GET /api/v1/pipelines/runs/{run_id}
Authorization: Bearer <token>
```

**Response includes:** `status` (`PENDING` | `RUNNING` | `SUCCESS` | `FAILED` | `CANCELLED`)

---

## Kubernetes

### Import Cluster

```http
POST /api/v1/kubernetes/clusters/import
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "name": "prod-eks-cluster",
  "endpoint": "https://eks.us-east-1.amazonaws.com",
  "kubeconfig": "<base64-encoded-kubeconfig>"
}
```

### List Clusters

```http
GET /api/v1/kubernetes/clusters
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

### Get Cluster Nodes

```http
GET /api/v1/kubernetes/clusters/{cluster_id}/nodes
Authorization: Bearer <token>
```

### List Deployments

```http
GET /api/v1/kubernetes/deployments
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

---

## Observability

### List Incidents

```http
GET /api/v1/observability/incidents
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

**Response:**
```json
[
  {
    "id": "...",
    "title": "API Gateway 5xx spike",
    "severity": "P1",
    "status": "open",
    "created_at": "2026-07-10T14:30:00Z"
  }
]
```

### Create Incident

```http
POST /api/v1/observability/incidents
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "title": "Database connection exhaustion",
  "severity": "P0",
  "description": "PostgreSQL max_connections reached in billing cluster"
}
```

### List Alerts

```http
GET /api/v1/observability/alerts
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

---

## AI Operations

### Chat with AI Agent

```http
POST /api/v1/ai/chat
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "prompt": "Why is the billing-service pod crashing?",
  "conversation_id": null
}
```

**Response `201`:**
```json
{
  "id": "...",
  "role": "assistant",
  "content": "[Agent: KUBERNETESAGENT] Pod memory limits exceeded. OOM Killer terminated billing-service-v2-abc.",
  "thoughts": "Supervisor routed to KubernetesAgent based on 'pod' keyword match.",
  "created_at": "2026-07-10T17:00:00Z"
}
```

### Diagnose an Incident

```http
POST /api/v1/ai/diagnose
Authorization: Bearer <token>
Content-Type: application/json

{
  "incident_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Response:**
```json
{
  "incident_id": "...",
  "diagnosis": "Kubernetes Pod memory limits exceeded. OOM Killer terminated api-service pod.",
  "confidence": 0.98,
  "reasoning": [
    "Loki logs indicate memory spike above 512Mi at 22:15 UTC",
    "Prometheus gauge reached memory limit bounds at 22:15 UTC"
  ]
}
```

### Get Advisor Recommendations

```http
POST /api/v1/ai/recommend
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "category": "Cost Optimization",
    "impact": "High",
    "confidence": 0.92,
    "description": "Resize unused Kubernetes worker nodes from m5.xlarge to t3.medium.",
    "actions": [
      "Update Terraform workspace parameters",
      "Drain non-essential nodes"
    ]
  }
]
```

### Generate Postmortem

```http
POST /api/v1/ai/postmortem?incident_id={incident_id}
Authorization: Bearer <token>
```

### List AI Conversations

```http
GET /api/v1/ai/conversations
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

### List Active Agents

```http
GET /api/v1/ai/agents
Authorization: Bearer <token>
```

---

## Governance

### Generate API Key

```http
POST /api/v1/api-keys
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "name": "Jenkins CI Integration",
  "scope": "write",
  "expires_days": 30
}
```

**Response `201`:**
```json
{
  "id": "...",
  "name": "Jenkins CI Integration",
  "scope": "write",
  "created_at": "2026-07-10T17:00:00Z",
  "expires_at": "2026-08-09T17:00:00Z",
  "key_preview": "op_abc123xyz..."
}
```

> ⚠️ `key_preview` is shown **only once**. Store it securely immediately.

### List API Keys

```http
GET /api/v1/api-keys
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

### Revoke API Key

```http
DELETE /api/v1/api-keys/{id}
Authorization: Bearer <token>
```

### List Audit Logs

```http
GET /api/v1/audit
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

**Response:**
```json
[
  {
    "id": "...",
    "action": "api_key.create",
    "details": "Generated API Key named: Jenkins CI Integration",
    "ip_address": "192.168.1.1",
    "created_at": "2026-07-10T17:00:00Z"
  }
]
```

### Create Feature Flag

```http
POST /api/v1/feature-flags
Authorization: Bearer <token>
X-Project-ID: {project_id}
Content-Type: application/json

{
  "key": "enable-new-checkout-flow",
  "description": "Enables redesigned checkout funnel",
  "is_enabled": false
}
```

### Get Usage Metrics

```http
GET /api/v1/usage
Authorization: Bearer <token>
X-Project-ID: {project_id}
```

**Response:**
```json
{
  "api_calls_count": 14205,
  "pipeline_runs_count": 86,
  "storage_usage_bytes": 10737418240,
  "active_users_count": 12,
  "license_tier": "Enterprise SaaS"
}
```

### Get System Settings

```http
GET /api/v1/settings
Authorization: Bearer <token>
```

### Update System Settings

```http
POST /api/v1/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "theme": "dark",
  "regional_format": "UTC",
  "mfa_enabled": true
}
```

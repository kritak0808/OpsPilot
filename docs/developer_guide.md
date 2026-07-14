# OpsPilot AI — Developer Guide

> This guide is the authoritative reference for engineers contributing to or extending the OpsPilot AI platform. It covers repository layout, coding standards, how to add new API endpoints, how to register new AI agents, and how to validate changes through the test suite.

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Architecture Principles](#architecture-principles)
3. [Backend: FastAPI Application](#backend-fastapi-application)
4. [Frontend: Next.js Console](#frontend-nextjs-console)
5. [AI Orchestrator: LangGraph](#ai-orchestrator-langgraph)
6. [Adding a New API Endpoint](#adding-a-new-api-endpoint)
7. [Adding a New AI Agent](#adding-a-new-ai-agent)
8. [Database Migrations](#database-migrations)
9. [Running Tests](#running-tests)
10. [Code Quality Tools](#code-quality-tools)
11. [Environment Variables Reference](#environment-variables-reference)

---

## Repository Overview

OpsPilot is a **PNPM monorepo** containing three independently deployable services:

```text
apps/
├── backend/          ← FastAPI REST API gateway (Python 3.11+, Poetry)
├── frontend/         ← Next.js 15 web console (TypeScript, PNPM)
└── ai-orchestrator/  ← LangGraph multi-agent service (Python 3.11+, Poetry)
```

Shared infrastructure resources live in:
```text
infrastructure/
├── docker/           ← Multi-stage Dockerfiles
├── helm/             ← Kubernetes Helm chart
└── terraform/        ← AWS IaC modules

docs/                 ← All documentation guides
```

---

## Architecture Principles

OpsPilot enforces **Clean Architecture** boundaries across all services:

| Layer | Responsibility | Directory |
|---|---|---|
| **Models** | SQLModel database entity definitions | `src/models/` |
| **Schemas** | Pydantic request/response validators | `src/schemas/` |
| **Routers** | FastAPI route handlers / controllers | `src/routers/` |
| **Dependencies** | Auth injection, session providers | `src/dependencies/` |
| **Database** | Connection pool, Alembic migrations | `src/database/` |

**Core rules:**
- Models never import from routers.
- Routers never contain business logic — keep them thin.
- All async database operations use `AsyncSession`.
- All schemas use strict Pydantic v2 validators.
- Every public endpoint must have a corresponding test.

---

## Backend: FastAPI Application

### Directory Layout

```text
apps/backend/src/
├── models/
│   ├── auth.py           # User, Organization, Team, Session, ApiKey
│   ├── project.py        # Project, Application, Environment, Repository
│   ├── pipeline.py       # Pipeline, PipelineRun, PipelineStep, Artifact
│   ├── kubernetes.py     # Cluster, Node, Namespace, Deployment, Pod
│   ├── observability.py  # Incident, Alert, Metric, Log, Trace
│   ├── ai.py             # AIConversation, AIMessage
│   └── governance.py     # AuditLog, FeatureFlag, UsageStatistic
├── routers/
│   ├── auth.py           # POST /api/v1/auth/*, /users/*
│   ├── organizations.py  # GET/POST /api/v1/organizations/*
│   ├── teams.py          # /api/v1/teams/*
│   ├── projects.py       # /api/v1/projects/*
│   ├── repositories.py   # /api/v1/repositories/*
│   ├── environments.py   # /api/v1/environments/*
│   ├── pipelines.py      # /api/v1/pipelines/*
│   ├── kubernetes.py     # /api/v1/kubernetes/*
│   ├── observability.py  # /api/v1/observability/*
│   ├── ai.py             # /api/v1/ai/*
│   └── governance.py     # /api/v1/audit, /api-keys, /feature-flags, /usage
├── schemas/
│   ├── auth.py
│   ├── project.py
│   ├── pipeline.py
│   ├── kubernetes.py
│   ├── observability.py
│   ├── ai.py
│   └── governance.py
├── database/
│   ├── connection.py     # AsyncEngine, get_session()
│   ├── seed.py           # Demo data seeder
│   └── versions/         # Alembic migration scripts
├── dependencies/
│   └── auth.py           # get_current_user() dependency
├── core/
│   ├── config.py         # Settings (pydantic-settings)
│   ├── exceptions.py     # Global exception handlers
│   └── logging.py        # structlog configuration
└── main.py               # App factory: create_app()
```

### Request Lifecycle

```
HTTP Request
    └─→ CORS Middleware
    └─→ Trace-ID Injection Middleware
    └─→ FastAPI Router
        └─→ Auth Dependency (JWT decode → get_current_user)
        └─→ RBAC Guard
        └─→ Route Handler
            └─→ AsyncSession (SQLModel)
            └─→ Response Schema (Pydantic)
```

---

## Frontend: Next.js Console

### Directory Layout

```text
apps/frontend/src/
├── app/
│   ├── page.tsx                    # Dashboard home
│   ├── login/page.tsx              # Authentication
│   ├── register/page.tsx           # Registration
│   ├── projects/page.tsx           # Projects list
│   ├── pipelines/page.tsx          # Pipelines center
│   ├── clusters/page.tsx           # Kubernetes clusters
│   ├── observability/page.tsx      # Observability hub
│   ├── ai/page.tsx                 # ChatOps interface
│   ├── ai/advisor/page.tsx         # AI Advisor recommendations
│   └── settings/page.tsx           # Governance settings (tabbed)
├── components/
│   └── auth/
│       └── protected-route.tsx     # Route guard component
└── providers/
    └── auth-provider.tsx           # JWT auth context
```

### Auth Pattern

All protected pages are wrapped in `<ProtectedRoute>`. The `useAuth()` hook provides:
- `token` — current JWT
- `user` — decoded user object
- `activeOrgId` — current organization context
- `logout()` — clears session

### API Calls Pattern

All fetch calls follow this pattern:
```typescript
const res = await fetch('/api/v1/resource', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-Project-ID': projectId,   // for project-scoped endpoints
    'X-Org-ID': activeOrgId,     // for org-scoped endpoints
  },
  body: JSON.stringify(payload),
})
```

---

## AI Orchestrator: LangGraph

### Directory Layout

```text
apps/ai-orchestrator/src/
├── langgraph/
│   ├── state.py         # AgentState TypedDict definition
│   └── graph.py         # StateGraph: nodes, edges, entry point
├── agents/              # (extend here for complex agent logic)
├── tools/               # LangChain tool wrappers
├── prompts/             # Prompt templates
├── memory/              # (extend for Qdrant vector memory)
└── main.py              # FastAPI entry: POST /api/v1/agent/run
```

### AgentState Schema

```python
class AgentState(TypedDict):
    messages: List[dict]          # Full conversation thread
    active_agent: str             # Current routing target
    incident_context: dict        # Incident metadata if applicable
    active_errors: List[str]      # Error strings discovered
    git_branch: str               # Target branch context
    reasoning_timeline: List[dict] # Chronological thought trace
    tool_outputs: List[dict]      # Results from agent tool calls
    confidence_score: float       # Agent confidence (0.0 – 1.0)
```

---

## Adding a New API Endpoint

Follow these four steps:

### Step 1 — Create the Model (if storing data)

```python
# apps/backend/src/models/my_feature.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class MyFeature(SQLModel, table=True):
    __tablename__ = "my_features"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", ondelete="CASCADE")
    name: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Step 2 — Create the Schema

```python
# apps/backend/src/schemas/my_feature.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class MyFeatureCreate(BaseModel):
    name: str = Field(min_length=1)

class MyFeatureResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    model_config = {"from_attributes": True}
```

### Step 3 — Create the Router

```python
# apps/backend/src/routers/my_feature.py
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/my-features", tags=["My Feature"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_my_feature(
    payload: MyFeatureCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    obj = MyFeature(name=payload.name, project_id=...)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
```

### Step 4 — Register in App Factory

```python
# apps/backend/src/routers/__init__.py
from .my_feature import router as my_feature

# apps/backend/src/main.py
from src.routers import ..., my_feature
app.include_router(my_feature)
```

### Step 5 — Write Tests

```python
# apps/backend/tests/test_my_feature.py
from src.models.my_feature import MyFeature

def test_my_feature_instantiation():
    f = MyFeature(project_id=uuid4(), name="Test Feature")
    assert f.name == "Test Feature"
```

---

## Adding a New AI Agent

### Step 1 — Define the Agent Node

Open `apps/ai-orchestrator/src/langgraph/graph.py` and add:

```python
workflow.add_node(
    "my_custom_agent",
    make_agent_node(
        "my_custom_agent",
        "My custom agent response — analysis complete."
    )
)
```

### Step 2 — Add Routing Logic in Supervisor

```python
def supervisor_node(state: AgentState) -> dict:
    message_content = state["messages"][-1].get("content", "").lower()

    if "my-keyword" in message_content:
        next_agent = "my_custom_agent"
    # ... existing conditions
```

### Step 3 — Add Conditional Edge and Terminal Edge

```python
# In add_conditional_edges dict:
"my_custom_agent": "my_custom_agent",

# Add terminal edge
workflow.add_edge("my_custom_agent", END)
```

---

## Database Migrations

OpsPilot uses **Alembic** for schema versioning.

```bash
# Create a new migration
cd apps/backend
poetry run alembic revision --autogenerate -m "add my_feature table"

# Apply all pending migrations
poetry run alembic upgrade head

# Roll back one migration
poetry run alembic downgrade -1

# View current revision
poetry run alembic current
```

Migration files live in `src/database/versions/` with naming convention:
`NNNN_description_of_change.py`

---

## Running Tests

```bash
cd apps/backend

# Run all tests
poetry run pytest tests/

# Run with verbose output
poetry run pytest tests/ -v

# Run a specific test file
poetry run pytest tests/test_ai.py -v

# Run with coverage report
poetry run pytest tests/ --cov=src --cov-report=term-missing
```

Current test suites:

| File | Coverage |
|---|---|
| `tests/test_auth.py` | User, Org, Team model validation |
| `tests/test_projects.py` | Project, Environment, Repository models |
| `tests/test_pipelines.py` | Pipeline, PipelineRun, Artifact models |
| `tests/test_kubernetes.py` | Cluster, Node, Namespace models |
| `tests/test_observability.py` | Incident, Alert models |
| `tests/test_ai.py` | AIConversation, AIMessage models |
| `tests/test_governance.py` | ApiKey, AuditLog, FeatureFlag models |

---

## Code Quality Tools

### Backend

```bash
cd apps/backend

# Lint with Ruff
poetry run ruff check src/

# Format with Ruff
poetry run ruff format src/

# Type-check with mypy
poetry run mypy src/
```

### Frontend

```bash
# Type check Next.js
pnpm --filter frontend tsc --noEmit

# Lint
pnpm --filter frontend lint

# Format with Prettier
pnpm prettier --write apps/frontend/src/
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | PostgreSQL async connection string |
| `REDIS_URL` | ✅ | — | Redis connection string |
| `JWT_SECRET_KEY` | ✅ | — | 256-bit signing secret |
| `JWT_ALGORITHM` | ❌ | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `60` | Token lifetime |
| `PROJECT_NAME` | ❌ | `OpsPilot AI` | API title shown in docs |
| `ENVIRONMENT` | ❌ | `development` | Runtime environment tag |
| `DEBUG` | ❌ | `false` | Enable debug mode |
| `AI_ORCHESTRATOR_URL` | ❌ | `http://localhost:8002` | AI service base URL |

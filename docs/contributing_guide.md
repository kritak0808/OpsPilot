# OpsPilot AI — Contributing Guide

> This guide outlines the process, standards, and expectations for contributing to OpsPilot AI — whether you are fixing a bug, proposing a feature, or improving documentation.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Branch Naming](#branch-naming)
5. [Commit Message Standards](#commit-message-standards)
6. [Pull Request Process](#pull-request-process)
7. [Code Review Guidelines](#code-review-guidelines)
8. [Python Coding Standards](#python-coding-standards)
9. [TypeScript Coding Standards](#typescript-coding-standards)
10. [Testing Requirements](#testing-requirements)
11. [Documentation Requirements](#documentation-requirements)

---

## Code of Conduct

OpsPilot AI is committed to maintaining an inclusive and respectful community.

All contributors are expected to:
- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the project and community
- Show empathy toward other community members

Unacceptable behavior should be reported to the maintainers at `conduct@opspilot.io`.

---

## How to Contribute

### Reporting a Bug

1. Search existing [GitHub Issues](https://github.com/your-org/opspilot/issues) to check for duplicates
2. Open a new issue with the **Bug Report** template
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - OS, browser, and service versions
   - Relevant logs or screenshots

### Proposing a Feature

1. Open a **Feature Request** issue describing the use case
2. Wait for maintainer feedback before starting implementation
3. For large features, open a **design discussion** first

### Making a Code Contribution

1. Fork the repository
2. Create a feature branch
3. Make your changes following the standards in this guide
4. Write tests for your changes
5. Open a Pull Request against `main`

---

## Development Setup

### First-Time Setup

```bash
# Clone your fork
git clone https://github.com/your-username/opspilot.git
cd opspilot

# Add upstream remote
git remote add upstream https://github.com/your-org/opspilot.git

# Install all dependencies
pnpm install
cd apps/backend && poetry install && cd ../..
cd apps/ai-orchestrator && poetry install && cd ../..

# Start infrastructure
docker compose up -d

# Apply migrations and seed data
cd apps/backend
poetry run alembic upgrade head
poetry run python src/database/seed.py
```

### Staying Up to Date

```bash
# Sync your fork with upstream
git fetch upstream
git checkout main
git merge upstream/main
```

---

## Branch Naming

Use this convention for all branches:

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/short-description` | `feat/add-slack-notifications` |
| Bug fix | `fix/short-description` | `fix/pipeline-run-status-update` |
| Documentation | `docs/short-description` | `docs/update-api-reference` |
| Refactor | `refactor/short-description` | `refactor/extract-auth-dependency` |
| Hotfix | `hotfix/short-description` | `hotfix/jwt-decode-null-check` |
| Chore | `chore/short-description` | `chore/upgrade-fastapi-0116` |

---

## Commit Message Standards

OpsPilot follows the **Conventional Commits** specification.

### Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

### Types

| Type | Usage |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, no logic changes |
| `refactor` | Code restructuring, no feature or bug |
| `test` | Adding or updating tests |
| `chore` | Build system, dependency updates |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |

### Scopes

| Scope | Description |
|---|---|
| `auth` | Authentication and JWT |
| `projects` | Project management |
| `pipelines` | CI/CD engine |
| `kubernetes` | Kubernetes integration |
| `observability` | Metrics, logs, incidents |
| `ai` | AI agent platform |
| `governance` | Audit, feature flags, API keys |
| `frontend` | Next.js web console |
| `infra` | Docker, Helm, Terraform |
| `docs` | Documentation |

### Examples

```bash
feat(pipelines): add support for matrix build strategy

fix(auth): handle expired JWT gracefully with 401 response

docs(api): add authentication flow sequence diagram

refactor(kubernetes): extract cluster health check into service class

test(governance): add unit tests for ApiKey hash verification

chore(infra): upgrade PostgreSQL Helm dependency to 13.4
```

### Breaking Changes

```
feat(auth)!: migrate from HS256 to RS256 JWT signing

BREAKING CHANGE: Existing tokens will be invalidated.
All clients must re-authenticate after this deployment.
```

---

## Pull Request Process

### Before Opening a PR

- [ ] All tests pass locally: `poetry run pytest tests/`
- [ ] Linting passes: `poetry run ruff check src/`
- [ ] Type checking passes: `poetry run mypy src/`
- [ ] New tests written for new functionality
- [ ] Existing tests not broken
- [ ] Documentation updated if adding new feature

### PR Title

Use the same format as commit messages:
```
feat(pipelines): add matrix build strategy support
```

### PR Description Template

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Added `MatrixStrategy` model in `src/models/pipeline.py`
- Updated `PipelineRun` to support parallel matrix jobs
- Added UI matrix configuration panel

## Testing
- [ ] Unit tests added for `MatrixStrategy` model
- [ ] Integration test for parallel job execution
- [ ] Manual testing on local Docker Compose stack

## Screenshots (if UI changes)
<!-- Add screenshots here -->

## Breaking Changes
<!-- List any breaking changes and migration path -->

## Related Issues
Closes #123
```

### Review Process

1. Submit PR → automated CI runs (tests, lint, type check)
2. At least **one maintainer approval** required for merge
3. All review comments must be resolved before merge
4. Use **Squash and Merge** to keep a clean commit history

---

## Code Review Guidelines

### For Reviewers

- Review within **48 hours** of PR submission
- Be specific and constructive in feedback — explain the *why*
- Use GitHub suggestion blocks for minor wording changes
- Approve promptly when all concerns are resolved
- Don't block on subjective style preferences unless they violate published standards

### Review Checklist

- [ ] Logic is correct and handles edge cases
- [ ] Security implications considered (auth, data exposure)
- [ ] No hardcoded secrets or credentials
- [ ] Database migrations are reversible
- [ ] API changes are backward compatible (or documented as breaking)
- [ ] Tests cover the happy path and failure scenarios
- [ ] Documentation updated for user-facing changes

---

## Python Coding Standards

### Style

- **Formatter**: Ruff (`poetry run ruff format src/`)
- **Linter**: Ruff (`poetry run ruff check src/`)
- **Type checker**: mypy (`poetry run mypy src/`)
- **Line length**: 100 characters
- **Quotes**: Double quotes for strings

### Naming Conventions

```python
# Modules and packages — snake_case
from src.models.my_feature import MyFeatureModel

# Classes — PascalCase
class PipelineRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"

# Functions and variables — snake_case
async def get_pipeline_run(run_id: UUID, db: AsyncSession) -> PipelineRun:
    ...

# Constants — UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
```

### Async Patterns

All database operations must be async:

```python
# ✅ Correct
result = await db.execute(select(Project).where(Project.id == project_id))
project = result.scalar_one_or_none()

# ❌ Incorrect — never use sync db calls in async context
project = db.query(Project).filter(Project.id == project_id).first()
```

### Error Handling

```python
# ✅ Raise HTTPException from routers
@router.get("/{id}")
async def get_project(id: UUID, db: AsyncSession = Depends(get_session)):
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# ✅ Use specific exception types — never bare except
try:
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    raise HTTPException(status_code=409, detail="Duplicate entry")
```

### Database Models

```python
class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        ondelete="CASCADE",
        nullable=False,
        index=True,  # Always index foreign keys
    )
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

---

## TypeScript Coding Standards

### Style

- **Formatter**: Prettier
- **Linter**: ESLint
- **Type checking**: `tsc --noEmit`
- Always prefer `const` over `let`
- Use `async/await` over `.then()` chains

### Naming Conventions

```typescript
// Interfaces — PascalCase
interface PipelineRun {
  id: string
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED'
  startedAt: string
}

// Components — PascalCase
export function PipelineStatusBadge({ status }: { status: string }) {
  ...
}

// Functions and variables — camelCase
const fetchPipelineRuns = async (projectId: string) => {
  ...
}
```

### Fetch Pattern

```typescript
// Always type the response body
const res = await fetch('/api/v1/pipelines', {
  headers: { Authorization: `Bearer ${token}` },
})

if (!res.ok) {
  throw new Error(`Failed to fetch pipelines: ${res.statusText}`)
}

const data: PipelineRun[] = await res.json()
```

---

## Testing Requirements

### Backend Testing

Every new endpoint or model must have at least one test.

**Model tests** — validate instantiation and field constraints:
```python
def test_pipeline_creation():
    p = Pipeline(project_id=uuid4(), name="Main Build")
    assert p.name == "Main Build"
    assert p.id is not None
```

**Router tests** — use `httpx.AsyncClient` with the FastAPI test app:
```python
@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/projects", json={"name": "Test"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test"
```

Run tests:
```bash
cd apps/backend
poetry run pytest tests/ -v --cov=src
```

**Minimum coverage target: 80%**

---

## Documentation Requirements

For every **user-facing** change, update the relevant documentation file in `docs/`:

| Change Type | Document to Update |
|---|---|
| New endpoint | `docs/api_documentation.md` |
| New AI agent | `docs/ai_documentation.md` |
| New deployment option | `docs/deployment_guide.md` |
| Security change | `docs/security_guide.md` |
| New developer workflow | `docs/developer_guide.md` |
| Architecture change | `docs/architecture_guide.md` |

Documentation PRs do not require code changes to be merged — docs-only contributions are welcomed.

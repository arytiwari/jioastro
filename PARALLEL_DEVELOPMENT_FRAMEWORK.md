# Parallel Development Framework for JioAstro

## Overview

This framework enables multiple developers (human or AI assistants like Claude) to work on different features from the Magical 12 roadmap concurrently without conflicts. It establishes clear boundaries, conventions, and processes for conflict-free parallel development.

## Table of Contents

1. [Architecture Principles](#architecture-principles)
2. [Feature Module Pattern](#feature-module-pattern)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Git Strategy](#git-strategy)
6. [Database Management](#database-management)
7. [API Versioning](#api-versioning)
8. [Feature Flags](#feature-flags)
9. [Testing Strategy](#testing-strategy)
10. [Code Review Guidelines](#code-review-guidelines)
11. [Conflict Resolution](#conflict-resolution)

---

## Architecture Principles

### 1. **Modular Design**
- Each feature is a self-contained module with clear boundaries
- Modules communicate through well-defined interfaces
- No direct dependencies between feature modules

### 2. **Separation of Concerns**
```
Core Layer (Shared)
├── Authentication & Authorization
├── Database Connection
├── Common Models
├── Shared Utilities
└── Base Services

Feature Layer (Independent)
├── Feature A (Life Snapshot)
├── Feature B (Life Threads)
├── Feature C (Decision Copilot)
└── ... (Other Magical 12 features)

Integration Layer
├── API Gateway
├── Event Bus
└── Service Registry
```

### 3. **Interface Contracts**
- Each feature exposes a well-defined API contract
- Contracts are versioned and documented
- Breaking changes require version bumps

### 4. **Feature Isolation**
- Features can be developed, tested, and deployed independently
- Feature flags control visibility
- Shared resources accessed through abstraction layers

---

## Feature Module Pattern

### Backend Feature Module Structure

```
backend/app/features/<feature_name>/
├── __init__.py                 # Module exports
├── README.md                   # Feature documentation
├── config.py                   # Feature-specific configuration
├── models.py                   # Database models (Alembic migrations)
├── schemas.py                  # Pydantic request/response schemas
├── service.py                  # Business logic
├── api.py                      # FastAPI route handlers
├── dependencies.py             # Feature-specific dependencies
├── constants.py                # Feature constants
├── exceptions.py               # Custom exceptions
└── tests/
    ├── test_models.py
    ├── test_service.py
    ├── test_api.py
    └── fixtures.py
```

### Frontend Feature Module Structure

```
frontend/features/<feature_name>/
├── README.md                   # Feature documentation
├── index.ts                    # Module exports
├── types.ts                    # TypeScript interfaces
├── api.ts                      # API client methods
├── hooks/                      # React hooks
│   ├── use<Feature>.ts
│   └── use<Feature>Data.ts
├── components/                 # Feature-specific components
│   ├── <Feature>Card.tsx
│   ├── <Feature>List.tsx
│   └── <Feature>Detail.tsx
├── pages/                      # Feature pages
│   └── <feature>.tsx
├── utils/                      # Feature utilities
│   └── helpers.ts
├── constants.ts                # Feature constants
└── __tests__/                  # Unit tests
    ├── components/
    └── hooks/
```

### Feature Registration

Each feature must register itself in the application:

**Backend** (`backend/app/features/registry.py`):
```python
from typing import Dict, Type
from .base import BaseFeature

class FeatureRegistry:
    _features: Dict[str, Type[BaseFeature]] = {}

    @classmethod
    def register(cls, feature: Type[BaseFeature]):
        cls._features[feature.name] = feature

    @classmethod
    def get_feature(cls, name: str) -> Type[BaseFeature]:
        return cls._features.get(name)
```

**Frontend** (`frontend/features/registry.ts`):
```typescript
interface FeatureConfig {
  name: string;
  route: string;
  component: React.ComponentType;
  enabled: boolean;
}

export class FeatureRegistry {
  private static features: Map<string, FeatureConfig> = new Map();

  static register(config: FeatureConfig): void {
    this.features.set(config.name, config);
  }

  static getFeature(name: string): FeatureConfig | undefined {
    return this.features.get(name);
  }
}
```

---

## Project Structure

### Updated Backend Structure

```
backend/
├── app/
│   ├── core/                   # Core shared functionality
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── events.py
│   ├── common/                 # Shared across features
│   │   ├── models/            # Base models
│   │   ├── schemas/           # Common schemas
│   │   ├── services/          # Shared services
│   │   └── utils/             # Utilities
│   ├── features/              # Feature modules (NEW)
│   │   ├── __init__.py
│   │   ├── base.py            # BaseFeature class
│   │   ├── registry.py        # Feature registry
│   │   ├── life_snapshot/     # Feature 1
│   │   ├── life_threads/      # Feature 2
│   │   ├── decision_copilot/  # Feature 3
│   │   ├── transit_pulse/     # Feature 4
│   │   ├── remedy_planner/    # Feature 5
│   │   ├── astrotwin_graph/   # Feature 6
│   │   ├── guided_rituals/    # Feature 7
│   │   ├── evidence_mode/     # Feature 8
│   │   ├── expert_console/    # Feature 9
│   │   ├── reality_check/     # Feature 10
│   │   ├── hyperlocal_panchang/ # Feature 11
│   │   └── story_reels/       # Feature 12
│   ├── legacy/                # Legacy code (to be refactored)
│   │   ├── api/v1/endpoints/  # Old endpoints
│   │   ├── models/            # Old models
│   │   ├── schemas/           # Old schemas
│   │   └── services/          # Old services
│   └── main.py
├── migrations/                 # Alembic migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── scripts/
    └── feature_generator.py   # CLI to scaffold new features
```

### Updated Frontend Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── dashboard/
│   │   └── [feature]/         # Dynamic feature routes
│   ├── layout.tsx
│   └── page.tsx
├── features/                   # Feature modules (NEW)
│   ├── index.ts
│   ├── registry.ts
│   ├── life-snapshot/
│   ├── life-threads/
│   ├── decision-copilot/
│   ├── transit-pulse/
│   ├── remedy-planner/
│   ├── astrotwin-graph/
│   ├── guided-rituals/
│   ├── evidence-mode/
│   ├── expert-console/
│   ├── reality-check/
│   ├── hyperlocal-panchang/
│   └── story-reels/
├── components/                 # Shared components
│   ├── ui/                    # shadcn/ui
│   └── common/                # Shared across features
├── lib/                        # Shared utilities
│   ├── api.ts
│   ├── feature-flags.ts       # Feature flag client
│   └── utils.ts
├── hooks/                      # Shared hooks
└── types/                      # Shared TypeScript types
```

---

## Development Workflow

### Step 1: Feature Assignment

Each developer/AI assistant is assigned a feature from the Magical 12:

```bash
# Developer/AI 1 assigned to: Life Snapshot (Feature #1)
# Developer/AI 2 assigned to: Life Threads (Feature #2)
# Developer/AI 3 assigned to: Decision Copilot (Feature #3)
```

### Step 2: Branch Creation

```bash
# Naming convention: feature/<feature-name>-<ticket-id>
git checkout main
git pull origin main
git checkout -b feature/life-snapshot-MAG-001
```

### Step 3: Feature Scaffolding

Use the feature generator CLI:

```bash
# Backend
cd backend
python scripts/feature_generator.py generate life_snapshot \
  --description "60-second personalized life insights" \
  --author "AI Assistant 1"

# Frontend
cd frontend
npm run generate:feature life-snapshot \
  --description "Life Snapshot UI" \
  --author "AI Assistant 1"
```

### Step 4: Development

**Backend Development Checklist:**
- [ ] Create database models in `features/<name>/models.py`
- [ ] Create Alembic migration: `alembic revision --autogenerate -m "Add <feature> tables"`
- [ ] Define Pydantic schemas in `features/<name>/schemas.py`
- [ ] Implement business logic in `features/<name>/service.py`
- [ ] Create API endpoints in `features/<name>/api.py`
- [ ] Register feature in `features/registry.py`
- [ ] Write unit tests (100% coverage target)
- [ ] Update feature README.md
- [ ] Add feature flag check

**Frontend Development Checklist:**
- [ ] Define TypeScript interfaces in `features/<name>/types.ts`
- [ ] Create API client methods in `features/<name>/api.ts`
- [ ] Build React components in `features/<name>/components/`
- [ ] Create custom hooks in `features/<name>/hooks/`
- [ ] Implement feature pages in `features/<name>/pages/`
- [ ] Register feature in `features/registry.ts`
- [ ] Write component tests
- [ ] Update feature README.md
- [ ] Add feature flag check

### Step 5: Testing

```bash
# Backend
cd backend
pytest tests/features/<feature_name>/ -v --cov

# Frontend
cd frontend
npm test features/<feature-name>
```

### Step 6: Pull Request

```bash
git add .
git commit -m "feat: implement life snapshot feature (MAG-001)"
git push origin feature/life-snapshot-MAG-001

# Create PR with template
gh pr create --template feature-pr.md
```

### Step 7: Code Review & Merge

- Automated tests must pass
- Code review by at least 1 other developer/AI
- Feature flag enabled for testing environment
- Merge to main after approval

---

## Git Strategy

### Branch Naming Convention

```
feature/<feature-name>-<ticket-id>    # New features
bugfix/<feature-name>-<ticket-id>     # Bug fixes
hotfix/<issue-description>             # Production hotfixes
refactor/<component-name>              # Code refactoring
docs/<document-name>                   # Documentation updates
test/<test-description>                # Test additions
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(life-snapshot): add 60-second insight generation

- Implement snapshot algorithm using transit data
- Create caching layer for performance
- Add unit tests with 95% coverage

Closes MAG-001
```

### Branch Protection Rules

**Main Branch:**
- Require pull request reviews (1 minimum)
- Require status checks to pass
- Require linear history (rebase or squash merge)
- No force pushes
- No deletions

**Feature Branches:**
- Can be force-pushed during development
- Deleted after merge

### Merge Strategy

1. **Squash and Merge** for feature branches (clean history)
2. **Rebase and Merge** for small bug fixes
3. **Merge Commit** for release branches (preserves history)

---

## Database Management

### Migration Strategy

Each feature manages its own database schema through Alembic migrations.

#### Naming Convention

```
<timestamp>_<feature_name>_<description>.py

Example: 20250107_life_snapshot_add_snapshot_table.py
```

#### Migration Workflow

1. **Create Migration:**
```bash
cd backend
alembic revision --autogenerate -m "life_snapshot: add snapshot table"
```

2. **Review Migration:**
- Check generated SQL
- Ensure backward compatibility
- Add data migration if needed

3. **Test Migration:**
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test re-upgrade
alembic upgrade head
```

4. **Commit Migration:**
```bash
git add migrations/versions/<migration_file>.py
git commit -m "db: add life_snapshot tables (MAG-001)"
```

#### Avoiding Conflicts

**Rule 1: Feature-Specific Tables**
- Prefix table names with feature identifier
```python
# Good
life_snapshot_data
life_threads_events
decision_copilot_recommendations

# Bad (shared table, causes conflicts)
user_data
events
recommendations
```

**Rule 2: Independent Migrations**
- Never modify tables from other features
- Use views or foreign keys for cross-feature queries
- Communicate schema dependencies in PR description

**Rule 3: Migration Review**
- All migrations reviewed before merge
- Check for table name conflicts
- Check for index name conflicts
- Check for constraint name conflicts

#### Cross-Feature Data Access

Use **database views** or **service interfaces**:

```sql
-- View for cross-feature queries
CREATE VIEW user_insights AS
SELECT
  u.id,
  ls.snapshot_data,
  lt.timeline_data
FROM users u
LEFT JOIN life_snapshot_data ls ON u.id = ls.user_id
LEFT JOIN life_threads_events lt ON u.id = lt.user_id;
```

---

## API Versioning

### Versioning Strategy

```
/api/v1/...  # Legacy APIs (existing)
/api/v2/...  # New feature APIs (with feature flags)
```

### Endpoint Naming Convention

```
/api/v2/<feature-name>/<resource>

Examples:
/api/v2/life-snapshot/generate
/api/v2/life-threads/timeline
/api/v2/decision-copilot/recommend
```

### Feature-Specific Routers

Each feature registers its own router:

```python
# backend/app/features/life_snapshot/api.py
from fastapi import APIRouter, Depends
from app.core.feature_flags import require_feature

router = APIRouter(prefix="/life-snapshot", tags=["Life Snapshot"])

@router.post("/generate")
@require_feature("life_snapshot")
async def generate_snapshot(
    user: dict = Depends(get_current_user)
):
    """Generate 60-second life snapshot."""
    # Implementation
    pass
```

### Router Registration

```python
# backend/app/main.py
from app.features import life_snapshot, life_threads, decision_copilot

# V2 API Router
api_v2 = APIRouter(prefix="/api/v2")

# Register feature routers
api_v2.include_router(life_snapshot.router)
api_v2.include_router(life_threads.router)
api_v2.include_router(decision_copilot.router)

app.include_router(api_v2)
```

---

## Feature Flags

### Implementation

**Backend:**

```python
# backend/app/core/feature_flags.py
from enum import Enum
from functools import wraps
from fastapi import HTTPException, status
import os

class Feature(Enum):
    LIFE_SNAPSHOT = "life_snapshot"
    LIFE_THREADS = "life_threads"
    DECISION_COPILOT = "decision_copilot"
    TRANSIT_PULSE = "transit_pulse"
    REMEDY_PLANNER = "remedy_planner"
    ASTROTWIN_GRAPH = "astrotwin_graph"
    GUIDED_RITUALS = "guided_rituals"
    EVIDENCE_MODE = "evidence_mode"
    EXPERT_CONSOLE = "expert_console"
    REALITY_CHECK = "reality_check"
    HYPERLOCAL_PANCHANG = "hyperlocal_panchang"
    STORY_REELS = "story_reels"

class FeatureFlags:
    """Feature flag management."""

    def __init__(self):
        self._flags = self._load_flags()

    def _load_flags(self) -> dict:
        """Load feature flags from environment."""
        return {
            feature: os.getenv(f"FEATURE_{feature.value.upper()}", "false").lower() == "true"
            for feature in Feature
        }

    def is_enabled(self, feature: Feature) -> bool:
        """Check if feature is enabled."""
        return self._flags.get(feature, False)

    def enable(self, feature: Feature):
        """Enable a feature."""
        self._flags[feature] = True

    def disable(self, feature: Feature):
        """Disable a feature."""
        self._flags[feature] = False

feature_flags = FeatureFlags()

def require_feature(feature_name: str):
    """Decorator to require feature flag."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            feature = Feature(feature_name)
            if not feature_flags.is_enabled(feature):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Feature '{feature_name}' is not enabled"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

**Frontend:**

```typescript
// frontend/lib/feature-flags.ts
export enum Feature {
  LIFE_SNAPSHOT = 'life_snapshot',
  LIFE_THREADS = 'life_threads',
  DECISION_COPILOT = 'decision_copilot',
  TRANSIT_PULSE = 'transit_pulse',
  REMEDY_PLANNER = 'remedy_planner',
  ASTROTWIN_GRAPH = 'astrotwin_graph',
  GUIDED_RITUALS = 'guided_rituals',
  EVIDENCE_MODE = 'evidence_mode',
  EXPERT_CONSOLE = 'expert_console',
  REALITY_CHECK = 'reality_check',
  HYPERLOCAL_PANCHANG = 'hyperlocal_panchang',
  STORY_REELS = 'story_reels',
}

class FeatureFlags {
  private flags: Map<Feature, boolean> = new Map();

  constructor() {
    this.loadFlags();
  }

  private loadFlags(): void {
    // Load from environment variables
    Object.values(Feature).forEach((feature) => {
      const envKey = `NEXT_PUBLIC_FEATURE_${feature.toUpperCase()}`;
      this.flags.set(feature, process.env[envKey] === 'true');
    });
  }

  isEnabled(feature: Feature): boolean {
    return this.flags.get(feature) ?? false;
  }

  enable(feature: Feature): void {
    this.flags.set(feature, true);
  }

  disable(feature: Feature): void {
    this.flags.set(feature, false);
  }
}

export const featureFlags = new FeatureFlags();

// React hook
export function useFeatureFlag(feature: Feature): boolean {
  return featureFlags.isEnabled(feature);
}
```

**Usage:**

```typescript
// In a component
import { useFeatureFlag, Feature } from '@/lib/feature-flags';

export function LifeSnapshotButton() {
  const isEnabled = useFeatureFlag(Feature.LIFE_SNAPSHOT);

  if (!isEnabled) return null;

  return <button>Generate Life Snapshot</button>;
}
```

### Environment Configuration

**Development (.env):**
```bash
# Enable all features in development
FEATURE_LIFE_SNAPSHOT=true
FEATURE_LIFE_THREADS=true
FEATURE_DECISION_COPILOT=true
# ... all other features
```

**Staging (.env.staging):**
```bash
# Enable features under testing
FEATURE_LIFE_SNAPSHOT=true
FEATURE_LIFE_THREADS=false
FEATURE_DECISION_COPILOT=false
```

**Production (.env.production):**
```bash
# Enable only production-ready features
FEATURE_LIFE_SNAPSHOT=false  # Not ready yet
FEATURE_LIFE_THREADS=false
```

---

## Testing Strategy

### Test Organization

```
backend/tests/
├── unit/                      # Fast, isolated tests
│   └── features/
│       ├── life_snapshot/
│       ├── life_threads/
│       └── ...
├── integration/               # Feature integration tests
│   └── features/
│       ├── life_snapshot/
│       └── ...
└── e2e/                      # End-to-end tests
    └── scenarios/
        ├── user_journey_life_snapshot.py
        └── ...

frontend/__tests__/
├── unit/
│   └── features/
│       ├── life-snapshot/
│       └── ...
├── integration/
│   └── features/
└── e2e/
    └── scenarios/
```

### Test Isolation

**Rule: Feature tests must not depend on other features**

```python
# Good - isolated test
def test_life_snapshot_generation():
    snapshot_service = LifeSnapshotService()
    result = snapshot_service.generate(user_id="test_user")
    assert result.insights is not None

# Bad - depends on another feature
def test_life_snapshot_with_threads():
    # Depends on Life Threads feature
    threads_service = LifeThreadsService()  # ❌
    snapshot_service = LifeSnapshotService()
    # ...
```

### Test Coverage Requirements

- **Unit Tests:** ≥ 90% coverage per feature
- **Integration Tests:** ≥ 80% coverage for critical paths
- **E2E Tests:** Cover main user journeys

### Running Tests

```bash
# Run all tests
pytest

# Run tests for specific feature
pytest tests/unit/features/life_snapshot/
pytest tests/integration/features/life_snapshot/

# Run with coverage
pytest --cov=app/features/life_snapshot --cov-report=html

# Frontend
npm test features/life-snapshot
npm run test:coverage
```

---

## Code Review Guidelines

### Review Checklist

**Architecture & Design:**
- [ ] Feature follows module pattern
- [ ] No dependencies on other features
- [ ] Clear interfaces and contracts
- [ ] Proper error handling

**Code Quality:**
- [ ] Follows coding standards (PEP 8, ESLint)
- [ ] No code duplication
- [ ] Meaningful variable/function names
- [ ] Proper typing (Python type hints, TypeScript)

**Testing:**
- [ ] Unit tests present and passing
- [ ] Integration tests for critical paths
- [ ] Test coverage meets requirements (≥90%)
- [ ] Edge cases covered

**Database:**
- [ ] Migrations reviewed and tested
- [ ] No conflicts with existing tables
- [ ] Proper indexing for performance
- [ ] Backward compatible

**API:**
- [ ] Follows RESTful conventions
- [ ] Proper HTTP status codes
- [ ] Request/response validation
- [ ] API documentation updated

**Security:**
- [ ] Authentication/authorization checks
- [ ] Input validation
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Sensitive data encrypted

**Performance:**
- [ ] No N+1 query problems
- [ ] Proper caching where needed
- [ ] Efficient algorithms
- [ ] Database queries optimized

**Documentation:**
- [ ] Feature README.md updated
- [ ] API docs generated
- [ ] Code comments for complex logic
- [ ] CHANGELOG.md updated

**Feature Flags:**
- [ ] Feature flag implemented
- [ ] Default to disabled in production
- [ ] Graceful degradation if disabled

### Review Process

1. **Automated Checks:** CI/CD pipeline runs tests, linters, security scans
2. **AI Review:** Use AI assistant to review code quality, patterns, security
3. **Human Review:** At least 1 developer reviews for logic, architecture, UX
4. **Approval:** Requires all checks passing + 1 approval
5. **Merge:** Squash and merge to main

---

## Conflict Resolution

### Common Conflicts & Solutions

#### 1. Database Migration Conflicts

**Problem:** Two features create migrations with conflicting version numbers.

**Solution:**
```bash
# Rebase your feature branch
git checkout feature/your-feature
git fetch origin main
git rebase origin/main

# Regenerate migration with new version number
alembic revision --autogenerate -m "your feature: description"

# Resolve conflicts manually
# Commit and push
```

#### 2. API Route Conflicts

**Problem:** Two features try to register the same endpoint.

**Solution:**
- Use feature-specific prefixes: `/api/v2/<feature-name>/...`
- Review API registry before implementing
- Coordinate in team channel

#### 3. Shared Component Conflicts

**Problem:** Two features modify the same shared component.

**Solution:**
- Create feature-specific variants if needed
- Discuss with team before modifying shared components
- Use composition over modification

#### 4. Import Conflicts

**Problem:** Circular imports between features.

**Solution:**
```python
# Bad - circular import
from app.features.life_threads import LifeThreadsService  # ❌

# Good - use dependency injection
from app.core.dependencies import get_service

async def my_endpoint(
    threads_service = Depends(get_service(LifeThreadsService))
):
    # Use threads_service
    pass
```

#### 5. Test Data Conflicts

**Problem:** Tests from different features interfere with each other.

**Solution:**
```python
# Use isolated test databases
@pytest.fixture(scope="function")
def db_session():
    """Create isolated test database session."""
    # Create test DB
    # Run migrations
    # Yield session
    # Cleanup
    pass

# Use unique test data prefixes
test_user_id = f"test_{feature_name}_{uuid4()}"
```

---

## Quick Reference

### Command Cheat Sheet

```bash
# Create new feature branch
git checkout -b feature/<name>-<ticket-id>

# Generate feature scaffold (backend)
python scripts/feature_generator.py generate <name>

# Generate feature scaffold (frontend)
npm run generate:feature <name>

# Create database migration
alembic revision --autogenerate -m "<feature>: <description>"

# Run feature tests
pytest tests/unit/features/<name>/ -v

# Check feature test coverage
pytest --cov=app/features/<name> --cov-report=term

# Enable feature flag (dev)
export FEATURE_<NAME>=true

# Create pull request
gh pr create --template feature-pr.md

# Merge feature branch
git checkout main && git merge --squash feature/<name>
```

### Feature Checklist Template

Save as `.github/PULL_REQUEST_TEMPLATE/feature-pr.md`:

```markdown
## Feature: [Feature Name]

### Description
Brief description of the feature and its purpose.

### Magical 12 Reference
- [ ] Feature #X: [Feature Name from Roadmap]

### Implementation Checklist

**Backend:**
- [ ] Models created in `features/<name>/models.py`
- [ ] Migration created and tested
- [ ] Schemas defined in `features/<name>/schemas.py`
- [ ] Service logic implemented
- [ ] API endpoints created
- [ ] Feature registered in registry
- [ ] Feature flag implemented
- [ ] Unit tests (≥90% coverage)
- [ ] Integration tests
- [ ] API documentation updated

**Frontend:**
- [ ] Types defined in `features/<name>/types.ts`
- [ ] API client methods created
- [ ] Components implemented
- [ ] Hooks created
- [ ] Pages implemented
- [ ] Feature registered in registry
- [ ] Feature flag check added
- [ ] Component tests
- [ ] E2E tests for critical paths

**Documentation:**
- [ ] Feature README.md created/updated
- [ ] API documentation generated
- [ ] CHANGELOG.md updated
- [ ] Migration guide (if needed)

**Code Quality:**
- [ ] All linters passing
- [ ] All tests passing
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Security scan passing

### Testing
Describe how to test this feature:
1. Enable feature flag: `FEATURE_<NAME>=true`
2. Run migrations: `alembic upgrade head`
3. Test scenarios:
   - ...

### Screenshots/Demo
[Add screenshots or demo video]

### Related Issues
Closes #[issue-number]

### Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes (describe below)

### Deployment Notes
Any special considerations for deployment?

---

**Reviewer Checklist:**
- [ ] Code follows project conventions
- [ ] Tests are comprehensive
- [ ] No conflicts with other features
- [ ] Feature flag properly implemented
- [ ] Documentation complete
```

---

## Next Steps

1. **Set up feature flag system** (see [Feature Flags](#feature-flags))
2. **Create feature scaffolding scripts** (see `scripts/feature_generator.py` template)
3. **Update CI/CD pipeline** for feature branch testing
4. **Create feature documentation templates**
5. **Train team on parallel development workflow**

---

## Support & Questions

For questions about this framework:
- Review this document first
- Check feature README files
- Ask in team channel
- Create GitHub discussion

**Happy Parallel Development! 🚀**

# Developer Quick Start Guide

## For Multiple Parallel Developers (Human or AI)

This guide helps you get started working on JioAstro features in parallel with other developers.

## Prerequisites

- Read `PARALLEL_DEVELOPMENT_FRAMEWORK.md`
- Have access to the repository
- Backend: Python 3.11+, PostgreSQL, Redis
- Frontend: Node.js 18+, npm

## Quick Start (5 Minutes)

### 1. Clone & Setup

```bash
git clone https://github.com/arytiwari/jioastro.git
cd jioastro

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Get Your Feature Assignment

Check which Magical 12 feature you're assigned:

| # | Feature | Status |
|---|---------|--------|
| 1 | Life Snapshot | 🟡 Template Ready |
| 2 | Life Threads | ⚪ Available |
| 3 | Decision Copilot | ⚪ Available |
| 4 | Transit Pulse | ⚪ Available |
| 5 | Remedy Planner | ⚪ Available |
| 6 | AstroTwin Graph | ⚪ Available |
| 7 | Guided Rituals | ⚪ Available |
| 8 | Evidence Mode | ⚪ Available |
| 9 | Expert Console | ⚪ Available |
| 10 | Reality Check | ⚪ Available |
| 11 | Hyperlocal Panchang | ⚪ Available |
| 12 | Story Reels | ⚪ Available |

### 3. Create Your Feature Branch

```bash
# Example for Life Threads feature
git checkout -b feature/life-threads-MAG-002
```

### 4. Generate Feature Scaffold

```bash
cd backend

# Generate backend feature
python scripts/feature_generator.py generate life_threads \
  --description "Zoomable life journey timeline visualization" \
  --author "Your Name or AI Assistant X" \
  --magical-number 2
```

**Output:**
```
Creating feature directory: backend/app/features/life_threads
  ✓ Created __init__.py
  ✓ Created README.md
  ✓ Created feature.py
  ✓ Created models.py
  ✓ Created schemas.py
  ✓ Created service.py
  ✓ Created constants.py
  ✓ Created tests/test_service.py

✅ Feature 'life_threads' generated successfully!
```

### 5. Enable Feature Flag

```bash
# Add to backend/.env
echo "FEATURE_LIFE_THREADS=true" >> backend/.env

# Add to frontend/.env.local
echo "NEXT_PUBLIC_FEATURE_LIFE_THREADS=true" >> frontend/.env.local
```

### 6. Create Database Migration

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "life_threads: add timeline tables"

# Review migration file in migrations/versions/

# Apply migration
alembic upgrade head
```

### 7. Implement Your Feature

**Backend Implementation Order:**

1. **Models** (`models.py`) - Define database schema
2. **Schemas** (`schemas.py`) - Define request/response formats
3. **Service** (`service.py`) - Implement business logic
4. **API** (`feature.py`) - Add endpoints to router
5. **Tests** (`tests/`) - Write comprehensive tests

**Frontend Implementation Order:**

1. **Types** (`types.ts`) - TypeScript interfaces
2. **API Client** (`api.ts`) - API methods
3. **Hooks** (`hooks/`) - React hooks for data fetching
4. **Components** (`components/`) - UI components
5. **Pages** (`pages/`) - Feature pages
6. **Tests** (`__tests__/`) - Component & hook tests

### 8. Run Tests

```bash
# Backend
cd backend
pytest app/features/life_threads/tests/ -v
pytest --cov=app/features/life_threads

# Frontend
cd frontend
npm test features/life-threads
```

### 9. Test Locally

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Visit: http://localhost:3000
```

### 10. Create Pull Request

```bash
git add .
git commit -m "feat(life-threads): implement zoomable timeline feature (MAG-002)"
git push origin feature/life-threads-MAG-002

# Create PR
gh pr create --title "feat: Life Threads timeline visualization" \
  --body "Implements Magical 12 Feature #2..."
```

## Feature Development Checklist

Copy this checklist for each feature:

```markdown
## Feature: [Name] (#X)

### Backend
- [ ] Generate feature scaffold
- [ ] Create database models
- [ ] Create Alembic migration
- [ ] Define Pydantic schemas
- [ ] Implement service logic
- [ ] Create API endpoints
- [ ] Add feature flag check
- [ ] Write unit tests (≥90% coverage)
- [ ] Write integration tests
- [ ] Update feature README

### Frontend
- [ ] Define TypeScript types
- [ ] Create API client methods
- [ ] Build React hooks
- [ ] Create components
- [ ] Implement pages
- [ ] Add feature flag check
- [ ] Write component tests
- [ ] Write E2E tests
- [ ] Update feature README

### Integration
- [ ] Test backend-frontend integration
- [ ] Test feature flag toggling
- [ ] Performance testing
- [ ] Security review
- [ ] Documentation complete

### Deployment
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Feature flag disabled in production
- [ ] Deployment plan documented
```

## Working in Parallel

### Rule #1: Feature Isolation

**DO:**
- Work only in your feature directory (`app/features/your_feature/`)
- Use feature-prefixed table names (`your_feature_data`)
- Create feature-specific migrations
- Test independently

**DON'T:**
- Modify other features' files
- Touch shared tables directly
- Skip feature flag checks
- Depend on other in-development features

### Rule #2: Communication

**Before You Start:**
- Announce your feature assignment in team channel
- Check for potential conflicts
- Review related features in roadmap

**During Development:**
- Update feature status regularly
- Report blockers immediately
- Ask questions in team channel
- Share progress weekly

**Before Merge:**
- Run full test suite
- Check for migration conflicts
- Update documentation
- Get code review

### Rule #3: Database Safety

```bash
# ALWAYS prefix table names with feature name
# Good:
life_threads_events
life_threads_milestones

# Bad (conflicts with other features):
events
milestones
```

### Rule #4: API Endpoints

```bash
# ALWAYS use feature prefix
# Good:
/api/v2/life-threads/timeline
/api/v2/life-threads/events

# Bad (conflicts):
/api/v2/timeline
/api/v2/events
```

## Common Issues & Solutions

### Issue: Migration Conflict

```bash
# If you see: "Multiple head revisions are present"
alembic heads

# Merge migrations
alembic merge -m "merge migrations" <rev1> <rev2>

# Or regenerate your migration after rebasing
git rebase origin/main
alembic revision --autogenerate -m "your_feature: description"
```

### Issue: Import Conflicts

```python
# Bad - circular import
from app.features.other_feature import SomeService

# Good - dependency injection
from app.core.dependencies import get_service
service = get_service(SomeService)
```

### Issue: Feature Not Visible

```bash
# Check feature flag
echo $FEATURE_YOUR_FEATURE  # Should output: true

# Check feature registration
curl http://localhost:8000/api/v2/features

# Check logs
tail -f backend.log | grep "your_feature"
```

## AI Assistant Instructions

If you're an AI assistant (like Claude) working on a feature:

1. **Read the feature README** in `app/features/<feature_name>/README.md`
2. **Follow the checklist** exactly
3. **Write tests first** (TDD approach)
4. **Document as you go** - update README with your progress
5. **Ask for clarification** if requirements are unclear
6. **Report completion** with summary when done

### Example AI Workflow

```
1. Receive assignment: "Implement Life Threads feature"
2. Read: PARALLEL_DEVELOPMENT_FRAMEWORK.md
3. Read: MAGICAL_12_PRODUCT_ROADMAP.md (Feature #2)
4. Generate scaffold: python scripts/feature_generator.py...
5. Read generated README: app/features/life_threads/README.md
6. Implement step-by-step following checklist
7. Run tests after each step
8. Update README with implementation notes
9. Create PR with comprehensive description
10. Report: "Life Threads feature implemented. PR #X ready for review."
```

## Resources

- **Architecture:** `PARALLEL_DEVELOPMENT_FRAMEWORK.md`
- **Product Vision:** `MAGICAL_12_PRODUCT_ROADMAP.md`
- **Project Context:** `CLAUDE.md`
- **API Docs:** http://localhost:8000/docs (when running)
- **Feature Status:** Check `.github/projects/magical-12` board

## Getting Help

1. **Check documentation first:**
   - Framework docs
   - Feature README
   - Existing similar features

2. **Search for solutions:**
   - GitHub issues
   - Team channel history
   - Code comments

3. **Ask for help:**
   - Team channel
   - Create GitHub discussion
   - Tag relevant developers

## Success Metrics

Your feature is ready when:

- ✅ All tests passing (≥90% coverage)
- ✅ Feature flag working
- ✅ No conflicts with other features
- ✅ Documentation complete
- ✅ Code reviewed and approved
- ✅ Performance targets met
- ✅ Security checks passed

---

**Welcome to parallel development! Let's build amazing features together! 🚀**

*Last Updated: 2025-11-07*

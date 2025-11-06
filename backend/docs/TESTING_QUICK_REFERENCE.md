# JioAstro Testing - Quick Reference

A condensed reference guide for common testing tasks. For comprehensive documentation, see [TESTING.md](./TESTING.md).

---

## Quick Commands

### Before Any Commit
```bash
# Run smoke tests (< 30s)
./scripts/run_smoke_tests.sh

# Or use pre-commit hooks
pre-commit run --all-files
```

### Before Pull Request
```bash
# Run full test suite with coverage
./scripts/run_tests.sh all

# Check coverage threshold (≥ 70%)
open htmlcov/index.html
```

### Daily Development
```bash
# Unit tests (fast iteration)
./scripts/run_tests.sh unit

# Integration tests
./scripts/run_tests.sh integration

# Specific test file
pytest tests/unit/test_numerology_service.py -v
```

### Performance Validation
```bash
# Run benchmarks
./scripts/run_benchmarks.sh

# Compare with baseline
./scripts/run_benchmarks.sh --compare

# Quick load test
./scripts/run_load_tests.sh smoke
```

### Before Major Release
```bash
# Full test suite
./scripts/run_tests.sh all

# Performance benchmarks with save
./scripts/run_benchmarks.sh --save "v1.0-baseline"

# Load test (stress)
./scripts/run_load_tests.sh stress

# Security scan
./scripts/run_tests.sh security
```

---

## Test Markers

```bash
# Run by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m performance   # Performance tests only
pytest -m regression    # Regression tests only
pytest -m "not slow"    # Skip slow tests

# Multiple markers
pytest -m "unit and not slow"
```

---

## Direct pytest Commands

```bash
# Basic
pytest tests/ -v                              # All tests, verbose
pytest tests/unit/ -v                         # Unit tests only
pytest tests/integration/ -v                  # Integration tests only

# Specific tests
pytest tests/unit/test_numerology_service.py::TestWesternNumerology -v
pytest tests/unit/test_numerology_service.py::TestWesternNumerology::test_calculate_life_path -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Parallel execution (requires pytest-xdist)
pytest -n auto

# Very verbose with stdout
pytest -vv -s

# Generate reports
pytest --junit-xml=test-results.xml
pytest --html=report.html --self-contained-html
```

---

## Coverage Commands

```bash
# Generate coverage report
./scripts/run_tests.sh coverage

# View HTML report
open htmlcov/index.html          # Mac
xdg-open htmlcov/index.html      # Linux
start htmlcov/index.html         # Windows

# Terminal report with missing lines
pytest --cov=app --cov-report=term-missing

# XML for CI/CD
pytest --cov=app --cov-report=xml

# Check specific module
pytest --cov=app.services.numerology_service --cov-report=term
```

---

## Benchmark Commands

```bash
# Run benchmarks
./scripts/run_benchmarks.sh

# Compare with previous (fail if > 10% slower)
./scripts/run_benchmarks.sh --compare

# Save with name for later comparison
./scripts/run_benchmarks.sh --save "baseline-v1.0"

# List saved benchmarks
./scripts/run_benchmarks.sh --list

# Generate histogram
./scripts/run_benchmarks.sh --histogram

# Run all performance tests
./scripts/run_benchmarks.sh --all
```

---

## Load Test Commands

```bash
# Quick smoke test (10 users, 30s)
./scripts/run_load_tests.sh smoke

# Headless with defaults (50 users, 60s)
./scripts/run_load_tests.sh headless

# Custom parameters
USERS=100 SPAWN_RATE=20 RUN_TIME=120s ./scripts/run_load_tests.sh headless

# Interactive web UI
./scripts/run_load_tests.sh web
# Open http://localhost:8089

# Stress test (200 users, 5 min)
./scripts/run_load_tests.sh stress

# Distributed mode
./scripts/run_load_tests.sh distributed --master
./scripts/run_load_tests.sh distributed --worker
```

---

## Pre-commit Hooks

```bash
# Install
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run pytest-smoke --all-files

# Skip hooks (use sparingly)
git commit -n -m "message"                    # Skip all
SKIP=pytest-smoke git commit -m "message"     # Skip specific
```

---

## CI/CD Workflow

### Test Suite Workflow (`.github/workflows/test-suite.yml`)

**Triggers**:
- Push to `main`, `develop`, `feature/*`
- Pull requests
- Manual dispatch
- Daily at 2 AM UTC

**Jobs**:
1. Backend tests (unit, integration, performance)
2. Frontend tests (lint, unit, build)
3. E2E tests (Playwright)
4. Security scan (Trivy, Bandit)

**Required Checks**:
- ✅ All tests pass
- ✅ Coverage ≥ 70%
- ✅ No high/critical vulnerabilities

### Pre-commit Check Workflow (`.github/workflows/pre-commit-check.yml`)

**Triggers**: Pull requests

**Checks**:
- Python formatting (Black)
- Python linting (Flake8)
- TypeScript compilation
- Smoke tests

---

## Performance Thresholds

### Response Times
| Operation | Target | Maximum |
|-----------|--------|---------|
| Numerology calculation | < 10ms | < 100ms |
| Yoga detection | < 50ms | < 200ms |
| Chart generation | < 500ms | < 2s |
| API endpoint | < 200ms | < 1s |

### Load Test Targets
| Scenario | Users | RPS | p95 Response |
|----------|-------|-----|--------------|
| Smoke | 10 | 5 | < 200ms |
| Normal | 50 | 25 | < 500ms |
| Peak | 100 | 50 | < 1s |
| Stress | 200 | 75 | < 2s |

### Coverage Targets
- **Overall**: 70% (enforced)
- **Critical Services**: 80%
- **API Endpoints**: 70%

---

## Writing Tests

### Basic Test Structure
```python
import pytest
from datetime import date

@pytest.mark.unit
def test_calculate_life_path(self):
    # Arrange
    western = WesternNumerology()
    birth_date = date(1990, 1, 15)

    # Act
    result = western.calculate_life_path(birth_date)

    # Assert
    assert result == 8
```

### Async Test
```python
@pytest.mark.asyncio
async def test_async_endpoint(self, async_client, auth_headers):
    response = await async_client.post(
        "/api/v1/endpoint",
        json={"key": "value"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

### Parameterized Test
```python
@pytest.mark.parametrize("birth_date,expected", [
    (date(1990, 1, 15), 8),
    (date(1985, 5, 20), 3),
    (date(1992, 11, 3), 8),
])
def test_life_path_multiple(self, birth_date, expected):
    western = WesternNumerology()
    result = western.calculate_life_path(birth_date)
    assert result == expected
```

### Benchmark Test
```python
@pytest.mark.benchmark
def test_performance(self, benchmark, numerology_service):
    result = benchmark(
        numerology_service.calculate,
        "John Doe",
        date(1990, 1, 15),
        "both"
    )
    assert "western" in result
```

### Using Fixtures
```python
@pytest.fixture
def sample_data():
    return {"name": "Test", "date": date(1990, 1, 15)}

def test_with_fixture(self, sample_data):
    result = process(sample_data)
    assert result is not None
```

---

## Troubleshooting

### Import Errors
```bash
cd backend
source venv/bin/activate
pip install -e .
```

### Coverage Not Updating
```bash
rm .coverage
rm -rf htmlcov/
./scripts/run_tests.sh coverage
```

### Benchmark Data Issues
```bash
rm -rf .benchmarks/
./scripts/run_benchmarks.sh
```

### Debug Mode
```bash
pytest --pdb              # Drop into debugger
pytest --pdb -x           # Debug on first failure
pytest -s                 # Show stdout
pytest -vv                # Very verbose
pytest --tb=long          # Full traceback
```

---

## Test File Locations

```
backend/
├── tests/
│   ├── conftest.py                          # Shared fixtures
│   ├── unit/
│   │   └── test_numerology_service.py       # Unit tests
│   ├── integration/
│   │   └── test_enhancement_apis.py         # API tests
│   └── performance/
│       ├── test_benchmarks.py               # Pytest benchmarks
│       └── locustfile.py                    # Load tests
├── scripts/
│   ├── run_tests.sh                         # Master test runner
│   ├── run_benchmarks.sh                    # Benchmark runner
│   ├── run_load_tests.sh                    # Load test runner
│   └── run_smoke_tests.sh                   # Smoke test runner
└── pytest.ini                                # Pytest config
```

---

## Environment Variables

```bash
# Load test host
export LOAD_TEST_HOST=http://localhost:8000

# Custom users/spawn rate
export USERS=100
export SPAWN_RATE=20
export RUN_TIME=120s

# Test database (optional)
export TEST_DATABASE_URL=postgresql+asyncpg://...

# Disable coverage in local dev
export COVERAGE_DISABLE=true
```

---

## Useful Links

- [Full Testing Documentation](./TESTING.md)
- [pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)
- [pre-commit Documentation](https://pre-commit.com/)
- [Codecov Dashboard](https://codecov.io/gh/[org]/jioastro)

---

## Daily Workflow

### Morning (Start of Dev Session)
```bash
# Pull latest changes
git pull origin develop

# Run smoke tests
./scripts/run_smoke_tests.sh
```

### During Development
```bash
# After each change
pytest tests/unit/test_[module].py -v

# Before commit
pre-commit run --all-files
```

### Before Push
```bash
# Run relevant tests
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration

# Check coverage
./scripts/run_tests.sh coverage
```

### Before Pull Request
```bash
# Full test suite
./scripts/run_tests.sh all

# Performance benchmarks
./scripts/run_benchmarks.sh --compare

# Load test
./scripts/run_load_tests.sh smoke
```

---

**Quick Help**: For detailed information, see [TESTING.md](./TESTING.md)

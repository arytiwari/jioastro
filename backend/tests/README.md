# JioAstro Test Suite

Comprehensive testing infrastructure for the JioAstro backend, ensuring code quality, functionality, and performance.

---

## Quick Start

```bash
# Install dependencies
pip install pytest pytest-asyncio pytest-cov pytest-benchmark pytest-mock locust

# Run all tests
cd backend
./scripts/run_tests.sh all

# Run smoke tests (< 30s)
./scripts/run_smoke_tests.sh

# Run performance benchmarks
./scripts/run_benchmarks.sh

# Run load tests
./scripts/run_load_tests.sh smoke
```

---

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and utilities
├── unit/                          # Unit tests (isolated components)
│   ├── __init__.py
│   └── test_numerology_service.py # Numerology calculations
├── integration/                   # Integration tests (API endpoints)
│   ├── __init__.py
│   └── test_enhancement_apis.py   # Phase 4 API endpoints
└── performance/                   # Performance and load tests
    ├── __init__.py
    ├── test_benchmarks.py         # pytest-benchmark tests
    └── locustfile.py              # Locust load tests
```

---

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **Marker**: `@pytest.mark.unit`
- **Coverage Target**: 80%
- **Run Time**: < 1 minute

**Example**:
```python
@pytest.mark.unit
def test_calculate_life_path(self):
    western = WesternNumerology()
    result = western.calculate_life_path(date(1990, 1, 15))
    assert result == 8
```

**Run**:
```bash
./scripts/run_tests.sh unit
# or
pytest tests/unit/ -m unit -v
```

### Integration Tests (`tests/integration/`)
- **Purpose**: Test API endpoints and service interactions
- **Marker**: `@pytest.mark.integration`
- **Coverage Target**: 70%
- **Run Time**: 1-2 minutes

**Example**:
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_yogas_success(self, async_client, auth_headers):
    response = await async_client.post(
        "/api/v1/enhancements/yogas/analyze",
        json={"profile_id": "test-profile-123"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

**Run**:
```bash
./scripts/run_tests.sh integration
# or
pytest tests/integration/ -m integration -v
```

### Performance Tests (`tests/performance/`)

#### Benchmarks (`test_benchmarks.py`)
- **Purpose**: Measure execution time and track regressions
- **Marker**: `@pytest.mark.benchmark`
- **Tool**: pytest-benchmark

**Example**:
```python
@pytest.mark.benchmark
def test_single_calculation(self, benchmark, numerology_service):
    result = benchmark(
        numerology_service.calculate,
        "John Doe",
        date(1990, 1, 15),
        "both"
    )
```

**Run**:
```bash
./scripts/run_benchmarks.sh
# Compare with previous
./scripts/run_benchmarks.sh --compare
```

#### Load Tests (`locustfile.py`)
- **Purpose**: Simulate real user traffic patterns
- **Tool**: Locust

**Example**:
```python
class JioAstroUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def calculate_numerology(self):
        self.client.post("/api/v1/numerology/calculate", json={...})
```

**Run**:
```bash
# Quick smoke test
./scripts/run_load_tests.sh smoke

# Interactive web UI
./scripts/run_load_tests.sh web
# Open http://localhost:8089

# Stress test
./scripts/run_load_tests.sh stress
```

---

## Shared Fixtures (`conftest.py`)

### Available Fixtures

#### Test Data
- `sample_birth_data`: Birth profile data
- `sample_chart_data`: Planetary positions and houses
- `sample_profile_data`: Complete profile object
- `sample_planets`: Planetary positions for yoga detection

#### Mock Services
- `mock_supabase_service`: Mocked Supabase client
- `mock_openai_service`: Mocked OpenAI client
- `auth_headers`: JWT authentication headers

#### Utilities
- `performance_threshold`: Performance target thresholds
- `async_client`: FastAPI async test client

**Usage Example**:
```python
def test_with_fixtures(self, sample_chart_data, mock_supabase_service):
    # Use fixtures directly
    yogas = detect_yogas(sample_chart_data["planets"])
    assert len(yogas) > 0
```

---

## Running Tests

### Test Runner Scripts (`../scripts/`)

#### `run_tests.sh` - Master Test Runner
```bash
./scripts/run_tests.sh [type]

# Types:
#   all          - All tests with coverage (default)
#   unit         - Unit tests only
#   integration  - Integration tests only
#   performance  - Performance tests only
#   smoke        - Quick smoke tests
#   regression   - Regression tests only
#   security     - Security scans
#   coverage     - Generate coverage report
```

#### `run_benchmarks.sh` - Performance Benchmarks
```bash
./scripts/run_benchmarks.sh [option]

# Options:
#   --only       - Run benchmarks (default)
#   --compare    - Compare with previous results
#   --save NAME  - Save results with name
#   --all        - Run all performance tests
#   --histogram  - Generate histogram
#   --list       - List saved benchmarks
```

#### `run_load_tests.sh` - Load Testing
```bash
./scripts/run_load_tests.sh [mode]

# Modes:
#   headless     - No UI (default)
#   web          - Web UI at :8089
#   distributed  - Master/worker mode
#   smoke        - Quick test (10 users, 30s)
#   stress       - Stress test (200 users, 5 min)
```

#### `run_smoke_tests.sh` - Quick Validation
```bash
./scripts/run_smoke_tests.sh

# Runs critical path tests in < 30s
# Perfect for pre-commit checks
```

### Direct pytest Commands

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/unit/test_numerology_service.py -v

# Specific class
pytest tests/unit/test_numerology_service.py::TestWesternNumerology -v

# Specific test
pytest tests/unit/test_numerology_service.py::TestWesternNumerology::test_calculate_life_path -v

# By marker
pytest -m unit -v
pytest -m integration -v
pytest -m performance -v

# Stop on first failure
pytest -x

# Parallel execution (requires pytest-xdist)
pytest -n auto

# With coverage
pytest --cov=app --cov-report=html
```

---

## Configuration

### `pytest.ini`
Located in `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
addopts =
    -v -ra -l --strict-markers
    --cov=app --cov-report=html --cov-report=term-missing
    --cov-fail-under=70
    --asyncio-mode=auto

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    regression: Regression tests
    slow: Tests > 1 second
    smoke: Quick smoke tests
    security: Security tests
    database: Tests requiring database
    external: Tests requiring external services
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit              # Unit test
@pytest.mark.integration       # Integration test
@pytest.mark.performance       # Performance test
@pytest.mark.regression        # Regression test
@pytest.mark.slow              # Slow test (> 1s)
@pytest.mark.smoke             # Smoke test
@pytest.mark.database          # Requires database
@pytest.mark.external          # Requires external service
```

---

## Coverage

### Targets
- **Overall Coverage**: 70% (enforced)
- **Critical Services**: 80%
- **API Endpoints**: 70%
- **Utility Functions**: 60%

### View Coverage

```bash
# Generate HTML report
./scripts/run_tests.sh coverage

# Open report
open htmlcov/index.html          # Mac
xdg-open htmlcov/index.html      # Linux
start htmlcov/index.html         # Windows
```

### Coverage Reports

- **HTML**: `backend/htmlcov/index.html` (interactive)
- **Terminal**: Shown after test run
- **XML**: `backend/coverage.xml` (for CI/CD)

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

**Thresholds defined in**: `tests/conftest.py`

```python
@pytest.fixture
def performance_threshold():
    return {
        "fast": 0.1,       # 100ms
        "moderate": 0.5,   # 500ms
        "slow": 2.0        # 2 seconds
    }
```

---

## CI/CD Integration

### GitHub Actions Workflows

#### Test Suite (`.github/workflows/test-suite.yml`)
**Triggers**: Push, PR, Manual, Daily @ 2 AM UTC

**Jobs**:
1. Backend tests (unit, integration, performance)
2. Frontend tests (lint, unit, build)
3. E2E tests (Playwright)
4. Security scan (Trivy, Bandit)

**Required**:
- ✅ All tests pass
- ✅ Coverage ≥ 70%
- ✅ No high/critical vulnerabilities

#### Pre-commit Check (`.github/workflows/pre-commit-check.yml`)
**Triggers**: Pull requests

**Fast checks** (< 2 min):
- Python formatting (Black)
- Python linting (Flake8)
- TypeScript compilation
- Smoke tests

### Codecov Integration

Coverage automatically uploaded to Codecov on CI runs.

View at: `https://codecov.io/gh/[org]/jioastro`

---

## Pre-commit Hooks

### Installation

```bash
pip install pre-commit
pre-commit install
```

### Configuration

Located in `backend/.pre-commit-config.yaml`:

**Hooks**:
- Trailing whitespace fixer
- End-of-file fixer
- Black (Python formatter)
- Flake8 (Python linter)
- isort (import sorting)
- pytest smoke tests
- ESLint (TypeScript)
- Bandit (security)
- detect-secrets

### Run Manually

```bash
# All hooks
pre-commit run --all-files

# Specific hook
pre-commit run black --all-files
pre-commit run pytest-smoke --all-files
```

---

## Writing New Tests

### Test Template

```python
import pytest
from datetime import date

class TestMyFeature:
    """Test suite for my feature"""

    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result is not None

    @pytest.mark.unit
    @pytest.mark.parametrize("input,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_with_parameters(self, input, expected):
        """Test with multiple parameters"""
        result = my_function(input)
        assert result == expected

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_async_endpoint(self, async_client, auth_headers):
        """Test async API endpoint"""
        response = await async_client.post(
            "/api/v1/endpoint",
            json={"key": "value"},
            headers=auth_headers
        )
        assert response.status_code == 200

    @pytest.mark.benchmark
    def test_performance(self, benchmark):
        """Test performance with benchmark"""
        result = benchmark(my_function, "input")
        assert result is not None
```

### Best Practices

1. **Use descriptive test names**: `test_calculate_life_path_with_master_number`
2. **Follow Arrange-Act-Assert pattern**
3. **One assertion per test** (when possible)
4. **Use fixtures for setup**
5. **Mock external dependencies**
6. **Test edge cases** (empty, invalid, boundary)
7. **Keep tests fast** (< 10ms for unit tests)
8. **Ensure test isolation** (no shared state)

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
```

---

## Documentation

- **Comprehensive Guide**: [TESTING.md](../docs/TESTING.md)
- **Quick Reference**: [TESTING_QUICK_REFERENCE.md](../docs/TESTING_QUICK_REFERENCE.md)
- **This README**: Overview and quick start

---

## Support

For questions or issues:
1. Check documentation files
2. Review test examples in this directory
3. Check CI/CD logs in GitHub Actions
4. Contact the development team

---

**Test Suite Version**: 1.0
**Last Updated**: 2025-11-06
**Coverage Target**: 70%
**Total Test Files**: 3
**Total Test Cases**: 50+

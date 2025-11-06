# JioAstro Testing Guide

This document provides comprehensive information about the JioAstro testing infrastructure, including how to run tests, interpret results, and maintain test quality.

## Table of Contents

- [Overview](#overview)
- [Test Infrastructure](#test-infrastructure)
- [Quick Start](#quick-start)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Coverage Requirements](#coverage-requirements)
- [Performance Testing](#performance-testing)
- [Load Testing](#load-testing)
- [CI/CD Integration](#cicd-integration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)

---

## Overview

JioAstro uses a comprehensive testing strategy to ensure code quality, functionality, and performance:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and service interactions
- **Performance Tests**: Validate speed and efficiency
- **Regression Tests**: Ensure no functionality breaks
- **Load Tests**: Simulate production traffic patterns
- **Security Tests**: Scan for vulnerabilities

### Test Statistics

- **Total Coverage Target**: 70%
- **Critical Path Coverage**: 90%+
- **Test Execution Time**: < 5 minutes (full suite)
- **Smoke Tests**: < 30 seconds

---

## Test Infrastructure

### Directory Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures and utilities
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   └── test_numerology_service.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   └── test_enhancement_apis.py
│   └── performance/             # Performance tests
│       ├── __init__.py
│       ├── test_benchmarks.py   # pytest-benchmark tests
│       └── locustfile.py        # Locust load tests
├── scripts/
│   ├── run_tests.sh             # Master test runner
│   ├── run_benchmarks.sh        # Performance benchmarks
│   ├── run_load_tests.sh        # Load testing
│   └── run_smoke_tests.sh       # Quick smoke tests
├── pytest.ini                    # Pytest configuration
└── .coverage                     # Coverage data (generated)
```

### Key Technologies

- **pytest**: Test framework with async support
- **pytest-cov**: Code coverage reporting
- **pytest-asyncio**: Async test support
- **pytest-benchmark**: Performance benchmarking
- **pytest-mock**: Mocking utilities
- **Locust**: Load testing framework
- **GitHub Actions**: CI/CD automation

---

## Quick Start

### Setup

1. **Activate virtual environment**:
   ```bash
   cd backend
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install test dependencies**:
   ```bash
   pip install pytest pytest-asyncio pytest-cov pytest-benchmark pytest-mock
   pip install locust  # For load testing
   ```

3. **Run all tests**:
   ```bash
   ./scripts/run_tests.sh all
   ```

### Quick Commands

```bash
# Smoke tests (< 30s)
./scripts/run_smoke_tests.sh

# Unit tests only
./scripts/run_tests.sh unit

# Integration tests only
./scripts/run_tests.sh integration

# Performance benchmarks
./scripts/run_benchmarks.sh

# Load tests
./scripts/run_load_tests.sh smoke
```

---

## Test Categories

### 1. Unit Tests

**Location**: `tests/unit/`

**Purpose**: Test individual functions and classes in isolation

**Markers**: `@pytest.mark.unit`

**Example**:
```python
@pytest.mark.unit
def test_calculate_life_path(self):
    western = WesternNumerology()
    result = western.calculate_life_path(date(1990, 1, 15))
    assert result == 8
```

**Coverage Target**: 80%

### 2. Integration Tests

**Location**: `tests/integration/`

**Purpose**: Test API endpoints and service interactions

**Markers**: `@pytest.mark.integration`

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

**Coverage Target**: 70%

### 3. Performance Tests

**Location**: `tests/performance/`

**Purpose**: Validate speed and efficiency

**Markers**: `@pytest.mark.performance`, `@pytest.mark.benchmark`

**Example**:
```python
@pytest.mark.performance
@pytest.mark.benchmark
def test_single_calculation(self, benchmark, numerology_service):
    result = benchmark(
        numerology_service.calculate,
        "John Doe",
        date(1990, 1, 15),
        "both"
    )
    assert "western" in result
```

**Performance Thresholds**:
- **Fast**: < 100ms (0.1s)
- **Moderate**: < 500ms (0.5s)
- **Slow**: < 2s
- **Throughput**: > 10 operations/second

### 4. Regression Tests

**Purpose**: Ensure no functionality breaks between releases

**Markers**: `@pytest.mark.regression`

**Example**:
```python
@pytest.mark.regression
def test_numerology_speed_threshold(self, numerology_service, performance_threshold):
    start = time.time()
    result = numerology_service.calculate("John Doe", date(1990, 1, 15), "both")
    duration = time.time() - start

    assert duration < performance_threshold["fast"]
```

### 5. Security Tests

**Tools**: Bandit, Safety

**Purpose**: Scan for vulnerabilities and security issues

**Run**:
```bash
./scripts/run_tests.sh security
```

---

## Running Tests

### Master Test Runner

The `run_tests.sh` script provides a unified interface for all test types:

```bash
./scripts/run_tests.sh [test-type]
```

**Test Types**:

| Type | Description | Run Time |
|------|-------------|----------|
| `all` | All tests with coverage (default) | 3-5 min |
| `unit` | Unit tests only | 30-60s |
| `integration` | Integration tests only | 1-2 min |
| `performance` | Performance tests only | 1-2 min |
| `smoke` | Quick smoke tests | < 30s |
| `regression` | Regression tests only | 1-2 min |
| `security` | Security scans | 1-2 min |
| `coverage` | Generate coverage report | 2-3 min |

### Examples

```bash
# Run all tests with coverage report
./scripts/run_tests.sh all

# Quick smoke tests before commit
./scripts/run_smoke_tests.sh

# Unit tests only
./scripts/run_tests.sh unit

# Generate coverage report
./scripts/run_tests.sh coverage
```

### Direct pytest Commands

You can also run pytest directly with custom options:

```bash
# Run specific test file
pytest tests/unit/test_numerology_service.py -v

# Run specific test class
pytest tests/unit/test_numerology_service.py::TestWesternNumerology -v

# Run specific test method
pytest tests/unit/test_numerology_service.py::TestWesternNumerology::test_calculate_life_path -v

# Run tests with specific marker
pytest -m unit -v
pytest -m integration -v
pytest -m performance -v

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests with verbose output
pytest -vv

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

---

## Coverage Requirements

### Coverage Thresholds

- **Overall Coverage**: 70% (enforced in pytest.ini)
- **Critical Services**: 80%
- **API Endpoints**: 70%
- **Utility Functions**: 60%

### Viewing Coverage Reports

#### Terminal Report
```bash
./scripts/run_tests.sh coverage
```

Output shows:
- Files with coverage percentage
- Missing lines
- Overall coverage

#### HTML Report
```bash
./scripts/run_tests.sh coverage
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

Features:
- Interactive file browser
- Line-by-line coverage visualization
- Branch coverage analysis

#### XML Report (for CI/CD)
```bash
pytest --cov=app --cov-report=xml
```

Generated as `coverage.xml` (used by Codecov, SonarQube, etc.)

### Coverage Configuration

Located in `pytest.ini`:

```ini
[pytest]
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

---

## Performance Testing

### Benchmarking with pytest-benchmark

**Purpose**: Measure execution time and compare across runs

**Runner Script**:
```bash
./scripts/run_benchmarks.sh [option]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--only` | Run only benchmarks (default) |
| `--compare` | Compare with previous results |
| `--save NAME` | Save results with name |
| `--all` | Run all performance tests |
| `--histogram` | Generate histogram |
| `--list` | List saved benchmarks |

**Examples**:

```bash
# Run benchmarks
./scripts/run_benchmarks.sh

# Compare with previous run (fail if > 10% slower)
./scripts/run_benchmarks.sh --compare

# Save benchmark for later comparison
./scripts/run_benchmarks.sh --save baseline-v1.0

# Generate histogram from saved results
./scripts/run_benchmarks.sh --histogram

# List all saved benchmarks
./scripts/run_benchmarks.sh --list
```

### Benchmark Output

```
------------------------- benchmark: 4 tests -------------------------
Name (time in us)                        Min        Max       Mean
----------------------------------------------------------------------
test_single_calculation               10.50      50.20      12.30
test_bulk_calculations               127.40     180.50     145.20
test_yoga_detection                   25.30      75.10      30.40
test_yoga_detection_bulk             250.80     320.40     275.60
----------------------------------------------------------------------
```

### Performance Thresholds

Defined in `tests/conftest.py`:

```python
@pytest.fixture
def performance_threshold():
    return {
        "fast": 0.1,      # 100ms
        "moderate": 0.5,   # 500ms
        "slow": 2.0        # 2 seconds
    }
```

### Writing Benchmark Tests

```python
@pytest.mark.benchmark
def test_single_calculation(self, benchmark, numerology_service):
    """Benchmark single numerology calculation"""
    result = benchmark(
        numerology_service.calculate,
        "John Doe",
        date(1990, 1, 15),
        "both"
    )
    assert "western" in result
```

---

## Load Testing

### Overview

JioAstro uses **Locust** for load testing to simulate real user traffic patterns.

### Load Test Runner

```bash
./scripts/run_load_tests.sh [mode] [options]
```

**Modes**:

| Mode | Description | Use Case |
|------|-------------|----------|
| `headless` | Run without UI (default) | CI/CD, automated testing |
| `web` | Run with web UI | Interactive load testing |
| `distributed` | Distributed mode | High-load scenarios |
| `smoke` | Quick smoke test (10 users, 30s) | Quick validation |
| `stress` | Stress test (200 users, 5 min) | Capacity planning |

### Examples

#### 1. Quick Smoke Test
```bash
./scripts/run_load_tests.sh smoke
```

Runs 10 concurrent users for 30 seconds.

#### 2. Headless Load Test
```bash
# Default: 50 users, spawn rate 10/s, 60s duration
./scripts/run_load_tests.sh headless

# Custom parameters
USERS=100 SPAWN_RATE=20 RUN_TIME=120s ./scripts/run_load_tests.sh headless
```

#### 3. Interactive Web UI
```bash
./scripts/run_load_tests.sh web
```

Open http://localhost:8089 in browser to:
- Set user count and spawn rate
- Start/stop tests
- View real-time metrics
- Download reports

#### 4. Stress Test
```bash
./scripts/run_load_tests.sh stress
```

Runs 200 concurrent users for 5 minutes.

#### 5. Distributed Load Testing

**Start Master**:
```bash
./scripts/run_load_tests.sh distributed --master
```

**Start Workers** (on same or different machines):
```bash
./scripts/run_load_tests.sh distributed --worker

# Remote worker
MASTER_HOST=192.168.1.100 ./scripts/run_load_tests.sh distributed --worker
```

### Load Test Configuration

Located in `tests/performance/locustfile.py`:

```python
class JioAstroUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3s between tasks

    @task(5)  # Weight: 5 (most frequent)
    def calculate_numerology(self):
        # ...

    @task(3)  # Weight: 3
    def analyze_yogas(self):
        # ...
```

**Task Weights**:
- Numerology calculation: 5 (most common)
- Yoga analysis: 3
- Remedy generation: 2
- Transit calculation: 2
- Shadbala calculation: 1
- Health check: 1

### Interpreting Load Test Results

#### HTML Report

Generated at: `backend/test-results/load-tests/results_TIMESTAMP.html`

**Key Metrics**:
- **RPS (Requests Per Second)**: Throughput
- **Response Time**: p50, p95, p99 percentiles
- **Failure Rate**: % of failed requests
- **Total Requests**: Volume handled

**Good Targets**:
- RPS: > 50 for standard load, > 100 for stress
- p95 Response Time: < 500ms
- p99 Response Time: < 1000ms
- Failure Rate: < 1%

#### CSV Reports

- `results_TIMESTAMP_stats.csv`: Aggregated statistics
- `results_TIMESTAMP_stats_history.csv`: Time-series data

---

## CI/CD Integration

### GitHub Actions Workflows

#### 1. Test Suite Workflow

**File**: `.github/workflows/test-suite.yml`

**Triggers**:
- Push to `main`, `develop`, or `feature/*` branches
- Pull requests to `main` or `develop`
- Manual dispatch
- Daily at 2 AM UTC

**Jobs**:

1. **Backend Tests**
   - Unit tests with coverage
   - Integration tests
   - Performance tests
   - Upload to Codecov

2. **Frontend Tests**
   - ESLint
   - Unit tests with coverage
   - Build test

3. **E2E Tests**
   - Playwright end-to-end tests

4. **Security Scan**
   - Trivy vulnerability scanner
   - Bandit security linter

**Status Checks**:
- ✅ All tests must pass
- ✅ Coverage must be ≥ 70%
- ✅ No high/critical vulnerabilities

#### 2. Pre-commit Check Workflow

**File**: `.github/workflows/pre-commit-check.yml`

**Triggers**: Pull requests

**Checks**:
- Python formatting (Black)
- Python linting (Flake8)
- TypeScript compilation
- Smoke tests

**Purpose**: Fast feedback loop (< 2 minutes)

### Codecov Integration

Coverage reports are automatically uploaded to Codecov:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    fail_ci_if_error: true
```

View coverage at: `https://codecov.io/gh/[org]/jioastro`

---

## Pre-commit Hooks

### Overview

Pre-commit hooks run automatically before each commit to ensure code quality.

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### Configuration

Located in `.pre-commit-config.yaml`:

**Hooks**:
1. **General File Checks**
   - Trailing whitespace
   - End-of-file fixer
   - Large files check
   - Private key detection

2. **Python**
   - Black (formatter)
   - Flake8 (linter)
   - isort (import sorting)
   - pytest smoke tests
   - Bandit (security)

3. **TypeScript/JavaScript**
   - ESLint

4. **Security**
   - detect-secrets

### Running Manually

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run pytest-smoke --all-files
```

### Skipping Hooks (Use Sparingly)

```bash
# Skip all hooks (not recommended)
git commit -n -m "commit message"

# Skip specific hook
SKIP=pytest-smoke git commit -m "commit message"
```

---

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_calculate_life_path(self):
    # Arrange: Setup test data
    western = WesternNumerology()
    birth_date = date(1990, 1, 15)

    # Act: Execute function
    result = western.calculate_life_path(birth_date)

    # Assert: Verify result
    assert result == 8
```

### Using Fixtures

**Define in conftest.py**:
```python
@pytest.fixture
def sample_chart_data():
    return {
        "planets": {...},
        "houses": {...}
    }
```

**Use in tests**:
```python
def test_yoga_detection(self, sample_chart_data):
    yogas = extended_yoga_service.detect_extended_yogas(
        sample_chart_data["planets"]
    )
    assert len(yogas) > 0
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_endpoint(self, async_client, auth_headers):
    response = await async_client.post(
        "/api/v1/endpoint",
        json={...},
        headers=auth_headers
    )
    assert response.status_code == 200
```

### Mocking

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock(self):
    with patch('app.services.supabase_service.get_profile') as mock_get:
        mock_get.return_value = {"id": "test-123", "name": "Test"}

        result = await some_function()

        assert result is not None
        mock_get.assert_called_once()
```

### Parameterized Tests

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

### Test Markers

```python
# Mark as unit test
@pytest.mark.unit

# Mark as integration test
@pytest.mark.integration

# Mark as slow test (skipped by default)
@pytest.mark.slow

# Mark as requiring database
@pytest.mark.database

# Mark as requiring external service
@pytest.mark.external

# Skip test conditionally
@pytest.mark.skipif(condition, reason="...")

# Expected to fail
@pytest.mark.xfail(reason="...")
```

### Best Practices

1. **Test Naming**: Use descriptive names
   - ✅ `test_calculate_life_path_with_master_number`
   - ❌ `test_1`

2. **One Assertion Per Test** (when possible)
   - Focus on single behavior
   - Makes failures easier to debug

3. **Use Fixtures for Setup**
   - DRY principle
   - Consistent test data

4. **Mock External Dependencies**
   - Database calls
   - API calls
   - OpenAI requests

5. **Test Edge Cases**
   - Empty inputs
   - Invalid inputs
   - Boundary conditions

6. **Keep Tests Fast**
   - Unit tests: < 10ms
   - Integration tests: < 100ms
   - Use `@pytest.mark.slow` for slow tests

7. **Test Isolation**
   - Each test should be independent
   - No shared state
   - Clean up after tests

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Install in development mode
pip install -e .
```

#### 2. Async Fixture Errors

**Error**: `ScopeMismatch: You tried to access the function scoped fixture event_loop with a session scoped request object`

**Solution**: Ensure `asyncio_mode=auto` in `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
```

#### 3. Coverage Not Updating

**Solution**:
```bash
# Remove old coverage data
rm .coverage
rm -rf htmlcov/

# Run tests again
./scripts/run_tests.sh coverage
```

#### 4. Benchmark Data Corruption

**Solution**:
```bash
# Remove old benchmark data
rm -rf .benchmarks/

# Run benchmarks again
./scripts/run_benchmarks.sh
```

#### 5. Tests Pass Locally but Fail in CI

**Common Causes**:
- Environment variable differences
- Database connection issues
- Timing issues (race conditions)

**Solution**:
```bash
# Check CI logs for specific error
# Ensure environment variables match
# Use fixtures for consistent test data
# Add timeout to prevent hanging
@pytest.mark.timeout(10)
```

### Debug Mode

```bash
# Run with Python debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb -x

# Print stdout/stderr
pytest -s

# Very verbose
pytest -vv
```

### Viewing Test Logs

```bash
# Show print statements
pytest -s

# Show full traceback
pytest --tb=long

# Show only failed tests
pytest -ra

# Generate JUnit XML report
pytest --junit-xml=test-results.xml
```

---

## Performance Targets

### Response Time Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| Numerology calculation | < 10ms | < 100ms |
| Yoga detection | < 50ms | < 200ms |
| Chart generation | < 500ms | < 2s |
| API endpoint | < 200ms | < 1s |

### Throughput Targets

| Endpoint | Minimum RPS | Optimal RPS |
|----------|-------------|-------------|
| /numerology/calculate | 10 | 50 |
| /yogas/analyze | 5 | 20 |
| /remedies/generate | 5 | 20 |
| /health | 100 | 500 |

### Load Test Targets

| Scenario | Users | Duration | Target RPS | Target p95 |
|----------|-------|----------|------------|------------|
| Smoke | 10 | 30s | 5 | < 200ms |
| Normal | 50 | 60s | 25 | < 500ms |
| Peak | 100 | 120s | 50 | < 1s |
| Stress | 200 | 300s | 75 | < 2s |

---

## Continuous Improvement

### Monthly Test Review

- Review coverage reports
- Identify untested code paths
- Add tests for bug fixes
- Update performance baselines

### Quarterly Performance Audit

- Run load tests
- Compare with baselines
- Identify bottlenecks
- Optimize slow paths

### Annual Test Suite Refactor

- Remove redundant tests
- Update fixtures
- Improve test clarity
- Update documentation

---

## Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
- [Locust Documentation](https://docs.locust.io/)
- [pre-commit Documentation](https://pre-commit.com/)

### Internal Links

- [Architecture Documentation](../JIOASTRO_ARCHITECTURE_DOCUMENTATION.md)
- [API Documentation](./api/)
- [Numerology Documentation](./numerology/)

### Tools

- [Codecov Dashboard](https://codecov.io/gh/[org]/jioastro)
- [GitHub Actions](https://github.com/[org]/jioastro/actions)

---

## Support

For questions or issues:

1. Check this documentation
2. Review test examples in `tests/`
3. Check CI/CD logs in GitHub Actions
4. Contact the development team

---

**Last Updated**: 2025-11-06
**Version**: 1.0
**Maintainer**: JioAstro Development Team

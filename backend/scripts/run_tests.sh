#!/bin/bash
# ============================================================================
# Master Test Runner Script
# ============================================================================
# Usage:
#   ./scripts/run_tests.sh [test-type]
#
# Test Types:
#   all         - Run all tests (default)
#   unit        - Unit tests only
#   integration - Integration tests only
#   performance - Performance tests only
#   smoke       - Quick smoke tests
#   coverage    - Generate coverage report
#   regression  - Regression tests only
#   security    - Security tests only
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COVERAGE_THRESHOLD=70
TEST_DIR="tests"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Helper Functions
print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if virtual environment is activated
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not activated. Activating..."
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
            print_success "Virtual environment activated"
        else
            print_error "Virtual environment not found. Run: python -m venv venv"
            exit 1
        fi
    fi
}

# Install dependencies
install_deps() {
    print_header "Installing Test Dependencies"
    pip install -q pytest pytest-asyncio pytest-cov pytest-benchmark pytest-mock pytest-timeout
    print_success "Dependencies installed"
}

# Run unit tests
run_unit_tests() {
    print_header "Running Unit Tests"
    pytest tests/unit/ -m unit -v --tb=short
    print_success "Unit tests completed"
}

# Run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"
    pytest tests/integration/ -m integration -v --tb=short
    print_success "Integration tests completed"
}

# Run performance tests
run_performance_tests() {
    print_header "Running Performance Tests"
    pytest tests/performance/test_benchmarks.py -m performance -v --tb=short
    print_success "Performance tests completed"
}

# Run smoke tests (fast subset)
run_smoke_tests() {
    print_header "Running Smoke Tests"
    pytest tests/unit/test_numerology_service.py::TestNumerologyService::test_full_calculation_both_systems -v
    pytest tests/integration/test_enhancement_apis.py::TestRemedyAPI::test_generate_remedies_success -v
    print_success "Smoke tests completed"
}

# Run regression tests
run_regression_tests() {
    print_header "Running Regression Tests"
    pytest tests/ -m regression -v --tb=short
    print_success "Regression tests completed"
}

# Run security tests
run_security_tests() {
    print_header "Running Security Tests"

    # Bandit security linter
    if command -v bandit &> /dev/null; then
        print_header "Running Bandit Security Scan"
        bandit -r app/ -ll || print_warning "Bandit found security issues"
    else
        print_warning "Bandit not installed. Run: pip install bandit"
    fi

    # Safety check for vulnerabilities in dependencies
    if command -v safety &> /dev/null; then
        print_header "Checking Dependencies for Vulnerabilities"
        safety check || print_warning "Safety found vulnerable dependencies"
    else
        print_warning "Safety not installed. Run: pip install safety"
    fi

    print_success "Security tests completed"
}

# Run all tests with coverage
run_all_tests() {
    print_header "Running Full Test Suite"
    pytest tests/ \
        -v \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-report=xml \
        --cov-fail-under=$COVERAGE_THRESHOLD \
        --tb=short

    print_success "All tests completed"
    echo -e "\n${GREEN}Coverage report generated at: htmlcov/index.html${NC}"
}

# Generate coverage report only
run_coverage() {
    print_header "Generating Coverage Report"
    pytest tests/ \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-report=xml \
        --tb=short

    print_success "Coverage report generated"
    echo -e "\n${GREEN}Open: htmlcov/index.html${NC}"
}

# Main execution
main() {
    TEST_TYPE=${1:-all}

    print_header "JioAstro Test Suite"
    echo "Test Type: $TEST_TYPE"
    echo "Coverage Threshold: $COVERAGE_THRESHOLD%"

    check_venv
    install_deps

    case $TEST_TYPE in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        performance)
            run_performance_tests
            ;;
        smoke)
            run_smoke_tests
            ;;
        regression)
            run_regression_tests
            ;;
        security)
            run_security_tests
            ;;
        coverage)
            run_coverage
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            echo "Available options: all, unit, integration, performance, smoke, regression, security, coverage"
            exit 1
            ;;
    esac

    print_success "Test run completed successfully!"
}

# Run main
main "$@"

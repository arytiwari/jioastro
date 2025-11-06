#!/bin/bash
# ============================================================================
# Quick Smoke Tests Runner
# ============================================================================
# Purpose: Fast subset of tests for pre-commit hooks and quick validation
# Run time: < 30 seconds
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

print_header() {
    echo -e "\n${BLUE}$1${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Run smoke tests
print_header "🚀 Running Smoke Tests"

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    print_error "pytest not installed"
    exit 1
fi

# Run critical path tests only
pytest tests/unit/test_numerology_service.py::TestNumerologyService::test_full_calculation_both_systems \
       tests/unit/test_numerology_service.py::TestPerformanceRegression::test_numerology_speed_threshold \
       -v \
       -x \
       --tb=short \
       --no-header \
       --quiet

if [ $? -eq 0 ]; then
    print_success "All smoke tests passed!"
    exit 0
else
    print_error "Smoke tests failed!"
    exit 1
fi

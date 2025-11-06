#!/bin/bash
# ============================================================================
# Performance Benchmarks Runner
# ============================================================================
# Purpose: Run pytest-benchmark performance tests and compare results
# Usage:
#   ./scripts/run_benchmarks.sh [options]
#
# Options:
#   --compare     Compare with previous benchmark results
#   --save NAME   Save benchmark results with a specific name
#   --only        Run only benchmark tests (skip other performance tests)
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BENCHMARK_DIR="$PROJECT_ROOT/.benchmarks"

cd "$PROJECT_ROOT"

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

# Check dependencies
check_deps() {
    if ! command -v pytest &> /dev/null; then
        print_error "pytest not installed"
        exit 1
    fi

    # Install pytest-benchmark if not present
    python -c "import pytest_benchmark" 2>/dev/null || {
        print_warning "Installing pytest-benchmark..."
        pip install pytest-benchmark
    }

    print_success "Dependencies checked"
}

# Run benchmarks only
run_benchmarks_only() {
    print_header "Running Performance Benchmarks"

    pytest tests/performance/test_benchmarks.py \
        -m benchmark \
        -v \
        --benchmark-only \
        --benchmark-autosave \
        --benchmark-save-data

    print_success "Benchmarks completed"
}

# Run with comparison
run_with_compare() {
    print_header "Running Benchmarks with Comparison"

    if [[ ! -d "$BENCHMARK_DIR" ]]; then
        print_warning "No previous benchmarks found. Running first benchmark..."
        run_benchmarks_only
        return
    fi

    pytest tests/performance/test_benchmarks.py \
        -m benchmark \
        -v \
        --benchmark-only \
        --benchmark-autosave \
        --benchmark-compare \
        --benchmark-compare-fail=mean:10%

    if [ $? -eq 0 ]; then
        print_success "Benchmarks passed! No significant performance regression."
    else
        print_error "Performance regression detected!"
        print_warning "Review the comparison output above"
        exit 1
    fi
}

# Run with custom save name
run_with_save() {
    SAVE_NAME=$1
    print_header "Running Benchmarks (Saving as: $SAVE_NAME)"

    pytest tests/performance/test_benchmarks.py \
        -m benchmark \
        -v \
        --benchmark-only \
        --benchmark-autosave \
        --benchmark-save="$SAVE_NAME"

    print_success "Benchmarks saved as: $SAVE_NAME"
}

# Run all performance tests (including benchmarks)
run_all_performance() {
    print_header "Running All Performance Tests"

    pytest tests/performance/ \
        -m performance \
        -v \
        --benchmark-autosave \
        --benchmark-save-data

    print_success "All performance tests completed"
}

# Generate histogram
generate_histogram() {
    print_header "Generating Benchmark Histogram"

    if [[ ! -d "$BENCHMARK_DIR" ]]; then
        print_error "No benchmark data found"
        exit 1
    fi

    pytest-benchmark compare --histogram

    print_success "Histogram generated"
}

# List saved benchmarks
list_benchmarks() {
    print_header "Saved Benchmarks"

    if [[ ! -d "$BENCHMARK_DIR" ]]; then
        print_warning "No benchmarks found"
        return
    fi

    ls -lh "$BENCHMARK_DIR"
}

# Main execution
main() {
    print_header "JioAstro Performance Benchmarks"

    check_deps

    # Parse options
    case "$1" in
        --compare)
            run_with_compare
            ;;
        --save)
            if [[ -z "$2" ]]; then
                print_error "Please provide a name for the benchmark save"
                exit 1
            fi
            run_with_save "$2"
            ;;
        --only)
            run_benchmarks_only
            ;;
        --histogram)
            generate_histogram
            ;;
        --list)
            list_benchmarks
            ;;
        --all)
            run_all_performance
            ;;
        *)
            print_header "Usage"
            echo "  ./scripts/run_benchmarks.sh [option]"
            echo ""
            echo "Options:"
            echo "  --only          Run only benchmarks (default)"
            echo "  --compare       Compare with previous results"
            echo "  --save NAME     Save results with name"
            echo "  --all           Run all performance tests"
            echo "  --histogram     Generate histogram from saved results"
            echo "  --list          List saved benchmarks"
            echo ""

            # Default: run benchmarks only
            run_benchmarks_only
            ;;
    esac

    echo ""
    print_success "Benchmark run completed!"
    echo -e "\n${BLUE}Benchmark data saved in: $BENCHMARK_DIR${NC}"
}

main "$@"

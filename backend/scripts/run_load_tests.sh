#!/bin/bash
# ============================================================================
# Load Testing Script using Locust
# ============================================================================
# Usage:
#   ./scripts/run_load_tests.sh [mode] [options]
#
# Modes:
#   headless    - Run without UI (default)
#   web         - Run with web UI
#   distributed - Run in distributed mode (master/worker)
#
# Examples:
#   ./scripts/run_load_tests.sh headless --users 100 --spawn-rate 10 --run-time 60s
#   ./scripts/run_load_tests.sh web
#   ./scripts/run_load_tests.sh distributed --master
#   ./scripts/run_load_tests.sh distributed --worker --master-host=localhost
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
HOST="${LOAD_TEST_HOST:-http://localhost:8000}"
LOCUSTFILE="tests/performance/locustfile.py"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/test-results/load-tests"

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

# Check dependencies
check_deps() {
    if ! command -v locust &> /dev/null; then
        print_error "Locust not installed"
        echo "Install with: pip install locust"
        exit 1
    fi

    if [[ ! -f "$LOCUSTFILE" ]]; then
        print_error "Locustfile not found at: $LOCUSTFILE"
        exit 1
    fi

    print_success "Dependencies checked"
}

# Create results directory
setup_results_dir() {
    mkdir -p "$RESULTS_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    RESULTS_FILE="$RESULTS_DIR/results_${TIMESTAMP}"
    print_success "Results will be saved to: $RESULTS_FILE"
}

# Run headless mode (CI/CD friendly)
run_headless() {
    print_header "Running Load Tests (Headless Mode)"

    # Default values
    USERS=${USERS:-50}
    SPAWN_RATE=${SPAWN_RATE:-10}
    RUN_TIME=${RUN_TIME:-60s}

    echo "Configuration:"
    echo "  Host: $HOST"
    echo "  Users: $USERS"
    echo "  Spawn Rate: $SPAWN_RATE/s"
    echo "  Run Time: $RUN_TIME"
    echo ""

    locust \
        -f "$LOCUSTFILE" \
        --host="$HOST" \
        --users="$USERS" \
        --spawn-rate="$SPAWN_RATE" \
        --run-time="$RUN_TIME" \
        --headless \
        --html="$RESULTS_FILE.html" \
        --csv="$RESULTS_FILE" \
        --loglevel INFO

    print_success "Load tests completed"
    echo -e "\n${GREEN}Results:${NC}"
    echo "  HTML Report: $RESULTS_FILE.html"
    echo "  CSV Stats: $RESULTS_FILE_stats.csv"
    echo "  CSV History: $RESULTS_FILE_stats_history.csv"
}

# Run with web UI
run_web() {
    print_header "Running Load Tests (Web UI Mode)"

    echo "Configuration:"
    echo "  Host: $HOST"
    echo "  Web UI: http://localhost:8089"
    echo ""

    print_warning "Access the Locust web interface at: http://localhost:8089"
    print_warning "Press Ctrl+C to stop"

    locust \
        -f "$LOCUSTFILE" \
        --host="$HOST" \
        --web-host=0.0.0.0 \
        --web-port=8089

    print_success "Load tests stopped"
}

# Run distributed master
run_distributed_master() {
    print_header "Running Load Tests (Distributed Master)"

    echo "Configuration:"
    echo "  Host: $HOST"
    echo "  Mode: Master"
    echo "  Web UI: http://localhost:8089"
    echo ""

    print_warning "Start workers with: ./scripts/run_load_tests.sh distributed --worker"
    print_warning "Access the Locust web interface at: http://localhost:8089"

    locust \
        -f "$LOCUSTFILE" \
        --host="$HOST" \
        --master \
        --web-host=0.0.0.0 \
        --expect-workers="${EXPECT_WORKERS:-1}"

    print_success "Master stopped"
}

# Run distributed worker
run_distributed_worker() {
    MASTER_HOST=${MASTER_HOST:-localhost}
    MASTER_PORT=${MASTER_PORT:-5557}

    print_header "Running Load Tests (Distributed Worker)"

    echo "Configuration:"
    echo "  Master Host: $MASTER_HOST"
    echo "  Master Port: $MASTER_PORT"
    echo ""

    locust \
        -f "$LOCUSTFILE" \
        --worker \
        --master-host="$MASTER_HOST" \
        --master-port="$MASTER_PORT"

    print_success "Worker stopped"
}

# Quick smoke test
run_smoke() {
    print_header "Running Quick Smoke Test"

    print_warning "Running 10 users for 30 seconds..."

    locust \
        -f "$LOCUSTFILE" \
        --host="$HOST" \
        --users=10 \
        --spawn-rate=5 \
        --run-time=30s \
        --headless \
        --html="$RESULTS_FILE.html" \
        --loglevel INFO

    print_success "Smoke test completed"
    echo -e "\n${GREEN}Report: $RESULTS_FILE.html${NC}"
}

# Stress test (high load)
run_stress() {
    print_header "Running Stress Test"

    print_warning "Running 200 users for 5 minutes..."

    locust \
        -f "$LOCUSTFILE" \
        --host="$HOST" \
        --users=200 \
        --spawn-rate=20 \
        --run-time=5m \
        --headless \
        --html="$RESULTS_FILE.html" \
        --csv="$RESULTS_FILE" \
        --loglevel INFO

    print_success "Stress test completed"
    echo -e "\n${GREEN}Results:${NC}"
    echo "  HTML Report: $RESULTS_FILE.html"
    echo "  CSV Stats: $RESULTS_FILE_stats.csv"
}

# Main execution
main() {
    MODE=${1:-headless}
    shift || true  # Remove first argument

    print_header "JioAstro Load Testing"
    echo "Mode: $MODE"
    echo "Host: $HOST"

    check_deps
    setup_results_dir

    case $MODE in
        headless)
            run_headless "$@"
            ;;
        web)
            run_web "$@"
            ;;
        distributed)
            if [[ "$1" == "--master" ]]; then
                run_distributed_master
            elif [[ "$1" == "--worker" ]]; then
                run_distributed_worker
            else
                print_error "Distributed mode requires --master or --worker flag"
                exit 1
            fi
            ;;
        smoke)
            run_smoke
            ;;
        stress)
            run_stress
            ;;
        *)
            print_error "Unknown mode: $MODE"
            echo "Available modes: headless, web, distributed, smoke, stress"
            exit 1
            ;;
    esac
}

# Run main
main "$@"

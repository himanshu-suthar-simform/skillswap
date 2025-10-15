#!/bin/bash

# Test runner script for accounts app
# This script provides various options for running tests with coverage

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
VERBOSE=0
COVERAGE=1
PARALLEL=0
MODULE=""
FAILFAST=0

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run tests for the accounts app with various options.

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Run tests with verbose output
    -n, --no-coverage       Run tests without coverage report
    -p, --parallel          Run tests in parallel
    -m, --module MODULE     Run specific test module (e.g., test_models)
    -f, --failfast          Stop on first test failure
    -c, --coverage-only     Generate coverage report without running tests
    -r, --report            Show coverage report from last run

EXAMPLES:
    $0                                  # Run all tests with coverage
    $0 -v                               # Run with verbose output
    $0 -m test_models                   # Run only model tests
    $0 -p                               # Run tests in parallel
    $0 -f                               # Stop on first failure
    $0 -r                               # Show coverage report

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -n|--no-coverage)
            COVERAGE=0
            shift
            ;;
        -p|--parallel)
            PARALLEL=1
            shift
            ;;
        -m|--module)
            MODULE="$2"
            shift 2
            ;;
        -f|--failfast)
            FAILFAST=1
            shift
            ;;
        -c|--coverage-only)
            print_info "Generating coverage report..."
            coverage report
            coverage html
            print_info "HTML coverage report generated in htmlcov/"
            exit 0
            ;;
        -r|--report)
            print_info "Showing coverage report..."
            coverage report
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Build test command
TEST_CMD="python manage.py test"

# Add module if specified
if [ -n "$MODULE" ]; then
    TEST_CMD="$TEST_CMD accounts.tests.$MODULE"
else
    TEST_CMD="$TEST_CMD"
fi

# Add verbosity
if [ $VERBOSE -eq 1 ]; then
    TEST_CMD="$TEST_CMD --verbosity=2"
fi

# Add parallel execution
if [ $PARALLEL -eq 1 ]; then
    TEST_CMD="$TEST_CMD --parallel"
    print_info "Running tests in parallel mode"
fi

# Add failfast
if [ $FAILFAST -eq 1 ]; then
    TEST_CMD="$TEST_CMD --failfast"
    print_info "Failfast mode enabled"
fi

echo $TEST_CMD

# Run tests with or without coverage
if [ $COVERAGE -eq 1 ]; then
    print_info "Running tests with coverage..."
    coverage erase
    coverage run --source='.' manage.py test

    print_info "Generating coverage report..."
    coverage report
    coverage html
    coverage xml

    print_info "Coverage reports generated:"
    print_info "  - Terminal: (shown above)"
    print_info "  - HTML: htmlcov/index.html"
    print_info "  - XML: coverage.xml"

    # Check coverage percentage
    COVERAGE_PERCENT=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
    if (( $(echo "$COVERAGE_PERCENT < 80" | bc -l) )); then
        print_warning "Coverage is below 80% ($COVERAGE_PERCENT%)"
        exit 1
    else
        print_info "Coverage is $COVERAGE_PERCENT% ✓"
    fi
else
    print_info "Running tests without coverage..."
    $TEST_CMD
fi

print_info "Tests completed successfully! ✓"

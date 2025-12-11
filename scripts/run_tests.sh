#!/bin/bash
# Run Tests with Coverage
# This script runs the complete test suite and generates coverage reports

echo "================================================"
echo "  AI Grading System - Test Runner with Coverage"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
COVERAGE_ONLY=false
FAST=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage-only)
            COVERAGE_ONLY=true
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./run_tests.sh [--coverage-only] [--fast] [-v|--verbose]"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing...${NC}"
    pip install pytest pytest-cov
fi

# Clean previous coverage data
echo -e "${BLUE}🧹 Cleaning previous coverage data...${NC}"
rm -rf .coverage .coverage.* htmlcov/ coverage.xml coverage.json
echo ""

# Run tests
if [ "$COVERAGE_ONLY" = true ]; then
    echo -e "${BLUE}📊 Generating coverage report only (no tests)...${NC}"
    coverage report
    coverage html
else
    echo -e "${BLUE}🧪 Running tests with coverage...${NC}"
    echo ""

    if [ "$FAST" = true ]; then
        # Fast mode - skip slow tests
        pytest -v --cov=. --cov-report=html --cov-report=term-missing -m "not slow and not load"
    elif [ "$VERBOSE" = true ]; then
        # Verbose mode
        pytest -vv --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-report=json
    else
        # Normal mode
        pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-report=json
    fi

    TEST_EXIT_CODE=$?
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Test execution complete!${NC}"
echo "================================================"
echo ""

# Display coverage summary
echo -e "${BLUE}📊 Coverage Summary:${NC}"
coverage report --skip-empty

echo ""
echo "================================================"
echo -e "${GREEN}📁 Coverage Reports Generated:${NC}"
echo "================================================"
echo -e "  ${YELLOW}HTML Report:${NC}    htmlcov/index.html"
echo -e "  ${YELLOW}XML Report:${NC}     coverage.xml"
echo -e "  ${YELLOW}JSON Report:${NC}    coverage.json"
echo -e "  ${YELLOW}Terminal:${NC}       See above"
echo ""

# Check coverage threshold
COVERAGE_PERCENT=$(coverage report | grep "TOTAL" | awk '{print $4}' | sed 's/%//')

if [ ! -z "$COVERAGE_PERCENT" ]; then
    THRESHOLD=85

    echo -e "${BLUE}Coverage: ${COVERAGE_PERCENT}% (Target: ${THRESHOLD}%)${NC}"

    if (( $(echo "$COVERAGE_PERCENT >= $THRESHOLD" | bc -l) )); then
        echo -e "${GREEN}✅ Coverage target met!${NC}"
    else
        echo -e "${YELLOW}⚠️  Coverage below target${NC}"
    fi
fi

echo ""

# Open HTML report (optional)
read -p "Open HTML coverage report in browser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    elif command -v open &> /dev/null; then
        open htmlcov/index.html
    elif command -v start &> /dev/null; then
        start htmlcov/index.html
    else
        echo "Please open htmlcov/index.html manually"
    fi
fi

# Exit with test exit code
exit ${TEST_EXIT_CODE:-0}

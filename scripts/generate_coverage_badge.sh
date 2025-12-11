#!/bin/bash
# Generate Coverage Badge
# Creates a coverage badge SVG for README

echo "Generating coverage badge..."

# Run coverage if not already done
if [ ! -f ".coverage" ]; then
    echo "Running coverage..."
    pytest --cov=. --cov-report=term > /dev/null 2>&1
fi

# Get coverage percentage
COVERAGE=$(coverage report | grep "TOTAL" | awk '{print $4}' | sed 's/%//')

# Determine badge color
if (( $(echo "$COVERAGE >= 90" | bc -l) )); then
    COLOR="brightgreen"
elif (( $(echo "$COVERAGE >= 80" | bc -l) )); then
    COLOR="green"
elif (( $(echo "$COVERAGE >= 70" | bc -l) )); then
    COLOR="yellowgreen"
elif (( $(echo "$COVERAGE >= 60" | bc -l) )); then
    COLOR="yellow"
else
    COLOR="red"
fi

# Generate badge using shields.io format
BADGE_URL="https://img.shields.io/badge/coverage-${COVERAGE}%25-${COLOR}"

# Create badge markdown
echo "[![Coverage](${BADGE_URL})](htmlcov/index.html)" > coverage_badge.md

# Also create HTML version
cat > coverage_badge.html << EOF
<a href="htmlcov/index.html">
  <img src="${BADGE_URL}" alt="Coverage ${COVERAGE}%">
</a>
EOF

echo "✅ Coverage badge generated!"
echo "Coverage: ${COVERAGE}%"
echo "Badge URL: ${BADGE_URL}"
echo ""
echo "Add to README.md:"
cat coverage_badge.md

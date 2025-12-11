#!/bin/bash
# Lighthouse Audit Script
# Tests performance, accessibility, best practices, and SEO

echo "================================================"
echo "  Lighthouse Audit - AI Grading System"
echo "================================================"
echo ""

TARGET_URL="${1:-http://localhost:5000}"
OUTPUT_DIR="lighthouse_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}🔍 Running Lighthouse audit on: $TARGET_URL${NC}"
echo ""

# Check if Lighthouse is installed
if ! command -v lighthouse &> /dev/null; then
    echo -e "${YELLOW}⚠️  Lighthouse not found. Installing...${NC}"
    npm install -g lighthouse
fi

# Run Lighthouse audit
echo -e "${BLUE}Running comprehensive audit...${NC}"

lighthouse "$TARGET_URL" \
    --output html \
    --output json \
    --output-path "$OUTPUT_DIR/report_${TIMESTAMP}" \
    --chrome-flags="--headless --no-sandbox" \
    --quiet

# Parse results
REPORT_JSON="$OUTPUT_DIR/report_${TIMESTAMP}.report.json"

if [ -f "$REPORT_JSON" ]; then
    echo ""
    echo "================================================"
    echo -e "${GREEN}Lighthouse Results${NC}"
    echo "================================================"

    # Extract scores
    PERFORMANCE=$(jq '.categories.performance.score * 100' "$REPORT_JSON" 2>/dev/null || echo "0")
    ACCESSIBILITY=$(jq '.categories.accessibility.score * 100' "$REPORT_JSON" 2>/dev/null || echo "0")
    BEST_PRACTICES=$(jq '.categories["best-practices"].score * 100' "$REPORT_JSON" 2>/dev/null || echo "0")
    SEO=$(jq '.categories.seo.score * 100 "$REPORT_JSON" 2>/dev/null || echo "0")
    PWA=$(jq '.categories.pwa.score * 100' "$REPORT_JSON" 2>/dev/null || echo "0")

    # Function to color score
    color_score() {
        local score=$1
        if (( $(echo "$score >= 90" | bc -l) )); then
            echo -e "${GREEN}${score}${NC}"
        elif (( $(echo "$score >= 50" | bc -l) )); then
            echo -e "${YELLOW}${score}${NC}"
        else
            echo -e "${RED}${score}${NC}"
        fi
    }

    echo -e "  Performance:      $(color_score $PERFORMANCE)/100"
    echo -e "  Accessibility:    $(color_score $ACCESSIBILITY)/100"
    echo -e "  Best Practices:   $(color_score $BEST_PRACTICES)/100"
    echo -e "  SEO:              $(color_score $SEO)/100"
    echo -e "  PWA:              $(color_score $PWA)/100"
    echo ""

    # Check if targets met
    echo "================================================"
    echo -e "${BLUE}Target Validation (95+ for 10/10)${NC}"
    echo "================================================"

    ALL_PASSED=true

    if (( $(echo "$PERFORMANCE >= 95" | bc -l) )); then
        echo -e "${GREEN}✅ Performance >= 95${NC}"
    else
        echo -e "${RED}❌ Performance < 95${NC}"
        ALL_PASSED=false
    fi

    if (( $(echo "$ACCESSIBILITY >= 95" | bc -l) )); then
        echo -e "${GREEN}✅ Accessibility >= 95${NC}"
    else
        echo -e "${RED}❌ Accessibility < 95${NC}"
        ALL_PASSED=false
    fi

    if (( $(echo "$BEST_PRACTICES >= 95" | bc -l) )); then
        echo -e "${GREEN}✅ Best Practices >= 95${NC}"
    else
        echo -e "${RED}❌ Best Practices < 95${NC}"
        ALL_PASSED=false
    fi

    if (( $(echo "$SEO >= 95" | bc -l) )); then
        echo -e "${GREEN}✅ SEO >= 95${NC}"
    else
        echo -e "${RED}❌ SEO < 95${NC}"
        ALL_PASSED=false
    fi

    echo ""

    # Overall result
    if [ "$ALL_PASSED" = true ]; then
        echo -e "${GREEN}🎉 ALL TARGETS MET - PERFECT 10/10!${NC}"
    else
        echo -e "${YELLOW}⚠️  Some targets not met - review report for details${NC}"
    fi

    echo ""
    echo "================================================"
    echo "Reports saved:"
    echo "  HTML: $OUTPUT_DIR/report_${TIMESTAMP}.report.html"
    echo "  JSON: $OUTPUT_DIR/report_${TIMESTAMP}.report.json"
    echo "================================================"

    # Open HTML report
    read -p "Open HTML report in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "$OUTPUT_DIR/report_${TIMESTAMP}.report.html"
        elif command -v open &> /dev/null; then
            open "$OUTPUT_DIR/report_${TIMESTAMP}.report.html"
        elif command -v start &> /dev/null; then
            start "$OUTPUT_DIR/report_${TIMESTAMP}.report.html"
        fi
    fi
else
    echo -e"${RED}❌ Lighthouse report not generated${NC}"
    exit 1
fi

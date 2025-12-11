#!/bin/bash
# Security Audit Script
# Runs comprehensive security scans using OWASP ZAP and other tools

echo "================================================"
echo "  AI Grading System - Security Audit"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
TARGET_URL="${1:-http://localhost:5000}"
OUTPUT_DIR="security_reports"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}🔒 Starting security audit for: $TARGET_URL${NC}"
echo ""

# 1. Check if OWASP ZAP is available
echo -e "${BLUE}1. Checking for OWASP ZAP...${NC}"
if command -v zap.sh &> /dev/null; then
    echo -e "${GREEN}✅ OWASP ZAP found${NC}"
else
    echo -e "${YELLOW}⚠️  OWASP ZAP not found. Download from: https://www.zaproxy.org/download/${NC}"
fi
echo ""

# 2. Check security headers
echo -e "${BLUE}2. Checking security headers...${NC}"
curl -sI "$TARGET_URL" > "$OUTPUT_DIR/headers.txt"

HEADERS_TO_CHECK=(
    "X-Frame-Options"
    "X-Content-Type-Options"
    "Strict-Transport-Security"
    "Content-Security-Policy"
    "X-XSS-Protection"
    "Referrer-Policy"
    "Permissions-Policy"
)

MISSING_HEADERS=0
for header in "${HEADERS_TO_CHECK[@]}"; do
    if grep -qi "$header" "$OUTPUT_DIR/headers.txt"; then
        echo -e "${GREEN}✅ $header present${NC}"
    else
        echo -e "${RED}❌ $header missing${NC}"
        ((MISSING_HEADERS++))
    fi
done

if [ $MISSING_HEADERS -eq 0 ]; then
    echo -e "${GREEN}All security headers present!${NC}"
else
    echo -e "${YELLOW}$MISSING_HEADERS security header(s) missing${NC}"
fi
echo ""

# 3. SSL/TLS Check
echo -e "${BLUE}3. Checking SSL/TLS configuration...${NC}"
if [[ $TARGET_URL == https* ]]; then
    if command -v testssl &> /dev/null; then
        testssl --quiet "$TARGET_URL" > "$OUTPUT_DIR/ssl_report.txt"
        echo -e "${GREEN}✅ SSL/TLS report generated${NC}"
    else
        echo -e "${YELLOW}⚠️  testssl not found. Install from: https://testssl.sh/${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Target uses HTTP (not HTTPS)${NC}"
fi
echo ""

# 4. Dependency Vulnerability Scan
echo -e "${BLUE}4. Scanning Python dependencies for vulnerabilities...${NC}"
if command -v safety &> /dev/null; then
    safety check --json > "$OUTPUT_DIR/dependency_vulnerabilities.json" 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ No known vulnerabilities in dependencies${NC}"
    else
        echo -e "${RED}❌ Vulnerabilities found in dependencies${NC}"
        echo -e "${YELLOW}See: $OUTPUT_DIR/dependency_vulnerabilities.json${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Safety not found. Install: pip install safety${NC}"
fi
echo ""

# 5.Bandit Security Linter
echo -e "${BLUE}5. Running Bandit security linter...${NC}"
if command -v bandit &> /dev/null; then
    bandit -r . -f json -o "$OUTPUT_DIR/bandit_report.json" 2>/dev/null

    # Count severity levels
    HIGH=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "$OUTPUT_DIR/bandit_report.json" 2>/dev/null || echo "0")
    MEDIUM=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' "$OUTPUT_DIR/bandit_report.json" 2>/dev/null || echo "0")

    echo -e "  High severity issues: ${RED}$HIGH${NC}"
    echo -e "  Medium severity issues: ${YELLOW}$MEDIUM${NC}"

    if [ "$HIGH" -eq 0 ] && [ "$MEDIUM" -eq 0 ]; then
        echo -e "${GREEN}✅ No security issues found${NC}"
    else
        echo -e "${YELLOW}⚠️  See: $OUTPUT_DIR/bandit_report.json${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Bandit not found. Install: pip install bandit${NC}"
fi
echo ""

# 6. Check for secrets in code
echo -e "${BLUE}6. Scanning for exposed secrets...${NC}"
if command -v trufflehog &> /dev/null; then
    trufflehog filesystem . --json > "$OUTPUT_DIR/secrets_scan.json" 2>&1

    SECRETS_COUNT=$(wc -l < "$OUTPUT_DIR/secrets_scan.json")
    if [ "$SECRETS_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✅ No secrets found${NC}"
    else
        echo -e "${RED}❌ Potential secrets found: $SECRETS_COUNT${NC}"
        echo -e "${YELLOW}See: $OUTPUT_DIR/secrets_scan.json${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  TruffleHog not found. Install: pip install trufflehog${NC}"
fi
echo ""

# 7. OWASP ZAP Baseline Scan
echo -e "${BLUE}7. Running OWASP ZAP baseline scan...${NC}"
if command -v zap-baseline.py &> /dev/null; then
    docker run --rm -v "$(pwd):/zap/wrk:rw" -t owasp/zap2docker-stable zap-baseline.py \
        -t "$TARGET_URL" \
        -r "$OUTPUT_DIR/zap_baseline_report.html" \
        -J "$OUTPUT_DIR/zap_baseline_report.json" \
        2>&1 | tee "$OUTPUT_DIR/zap_baseline.log"

    echo -e "${GREEN}✅ ZAP baseline scan complete${NC}"
    echo -e "${YELLOW}Report: $OUTPUT_DIR/zap_baseline_report.html${NC}"
else
    echo -e "${YELLOW}⚠️  OWASP ZAP Docker image not available${NC}"
    echo -e "${YELLOW}Run: docker pull owasp/zap2docker-stable${NC}"
fi
echo ""

# 8. Generate Summary Report
echo -e "${BLUE}8. Generating summary report...${NC}"
cat > "$OUTPUT_DIR/summary.md" << EOF
# Security Audit Report

**Date**: $(date)
**Target**: $TARGET_URL

## Summary

### Security Headers
- Missing Headers: $MISSING_HEADERS

### Dependencies
- See: dependency_vulnerabilities.json

### Code Security (Bandit)
- High Severity: $HIGH
- Medium Severity: $MEDIUM

### Secrets Scan
- Check: secrets_scan.json

### OWASP ZAP
- Report: zap_baseline_report.html

## Recommendations

1. **Security Headers**: Ensure all recommended headers are present
2. **Dependencies**: Update vulnerable packages
3. **Code Issues**: Fix high severity Bandit findings
4. **Secrets**: Remove any exposed secrets
5. **SSL/TLS**: Use HTTPS with strong cipher suites

## Files Generated

- headers.txt
- ssl_report.txt
- dependency_vulnerabilities.json
- bandit_report.json
- secrets_scan.json
- zap_baseline_report.html
- zap_baseline_report.json

EOF

echo -e "${GREEN}✅ Summary report generated: $OUTPUT_DIR/summary.md${NC}"
echo ""

# Final Summary
echo "================================================"
echo -e "${GREEN}Security Audit Complete!${NC}"
echo "================================================"
echo ""
echo -e "${BLUE}Reports saved to: $OUTPUT_DIR/${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Review all reports in $OUTPUT_DIR/"
echo "2. Fix high severity issues immediately"
echo "3. Address medium severity issues"
echo "4. Implement missing security headers"
echo "5. Run full ZAP scan for production deployment"
echo ""

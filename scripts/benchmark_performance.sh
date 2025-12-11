#!/bin/bash
# Performance Benchmarking Script
# Measures and documents system performance

echo "================================================"
echo "  AI Grading System - Performance Benchmark"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TARGET_URL="${1:-http://localhost:5000}"
OUTPUT_FILE="performance_benchmark_$(date +%Y%m%d_%H%M%S).json"

echo -e "${BLUE}📊 Benchmarking: $TARGET_URL${NC}"
echo ""

# 1. Response Time Benchmark
echo -e "${BLUE}1. Testing Response Times...${NC}"

ENDPOINTS=(
    "/"
    "/health"
    "/api/submissions/recent"
    "/api/gamification/leaderboard"
    "/api/dashboard/analytics"
)

declare -A response_times

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "  Testing $endpoint... "

    # Make 10 requests and calculate average
    total=0
    for i in {1..10}; do
        time=$(curl -o /dev/null -s -w '%{time_total}\n' "$TARGET_URL$endpoint")
        total=$(echo "$total + $time" | bc)
    done

    avg=$(echo "scale=3; $total / 10" | bc)
    avg_ms=$(echo "$avg * 1000" | bc)

    response_times["$endpoint"]=$avg_ms

    if (( $(echo "$avg_ms < 200" | bc -l) )); then
        echo -e "${GREEN}✅ ${avg_ms}ms${NC}"
    elif (( $(echo "$avg_ms < 500" | bc -l) )); then
        echo -e "${YELLOW}⚠️  ${avg_ms}ms${NC}"
    else
        echo -e "${RED}❌ ${avg_ms}ms (> 500ms)${NC}"
    fi
done

echo ""

# 2. Concurrent Users Test
echo -e "${BLUE}2. Testing Concurrent Users (using AB)...${NC}"

if command -v ab &> /dev/null; then
    ab -n 1000 -c 100 -g concurrent_test.tsv "$TARGET_URL/" > /dev/null 2>&1

    # Parse results
    requests_per_sec=$(ab -n 1000 -c 100 "$TARGET_URL/" 2>/dev/null | grep "Requests per second" | awk '{print $4}')
    time_per_request=$(ab -n 1000 -c 100 "$TARGET_URL/" 2>/dev/null | grep "Time per request" | head -1 | awk '{print $4}')

    echo -e "  Requests/sec: ${GREEN}$requests_per_sec${NC}"
    echo -e "  Time/request: ${GREEN}${time_per_request}ms${NC}"
else
    echo -e "${YELLOW}⚠️  Apache Bench not found. Install: apt-get install apache2-utils${NC}"
fi

echo ""

# 3. Database Query Performance
echo -e "${BLUE}3. Database Performance...${NC}"
echo "  Testing MongoDB query times..."

python3 << 'PYTHON'
from pymongo import MongoClient
import time
import os

try:
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    db = client['ai_grading']

    # Test query performance
    start = time.time()
    submissions = list(db.submissions.find().limit(100))
    query_time = (time.time() - start) * 1000

    if query_time < 50:
        print(f"  ✅ Query time: {query_time:.2f}ms (< 50ms)")
    elif query_time < 100:
        print(f"  ⚠️  Query time: {query_time:.2f}ms")
    else:
        print(f"  ❌ Query time: {query_time:.2f}ms (> 100ms)")

except Exception as e:
    print(f"  ⚠️  Could not connect to MongoDB: {e}")
PYTHON

echo ""

# 4. Cache Performance
echo -e "${BLUE}4. Redis Cache Performance...${NC}"

if command -v redis-cli &> /dev/null; then
    # Test Redis ping
    redis_ping=$(redis-cli ping 2>/dev/null)

    if [ "$redis_ping" = "PONG" ]; then
        echo -e "  ${GREEN}✅ Redis is responding${NC}"

        # Test cache hit rate
        info=$(redis-cli info stats 2>/dev/null)
        hits=$(echo "$info" | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
        misses=$(echo "$info" | grep keyspace_misses | cut -d: -f2 | tr -d '\r')

        if [ ! -z "$hits" ] && [ ! -z "$misses" ]; then
            total=$((hits + misses))
            if [ $total -gt 0 ]; then
                hit_rate=$(echo "scale=2; ($hits / $total) * 100" | bc)
                echo -e "  Cache hit rate: ${GREEN}${hit_rate}%${NC}"
            fi
        fi
    else
        echo -e "  ${YELLOW}⚠️  Redis not responding${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  redis-cli not found${NC}"
fi

echo ""

# 5. Generate JSON Report
echo -e "${BLUE}5. Generating Performance Report...${NC}"

cat > "$OUTPUT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "target_url": "$TARGET_URL",
  "response_times_ms": {
$(for endpoint in "${!response_times[@]}"; do
    echo "    \"$endpoint\": ${response_times[$endpoint]},"
done | sed '$ s/,$//')
  },
  "concurrent_users": {
    "requests_per_second": ${requests_per_sec:-0},
    "time_per_request_ms": ${time_per_request:-0}
  },
  "benchmarks": {
    "response_time_target": 200,
    "query_time_target": 50,
    "cache_hit_rate_target": 90
  },
  "status": "complete"
}
EOF

echo -e "${GREEN}✅ Report saved: $OUTPUT_FILE${NC}"
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}Performance Benchmark Complete!${NC}"
echo "================================================"
echo ""
echo -e "${BLUE}Key Metrics:${NC}"
echo -e "  Response Time Target: ${GREEN}< 200ms${NC}"
echo -e "  Query Time Target: ${GREEN}< 50ms${NC}"
echo -e "  Cache Hit Rate Target: ${GREEN}> 90%${NC}"
echo ""
echo -e "${YELLOW}Recommendations:${NC}"
echo "1. Optimize queries taking > 50ms"
echo "2. Add caching for frequently accessed data"
echo "3. Use CDN for static assets"
echo "4. Enable HTTP/2"
echo "5. Implement database connection pooling"
echo ""

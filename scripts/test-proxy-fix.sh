#!/bin/bash

echo "🔧 Multi-Agent Observability System - Proxy Fix Test"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "\n${YELLOW}Current proxy settings:${NC}"
echo "HTTP_PROXY: $HTTP_PROXY"
echo "http_proxy: $http_proxy"
echo "HTTPS_PROXY: $HTTPS_PROXY"
echo "https_proxy: $https_proxy"
echo "NO_PROXY: $NO_PROXY"
echo "no_proxy: $no_proxy"

# Step 1: Start the server in background
echo -e "\n${GREEN}Step 1: Starting server...${NC}"
cd "$PROJECT_ROOT/apps/server"
bun run start &
SERVER_PID=$!
sleep 3

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started successfully (PID: $SERVER_PID)"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    exit 1
fi

# Step 2: Test send_event.py directly with debug
echo -e "\n${GREEN}Step 2: Testing send_event.py with proxy environment...${NC}"
cd "$PROJECT_ROOT/.claude/hooks"

echo '{"session_id":"proxy-test","tool_name":"TestTool","tool_input":{"test":"proxy-bypass"}}' | \
    uv run send_event.py --source-app proxy-test --event-type PreToolUse --debug

HOOK_EXIT_CODE=$?
echo "Exit code: $HOOK_EXIT_CODE"

if [ $HOOK_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ send_event.py succeeded with proxy environment${NC}"
else
    echo -e "${RED}❌ send_event.py failed with proxy environment${NC}"
fi

# Step 3: Test multiple rapid requests
echo -e "\n${GREEN}Step 3: Testing multiple rapid requests...${NC}"
SUCCESS_COUNT=0
TOTAL_REQUESTS=5

for i in $(seq 1 $TOTAL_REQUESTS); do
    echo "Request $i..."
    echo "{\"session_id\":\"proxy-test-$i\",\"tool_name\":\"TestTool\",\"request_id\":$i}" | \
        uv run send_event.py --source-app proxy-test --event-type PostToolUse --debug 2>/dev/null
    
    if [ $? -eq 0 ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "  ✅ Request $i succeeded"
    else
        echo -e "  ${RED}❌ Request $i failed${NC}"
    fi
done

echo -e "\n${YELLOW}Results: $SUCCESS_COUNT/$TOTAL_REQUESTS requests succeeded${NC}"

# Step 4: Verify events were received
echo -e "\n${GREEN}Step 4: Verifying events were received...${NC}"
# Using curl with --noproxy to ensure it works regardless of proxy settings
EVENTS=$(curl --noproxy "*" -s http://localhost:4000/events/recent?limit=10)
EVENT_COUNT=$(echo "$EVENTS" | python3 -c "import json,sys; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

echo "Total events in server: $EVENT_COUNT"
if [ "$EVENT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Events were successfully received by server${NC}"
else
    echo -e "${RED}❌ No events found in server${NC}"
fi

# Step 5: Test with curl for comparison
echo -e "\n${GREEN}Step 5: Testing curl behavior with proxy...${NC}"
echo "Testing curl without --noproxy:"
curl -s -w "HTTP_CODE:%{http_code}\n" \
  -X POST http://localhost:4000/events \
  -H "Content-Type: application/json" \
  -d '{"source_app":"curl-test","session_id":"curl-test","hook_event_type":"TestEvent","payload":{"test":true}}' \
  2>&1 | tail -3

echo -e "\nTesting curl with --noproxy:"
curl --noproxy "*" -s -w "HTTP_CODE:%{http_code}\n" \
  -X POST http://localhost:4000/events \
  -H "Content-Type: application/json" \
  -d '{"source_app":"curl-test","session_id":"curl-test","hook_event_type":"TestEvent","payload":{"test":true}}' \
  2>&1 | tail -3

# Cleanup
echo -e "\n${GREEN}Cleaning up...${NC}"
kill $SERVER_PID 2>/dev/null
echo "✅ Server stopped"

echo -e "\n${GREEN}Proxy Fix Test Complete!${NC}"
echo -e "${YELLOW}Summary:${NC}"
echo "- send_event.py should now work correctly even with proxy enabled"
echo "- Python urllib automatically bypasses proxy for localhost connections"
echo "- All Claude Code hook events should now reach the observability server"
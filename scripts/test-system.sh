#!/bin/bash

echo "🚀 Multi-Agent Observability System Test"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Step 1: Start the server in background
echo -e "\n${GREEN}Step 1: Starting server...${NC}"
cd "$PROJECT_ROOT/apps/server"
echo "🔍 Debug: Current directory: $(pwd)"
echo "🔍 Debug: Checking for package.json..."
ls -la package.json 2>/dev/null || echo "No package.json found"

echo "🔍 Debug: Starting server with 'bun run start'..."
bun run start &
SERVER_PID=$!
echo "🔍 Debug: Server PID: $SERVER_PID"

# Give more time for server to start up
sleep 5

# Check if server is running
echo "🔍 Debug: Checking if server process is still alive..."
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started successfully (PID: $SERVER_PID)"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    echo "🔍 Debug: Checking for any error logs..."
    # Try to get any output from the background process
    exit 1
fi

# Step 2: Test sending an event
echo -e "\n${GREEN}Step 2: Testing event endpoint...${NC}"
echo "🔍 Debug: Attempting to send POST request to http://localhost:4000/events"

# Disable proxy for localhost connections
export no_proxy="localhost,127.0.0.1"
export NO_PROXY="localhost,127.0.0.1"

# Test server connectivity first
echo "🔍 Debug: Testing server connectivity..."
curl --noproxy "*" -v --connect-timeout 5 http://localhost:4000/health 2>&1 | head -10

echo "🔍 Debug: Sending event payload..."
RESPONSE=$(curl --noproxy "*" -v -w "HTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\n" \
  -X POST http://localhost:4000/events \
  -H "Content-Type: application/json" \
  -d '{"source_app":"test","session_id":"test-123","hook_event_type":"PreToolUse","payload":{"tool":"Bash","command":"ls -la"}}' \
  2>&1)

EXIT_CODE=$?
echo "🔍 Debug: curl exit code: $EXIT_CODE"
echo "🔍 Debug: Full curl response:"
echo "$RESPONSE"

if [ $EXIT_CODE -eq 0 ] && echo "$RESPONSE" | grep -q "HTTP_CODE:200"; then
    echo "✅ Event sent successfully"
else
    echo -e "${RED}❌ Failed to send event (exit code: $EXIT_CODE)${NC}"
fi

# Step 3: Test filter options endpoint
echo -e "\n${GREEN}Step 3: Testing filter options endpoint...${NC}"
echo "🔍 Debug: Sending GET request to http://localhost:4000/events/filter-options"

FILTERS=$(curl --noproxy "*" -v -w "HTTP_CODE:%{http_code}\n" -s http://localhost:4000/events/filter-options 2>&1)
FILTER_EXIT_CODE=$?

echo "🔍 Debug: curl exit code: $FILTER_EXIT_CODE"
echo "🔍 Debug: Filter response:"
echo "$FILTERS"

if [ $FILTER_EXIT_CODE -eq 0 ] && echo "$FILTERS" | grep -q "HTTP_CODE:200"; then
    echo "✅ Filter options retrieved"
else
    echo -e "${RED}❌ Failed to get filter options (exit code: $FILTER_EXIT_CODE)${NC}"
fi

# Step 4: Test demo agent hook
echo -e "\n${GREEN}Step 4: Testing demo agent hook script...${NC}"
echo "🔍 Debug: Changing to demo agent directory: $PROJECT_ROOT/apps/demo-cc-agent"

# Always use main hooks directory since demo-cc-agent doesn't have the script
echo "🔍 Debug: Using main hooks directory"
cd "$PROJECT_ROOT/.claude/hooks"

echo "🔍 Debug: Current working directory: $(pwd)"
echo "🔍 Debug: Listing files in current directory..."
ls -la *.py

echo "🔍 Debug: Testing send_event.py script..."

# Export no_proxy for Python script too
export no_proxy="localhost,127.0.0.1"
export NO_PROXY="localhost,127.0.0.1"

# Test the send_event.py script with debug output
echo '{"session_id":"demo-test","tool_name":"Bash","tool_input":{"command":"echo test"}}' | \
    uv run send_event.py --source-app demo --event-type PreToolUse --debug 2>&1

HOOK_EXIT_CODE=$?
echo "🔍 Debug: Hook script exit code: $HOOK_EXIT_CODE"

if [ $HOOK_EXIT_CODE -eq 0 ]; then
    echo "✅ Demo agent hook executed successfully"
else
    echo -e "${RED}❌ Demo agent hook failed (exit code: $HOOK_EXIT_CODE)${NC}"
fi

# Step 5: Check recent events
echo -e "\n${GREEN}Step 5: Checking recent events...${NC}"
echo "🔍 Debug: Sending GET request to http://localhost:4000/events/recent?limit=5"

RECENT=$(curl --noproxy "*" -v -w "HTTP_CODE:%{http_code}\n" -s http://localhost:4000/events/recent?limit=5 2>&1)
RECENT_EXIT_CODE=$?

echo "🔍 Debug: curl exit code: $RECENT_EXIT_CODE"
echo "🔍 Debug: Recent events response:"
echo "$RECENT"

if [ $RECENT_EXIT_CODE -eq 0 ] && echo "$RECENT" | grep -q "HTTP_CODE:200"; then
    echo "✅ Recent events retrieved"
    # Try to format JSON if possible
    RECENT_JSON=$(echo "$RECENT" | sed '/HTTP_CODE:/d')
    echo "Events: $RECENT_JSON" | python3 -m json.tool 2>/dev/null || echo "$RECENT_JSON"
else
    echo -e "${RED}❌ Failed to get recent events (exit code: $RECENT_EXIT_CODE)${NC}"
fi

# Cleanup
echo -e "\n${GREEN}Cleaning up...${NC}"
kill $SERVER_PID 2>/dev/null
echo "✅ Server stopped"

echo -e "\n${GREEN}Test complete!${NC}"
echo "To run the full system:"
echo "1. In terminal 1: cd apps/server && bun run dev"
echo "2. In terminal 2: cd apps/client && bun run dev"
echo "3. Open http://localhost:5173 in your browser"
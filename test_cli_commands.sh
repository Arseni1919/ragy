#!/bin/bash
# Test script for CLI commands

echo "Starting API server..."
uv run uvicorn ragy_api.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
API_PID=$!

echo "Waiting for API server to start..."
sleep 12

echo ""
echo "=== Testing search_bd command ==="
echo "AI trends" | uv run ragy << 'COMMANDS'
search_bd
AI trends
2
exit
COMMANDS

echo ""
echo ""
echo "=== Testing search_tvly command ==="
echo "" | uv run ragy << 'COMMANDS'
search_tvly
Quantum computing
exit
COMMANDS

echo ""
echo "Stopping API server..."
kill $API_PID

echo ""
echo "✅ CLI command tests completed!"

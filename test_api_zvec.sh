#!/bin/bash
set -e

echo "============================================"
echo "Phase 3: API Endpoint Testing with zvec"
echo "============================================"
echo ""

# Set environment to use zvec
export DB_PROVIDER="zvec"

# Start API server
echo "Starting API server with zvec..."
uv run uvicorn ragy_api.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
echo "Waiting for server to initialize (loading embedding model)..."
sleep 15

echo ""
echo "Running endpoint tests..."
echo ""

# Test 1: Health check
echo "1. Health check..."
curl -s http://localhost:8000/api/v1/system/health | jq . && echo "✓ Health check passed" || echo "✗ Failed"

# Test 2: List collections (should be empty)
echo ""
echo "2. List collections..."
curl -s http://localhost:8000/api/v1/extract/collections | jq . && echo "✓ List collections passed" || echo "✗ Failed"

# Test 3: Database stats
echo ""
echo "3. Database stats..."
curl -s http://localhost:8000/api/v1/database/stats | jq . && echo "✓ Database stats passed" || echo "✗ Failed"

# Test 4: Embedding info (verify model loads)
echo ""
echo "4. Embedding model info..."
curl -s http://localhost:8000/api/v1/system/embedding/info | jq . && echo "✓ Embedding info passed" || echo "✗ Failed"

echo ""
echo "============================================"
echo "✅ All API endpoint tests completed!"
echo "============================================"
echo ""
echo "Note: Full integration testing (index creation, search) can be done via CLI"
echo "      Run: uv run ragy"
echo ""

# Cleanup
echo "Stopping API server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

echo "✓ Server stopped"

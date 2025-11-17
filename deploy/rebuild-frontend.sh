#!/bin/bash
# ============================================
# DES System - Force Rebuild Frontend Script
# ============================================
# Use this script when frontend changes are not being picked up
# This will completely rebuild frontend WITHOUT using cache

set -e

echo "======================================"
echo "Force Rebuilding Frontend (No Cache)"
echo "======================================"
echo ""

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production not found"
    exit 1
fi

echo "📋 Current configuration:"
echo "   VITE_API_BASE_URL: $(grep VITE_API_BASE_URL .env.production | head -1)"
echo ""

# Stop frontend
echo "🛑 Stopping frontend container..."
docker compose stop frontend
docker compose rm -f frontend

# Remove frontend image
echo "🗑️  Removing frontend image..."
docker rmi -f des-system-design-frontend 2>/dev/null || true

# Clear build cache
echo "🧹 Clearing build cache..."
docker builder prune -f

echo ""
echo "🔨 Rebuilding frontend from scratch (this may take 2-3 minutes)..."
docker compose --env-file .env.production build --no-cache frontend

echo ""
echo "🚀 Starting frontend..."
docker compose --env-file .env.production up -d frontend

echo ""
echo "⏳ Waiting for frontend to start..."
sleep 5

echo ""
echo "✅ Verifying build results..."
echo ""

# Verification
echo "1. Worker processes (should be ~5):"
WORKER_COUNT=$(docker exec des-frontend ps aux | grep nginx | wc -l)
echo "   Count: $WORKER_COUNT"
if [ "$WORKER_COUNT" -lt 10 ]; then
    echo "   ✓ PASS"
else
    echo "   ✗ FAIL (still too many workers)"
fi

echo ""
echo "2. Nginx config (should be 'worker_processes 4;'):"
WORKER_CONFIG=$(docker exec des-frontend cat /etc/nginx/nginx.conf | grep "worker_processes")
echo "   $WORKER_CONFIG"
if echo "$WORKER_CONFIG" | grep -q "worker_processes.*4;"; then
    echo "   ✓ PASS"
else
    echo "   ✗ FAIL (still using auto)"
fi

echo ""
echo "3. BaseURL in JS (should be empty ''):"
BASEURL=$(docker exec des-frontend sh -c 'cat /usr/share/nginx/html/assets/index-*.js' | grep -o 'baseURL:"[^"]*"' | head -1)
echo "   $BASEURL"
if [ "$BASEURL" = 'baseURL:""' ]; then
    echo "   ✓ PASS"
else
    echo "   ✗ FAIL (still using old default)"
fi

echo ""
echo "======================================"
echo "Rebuild Complete!"
echo "======================================"
echo ""
echo "⚠️  Important: Clear your browser cache!"
echo "   - Press Ctrl+Shift+Delete"
echo "   - Or hard refresh with Ctrl+F5"
echo ""
echo "Frontend should now use nginx proxy (no :8000 in API calls)"

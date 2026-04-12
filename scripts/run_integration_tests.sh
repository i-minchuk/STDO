#!/usr/bin/env bash
# Run integration tests with Docker Compose
# Usage: ./scripts/run_integration_tests.sh

set -e

echo "=========================================="
echo "Integration Tests Runner"
echo "=========================================="

# Clean up any existing containers
echo "[1/5] Cleaning up existing containers..."
docker compose -f docker-compose.test.yml down -v --remove-orphans 2>/dev/null || true

# Start services
echo "[2/5] Starting services..."
docker compose -f docker-compose.test.yml up -d postgres

# Wait for database to be ready
echo "[3/5] Waiting for database to be ready..."
for i in {1..30}; do
    if docker compose -f docker-compose.test.yml exec -T postgres pg_isready -U test -d iris_test > /dev/null 2>&1; then
        echo "Database is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Run migrations and tests
echo "[4/5] Running migrations and integration tests..."
docker compose -f docker-compose.test.yml run --rm test_runner

# Show results
echo "[5/5] Test results:"
docker compose -f docker-compose.test.yml logs test_runner

# Cleanup (optional - comment out to inspect containers)
echo ""
echo "Cleaning up..."
docker compose -f docker-compose.test.yml down -v

echo "=========================================="
echo "Integration tests completed!"
echo "=========================================="

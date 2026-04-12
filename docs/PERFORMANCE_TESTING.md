# Performance Testing Guide

## Locust Setup

### Installation

```bash
pip install locust
```

### Running Tests

#### Basic Usage

```bash
# Run with web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Headless mode (CLI only)
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 --run-time 5m

# Specific user types
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 --run-time 10m
```

#### Parameters

- `-u, --users`: Peak number of concurrent users
- `-r, --spawn-rate`: Users spawned per second
- `--run-time`: Test duration (e.g., "5m", "1h")
- `--headless`: Run without web UI
- `--host`: Target API URL

### Test Scenarios

| Scenario | Users | Spawn Rate | Duration | Description |
|----------|-------|------------|----------|-------------|
| Smoke | 10 | 2/min | 2m | Basic functionality |
| Load | 50 | 5/sec | 10m | Normal usage |
| Stress | 100 | 10/sec | 15m | Peak load |
| Soak | 30 | 1/sec | 1h | Long-running stability |
| Spike | 0→100 | 20/sec | 5m | Sudden traffic surge |

### Running Scenarios

```bash
# Smoke test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 --run-time 2m

# Load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 --run-time 10m

# Stress test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 --run-time 15m

# With web UI for monitoring
locust -f tests/performance/locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089
```

### Performance Targets

| Endpoint | RPS | Latency (p95) | Error Rate |
|----------|-----|---------------|------------|
| GET /health | 1000+ | <50ms | <0.1% |
| GET /api/projects | 100+ | <200ms | <1% |
| GET /api/documents | 100+ | <200ms | <1% |
| POST /api/auth/login | 50+ | <500ms | <1% |
| POST /api/projects/create-from-tender | 10+ | <2s | <5% |

### CI/CD Integration

Add to `.github/workflows/performance.yml`:

```yaml
name: Performance Tests

on:
  pull_request:
    branches: [main]

jobs:
  performance-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: iris_test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust
      
      - name: Run migrations
        run: python -m db.migrations_runner
        env:
          DB_DSN: postgresql://postgres:postgres@localhost:5432/iris_test
      
      - name: Start API server
        run: |
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 10
        env:
          DB_DSN: postgresql://postgres:postgres@localhost:5432/iris_test
          SECRET_KEY: test-secret-key
      
      - name: Run load test
        run: |
          locust -f tests/performance/locustfile.py \
            --host=http://localhost:8000 \
            --headless \
            -u 50 \
            -r 5 \
            --run-time 5m \
            --html=performance-report.html
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: performance-report
          path: performance-report.html
```

### Analyzing Results

#### Web UI

1. Start Locust with web UI: `locust -f tests/performance/locustfile.py`
2. Open http://localhost:8089
3. Enter number of users and spawn rate
4. Monitor real-time metrics:
   - Requests/s
   - Failures/s
   - Response times (min, median, avg, max)
   - Response time distribution

#### CLI Output

```
Name                                      # reqs      # fails  req/s     fail/s  avg(ms)   med(ms)
---------------------------------------------------------------------------------------------
GET /api/projects                           5000     0(0.00%)    16.7      0.00      45.2      32
POST /api/auth/login                        1000     0(0.00%)    3.3       0.00      125.3     98
```

#### Key Metrics

- **RPS (Requests per Second)**: Throughput capacity
- **Latency (p50, p95, p99)**: Response time percentiles
- **Error Rate**: Percentage of failed requests
- **CPU/Memory**: Server resource utilization

### Troubleshooting

#### High Latency

1. Check database connection pool
2. Review slow queries
3. Check network latency
4. Monitor CPU/memory usage

#### High Error Rate

1. Check application logs
2. Review rate limiting
3. Verify authentication
4. Check database constraints

#### Resource Exhaustion

1. Increase server resources
2. Optimize database queries
3. Enable caching
4. Scale horizontally

### Best Practices

1. **Test in isolation**: Use dedicated test environment
2. **Start small**: Begin with smoke tests
3. **Monitor everything**: Logs, metrics, traces
4. **Baseline first**: Measure before optimizing
5. **Realistic data**: Use production-like datasets
6. **Gradual ramp-up**: Don't spike immediately
7. **Document results**: Track performance over time

## k6 Alternative

For JavaScript-based performance testing:

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/docs/getting-started/installation/

# Run test
k6 run tests/performance/script.js

# With custom options
k6 run --vus 50 --duration 5m tests/performance/script.js
```

### Example k6 Script

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '5m',
};

export default function () {
  const res = http.get('http://localhost:8000/api/projects');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

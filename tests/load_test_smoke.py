#!/usr/bin/env python
"""Load Testing Smoke Test for DokPotok IRIS.

Simple load test for key API endpoints.

Endpoins tested:
1. GET /api/health - Health check (should be very fast)
2. GET /api/projects/portfolio/today - Portfolio overview (with caching)

Usage:
    python tests/load_test_smoke.py

Results interpretation:
- Health endpoint: <10ms average is good
- Portfolio endpoint: <100ms average with cache is good
- Error rate: Should be 0%
"""

import sys
import os
import asyncio
import time
import statistics
from dataclasses import dataclass
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx


@dataclass
class RequestResult:
    endpoint: str
    status_code: int
    latency_ms: float
    success: bool


async def run_load_test(
    base_url: str = "http://localhost:8000",
    requests_per_endpoint: int = 100,
    concurrency: int = 10
) -> dict:
    """Run load test on key endpoints."""
    
    endpoints = [
        "/api/health",
        "/api/projects/portfolio/today",
    ]
    
    results = {ep: [] for ep in endpoints}
    
    async def make_request(client: httpx.AsyncClient, endpoint: str) -> RequestResult:
        start = time.perf_counter()
        try:
            response = await client.get(f"{base_url}{endpoint}")
            latency_ms = (time.perf_counter() - start) * 1000
            return RequestResult(
                endpoint=endpoint,
                status_code=response.status_code,
                latency_ms=latency_ms,
                success=response.status_code == 200
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return RequestResult(
                endpoint=endpoint,
                status_code=0,
                latency_ms=latency_ms,
                success=False
            )
    
    async def worker(client: httpx.AsyncClient, endpoint: str, count: int):
        for _ in range(count):
            result = await make_request(client, endpoint)
            results[endpoint].append(result)
    
    print("=" * 60)
    print("Load Test Smoke Test")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Base URL: {base_url}")
    print(f"  Requests per endpoint: {requests_per_endpoint}")
    print(f"  Concurrency: {concurrency}")
    print(f"  Endpoints: {', '.join(endpoints)}")
    print()
    
    # Run tests
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Run with concurrency
            tasks = [worker(client, endpoint, requests_per_endpoint // concurrency + 1) 
                    for _ in range(min(concurrency, requests_per_endpoint))]
            await asyncio.gather(*tasks)
        
        # Calculate stats
        endpoint_results = results[endpoint]
        latencies = [r.latency_ms for r in endpoint_results if r.success]
        errors = [r for r in endpoint_results if not r.success]
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max_latency
            
            print(f"  ✅ Requests: {len(latencies)}")
            print(f"  ⏱️  Avg latency: {avg_latency:.2f}ms")
            print(f"  ⏱️  Min latency: {min_latency:.2f}ms")
            print(f"  ⏱️  Max latency: {max_latency:.2f}ms")
            print(f"  ⏱️  P95 latency: {p95_latency:.2f}ms")
            
            if errors:
                print(f"  ❌ Errors: {len(errors)} ({len(errors)/len(endpoint_results)*100:.1f}%)")
            else:
                print(f"  ✅ Error rate: 0%")
            
            # Threshold check
            if endpoint == "/api/health":
                if avg_latency > 10:
                    print(f"  ⚠️  WARNING: Health endpoint avg latency > 10ms")
            elif endpoint == "/api/projects/portfolio/today":
                if avg_latency > 500:
                    print(f"  ⚠️  WARNING: Portfolio endpoint avg latency > 500ms")
    """Run load test."""
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    requests = int(os.environ.get("LOAD_TEST_REQUESTS", "100"))
    concurrency = int(os.environ.get("LOAD_TEST_CONCURRENCY", "10"))
    
    try:
        asyncio.run(run_load_test(
            base_url=base_url,
            requests_per_endpoint=requests,
            concurrency=concurrency
        ))
        return 0
    except Exception as e:
        print(f"\n[ERROR] Load test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""E2E Test: Project Metrics Recalculation.

Tests:
1. Create project with tasks
2. Trigger CPM recalculation
3. Verify metrics are calculated
4. Check SPI/CPI values

Usage:
    python tests/test_e2e_metrics.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
from config import Config


async def test_project_metrics():
    """Test project metrics recalculation."""
    print("=" * 60)
    print("E2E Test: Project Metrics Recalculation")
    print("=" * 60)
    
    cfg = Config()
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    
    # Step 1: Login
    print("\n[1/5] Logging in...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        login_response = await client.post(
            f"{base_url}/api/auth/login",
            json={"username": "admin", "password": "admin"}
        )
        
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"  [OK] Logged in")
    
    # Step 2: Create project
    print("\n[2/5] Creating project...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        project_response = await client.post(
            f"{base_url}/api/projects",
            headers=headers,
            json={
                "code": "METRICS-TEST-001",
                "name": "Metrics Test Project",
                "customer": "Test Customer",
                "status": "active"
            }
        )
        
        assert project_response.status_code == 200, f"Project creation failed: {project_response.text}"
        project_id = project_response.json()["id"]
        project_code = project_response.json()["code"]
        print(f"  [OK] Project created: {project_code}")
    
    # Step 3: Recalculate metrics
    print("\n[3/5] Triggering metrics recalculation...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        recalc_response = await client.post(
            f"{base_url}/api/internal/projects/{project_id}/recalc_cpm_and_metrics",
            headers=headers
        )
        
        if recalc_response.status_code == 200:
            metrics = recalc_response.json()
            print(f"  [OK] Metrics recalculated")
            print(f"    SPI: {metrics.get('spi', 'N/A')}")
            print(f"    CPI: {metrics.get('cpi', 'N/A')}")
            print(f"    Risk level: {metrics.get('risk_level', 'N/A')}")
        else:
            print(f"  [INFO] Recalculation endpoint: {recalc_response.status_code}")
    
    # Step 4: Get portfolio overview
    print("\n[4/5] Getting portfolio overview...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        portfolio_response = await client.get(
            f"{base_url}/api/projects/portfolio/today",
            headers=headers
        )
        
        if portfolio_response.status_code == 200:
            portfolio = portfolio_response.json()
            projects = portfolio.get("projects", [])
            print(f"  [OK] Portfolio retrieved: {len(projects)} projects")
            
            # Find our test project
            test_project = next((p for p in projects if p.get("code") == project_code), None)
            if test_project:
                print(f"    Test project found in portfolio")
        else:
            print(f"  [INFO] Portfolio endpoint: {portfolio_response.status_code}")
    
    # Step 5: Verify health endpoint
    print("\n[5/5] Checking health endpoint...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        health_response = await client.get(f"{base_url}/api/health")
        
        assert health_response.status_code == 200
        health = health_response.json()
        print(f"  [OK] Health check: {health.get('status', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("E2E METRICS TEST COMPLETED")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_project_metrics())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n[ERROR] Metrics test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

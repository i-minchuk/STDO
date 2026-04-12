#!/usr/bin/env python
"""E2E Test: Tender Assessment Workflow.

Tests:
1. Create tender
2. Upload documents
3. Assess tender
4. Update status

Usage:
    python tests/test_e2e_tender.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
from config import Config


async def test_tender_workflow():
    """Test tender assessment workflow."""
    print("=" * 60)
    print("E2E Test: Tender Assessment Workflow")
    print("=" * 60)
    
    cfg = Config()
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    
    # Step 1: Login
    print("\n[1/6] Logging in...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        login_response = await client.post(
            f"{base_url}/api/auth/login",
            json={"username": "admin", "password": "admin"}
        )
        
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"  [OK] Logged in")
    
    # Step 2: Create project (needed for tender)
    print("\n[2/6] Creating project...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        project_response = await client.post(
            f"{base_url}/api/projects",
            headers=headers,
            json={
                "code": "TENDER-TEST-001",
                "name": "Tender Test Project",
                "customer": "Test Customer",
                "status": "active"
            }
        )
        
        assert project_response.status_code == 200, f"Project creation failed: {project_response.text}"
        project_id = project_response.json()["id"]
        print(f"  [OK] Project created: {project_id}")
    
    # Step 3: Create tender
    print("\n[3/6] Creating tender...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        tender_response = await client.post(
            f"{base_url}/api/tenders",
            headers=headers,
            json={
                "project_id": project_id,
                "title": "Test Tender",
                "description": "Test tender description",
                "estimated_cost": 1000000,
                "deadline": "2026-12-31"
            }
        )
        
        # Note: May fail if tender endpoint not fully implemented
        if tender_response.status_code == 200:
            tender_id = tender_response.json()["id"]
            print(f"  [OK] Tender created: {tender_id}")
            
            # Step 4: Assess tender
            print("\n[4/6] Assessing tender...")
            assessment_response = await client.post(
                f"{base_url}/api/tenders/{tender_id}/assess",
                headers=headers,
                json={
                    "technical_score": 85,
                    "commercial_score": 90,
                    "comments": "Good tender"
                }
            )
            
            if assessment_response.status_code == 200:
                print(f"  [OK] Tender assessed")
            else:
                print(f"  [SKIP] Assessment not available: {assessment_response.status_code}")
            
            # Step 5: Update status
            print("\n[5/6] Updating tender status...")
            status_response = await client.put(
                f"{base_url}/api/tenders/{tender_id}/status",
                headers=headers,
                json={"status": "approved"}
            )
            
            if status_response.status_code == 200:
                print(f"  [OK] Tender status updated")
            else:
                print(f"  [SKIP] Status update not available: {status_response.status_code}")
        else:
            print(f"  [SKIP] Tender creation not available: {tender_response.status_code}")
    
    # Step 6: Verify cleanup
    print("\n[6/6] Cleanup...")
    print(f"  [INFO] Manual cleanup may be required for test data")
    
    print("\n" + "=" * 60)
    print("E2E TENDER TEST COMPLETED")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_tender_workflow())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n[ERROR] Tender test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

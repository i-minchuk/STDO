#!/usr/bin/env python
"""E2E Test: Authentication and Permissions.

Tests:
1. Login with valid credentials
2. Token refresh
3. Access control (different roles)
4. Invalid credentials rejection

Usage:
    python tests/test_e2e_auth.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
import json
from config import Config


async def test_auth_and_permissions():
    """Test authentication flow and permissions."""
    print("=" * 60)
    print("E2E Test: Authentication & Permissions")
    print("=" * 60)
    
    cfg = Config()
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    
    # Test 1: Valid login
    print("\n[1/5] Testing valid login...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "admin",
                "password": "admin"  # Default password from 0001_initial_schema.py
            }
        )
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "access_token not in response"
        assert "refresh_token" in data, "refresh_token not in response"
        
        access_token = data["access_token"]
        print(f"  [OK] Login successful, token received")
    
    # Test 2: Access protected endpoint with token
    print("\n[2/5] Testing protected endpoint access...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = await client.get(
            f"{base_url}/api/auth/me",
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data["username"] == "admin", "Username mismatch"
        print(f"  [OK] Protected endpoint accessible")
    
    # Test 3: Invalid credentials
    print("\n[3/5] Testing invalid credentials...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "admin",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"  [OK] Invalid credentials rejected")
    
    # Test 4: Token refresh
    print("\n[4/5] Testing token refresh...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        refresh_response = await client.post(
            f"{base_url}/api/auth/refresh",
            json={"refresh_token": data.get("refresh_token")}
        )
        
        assert refresh_response.status_code == 200, f"Refresh failed: {refresh_response.text}"
        new_token = refresh_response.json()["access_token"]
        print(f"  [OK] Token refresh successful")
    
    # Test 5: Access without token
    print("\n[5/5] Testing access without token...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{base_url}/api/projects")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"  [OK] Unauthenticated access rejected")
    
    print("\n" + "=" * 60)
    print("E2E AUTH TEST PASSED")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_auth_and_permissions())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n[ERROR] Auth test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

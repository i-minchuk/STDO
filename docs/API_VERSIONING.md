# API Versioning Strategy

## Overview

DokPotok IRIS uses URI path versioning to maintain backward compatibility while allowing breaking changes.

**Current Version**: v1 (stable)
**Deprecated Versions**: None
**Sunset Versions**: None

## Versioning Scheme

```
/api/v{version}/{resource}
```

Examples:
- `/api/v1/projects`
- `/api/v1/documents`
- `/api/v1/auth/login`

## Migration Guide

### For API Consumers

#### Including Version in Requests

```bash
# Always include version in URL
curl http://localhost:8000/api/v1/projects

# With authentication
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/projects
```

#### Handling Deprecation

When an endpoint is deprecated, you'll receive:

```http
HTTP/1.1 200 OK
X-API-Version: 1
X-Deprecated-Versions: v1
X-Sunset-Dates: v1: 2026-12-31
Deprecation: true
Sunset: Sat, 31 Dec 2026 23:59:59 GMT
```

**Action Required**: Migrate to new version before sunset date.

### For Developers

#### Creating Versioned Endpoints

```python
from fastapi import APIRouter
from api.v1 import router as v1_router

# All routes in this file are v1 by default
@v1_router.get("/projects")
async def list_projects():
    ...

# For v2 (future)
from api.v1 import versioned_route

@versioned_route("2")
@router.get("/projects")
async def list_projects_v2():
    ...
```

#### Breaking Changes Protocol

When introducing breaking changes:

1. **Create new version** (`/api/v2/...`)
2. **Mark old version as deprecated** (add headers)
3. **Announce deprecation** (email, docs, changelog)
4. **Wait 6 months** before sunset
5. **Remove old version** after sunset date

#### Common Breaking Changes

| Change | Action |
|--------|--------|
| Remove endpoint | Deprecate → Create replacement → Sunset |
| Change response format | Add new field → Deprecate old field → Remove |
| Change request format | Accept both → Deprecate old format → Require new |
| Change authentication | Support both → Deprecate old → Require new |

## Version Support Policy

| Version | Status | Support Ends |
|---------|--------|--------------|
| v1 | Current | TBD |
| v0 | Deprecated | 2025-12-31 |

### Support Timeline

- **Current**: Fully supported, bug fixes, security patches
- **Deprecated**: Security fixes only, migration guide provided
- **Sunset**: No support, returns 410 Gone

## Response Headers

| Header | Description |
|--------|-------------|
| `X-API-Version` | Current API version |
| `X-Deprecated-Versions` | Comma-separated deprecated versions |
| `X-Sunset-Dates` | Sunset dates for deprecated versions |
| `Deprecation` | `true` if endpoint is deprecated |
| `Sunset` | RFC 1123 date when endpoint will be removed |

## Example Migration

### v1 → v2 (Hypothetical)

#### v1 Response (Deprecated)
```json
{
  "id": 1,
  "name": "Project",
  "status": "active"
}
```

#### v2 Response (New)
```json
{
  "data": {
    "id": "proj_123",
    "attributes": {
      "name": "Project",
      "status": "active",
      "created_at": "2026-01-01T00:00:00Z"
    }
  }
}
```

#### Migration Steps

1. Update client to use `/api/v2/projects`
2. Parse new response format
3. Handle new ID format (int → string)
4. Test thoroughly
5. Remove v1 code after sunset

## Testing Versioning

### Unit Tests

```python
def test_v1_endpoint(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert "X-API-Version" in response.headers
    assert response.headers["X-API-Version"] == "1"

def test_deprecated_headers(client):
    response = client.get("/api/v0/legacy")
    assert response.headers.get("Deprecation") == "true"
    assert "Sunset" in response.headers
```

### Integration Tests

```python
def test_version_negotiation(client):
    # Test that wrong version returns 404
    response = client.get("/api/v999/projects")
    assert response.status_code == 404
```

## Rollback Strategy

If a new version has critical issues:

1. **Immediately deprecate** new version
2. **Reinforce old version** (remove deprecation)
3. **Hotfix** the new version
4. **Communicate** with users

## Best Practices

1. **Never break backwards compatibility** without versioning
2. **Document all changes** in changelog
3. **Provide migration guides** for breaking changes
4. **Test both old and new versions** during transition
5. **Monitor usage** of deprecated endpoints
6. **Communicate early** about upcoming deprecations

## Tools & Utilities

### Version Detection Middleware

```python
from fastapi import Request, Response

async def version_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Add version headers to all responses
    if request.url.path.startswith("/api/"):
        response.headers["X-API-Version"] = "1"
    
    return response
```

### Client SDK Example

```python
class IRISClient:
    def __init__(self, base_url: str, version: str = "1"):
        self.base_url = f"{base_url}/api/v{version}"
        self.session = requests.Session()
    
    def get_projects(self):
        response = self.session.get(f"{self.base_url}/projects")
        
        # Check for deprecation warnings
        if response.headers.get("Deprecation") == "true":
            print(f"Warning: This API version will be sunset on {response.headers.get('Sunset')}")
        
        return response.json()
```

## Support & Feedback

For API versioning questions or issues:
- Open an issue on GitHub
- Contact development team
- Check API documentation at `/docs`

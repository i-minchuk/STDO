# API Layer

FastAPI route handlers for DokPotok IRIS.

## Overview

API layer provides HTTP endpoints for the application. It handles:
- Request validation (Pydantic)
- Authentication and authorization
- Rate limiting
- Error handling
- Response formatting

## Architecture

```
┌─────────────────┐
│   Client        │  ← Browser, mobile, CLI
└────────┬────────┘
         │ HTTP
┌────────▼────────┐
│   API Routers   │  ← FastAPI endpoints
└────────┬────────┘
         │ calls
┌────────▼────────┐
│   Services      │  ← Business logic
└─────────────────┘
```

## Routers

### Authentication

**File**: `auth_api.py`

**Endpoints**:
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

**Auth Flow**:
```
1. POST /api/auth/login → access_token + refresh_token
2. Include token: Authorization: Bearer <token>
3. Refresh when expired: POST /api/auth/refresh
```

### Projects

**File**: `project_api.py`

**Endpoints**:
- `GET /api/projects` - List projects (paginated)
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}/status` - Update status
- `GET /api/projects/portfolio/today` - Portfolio overview

### Documents

**File**: `document_api.py`

**Endpoints**:
- `GET /api/documents` - List documents
- `POST /api/documents` - Create document
- `GET /api/documents/{id}` - Get document
- `POST /api/documents/{id}/file` - Upload file
- `GET /api/documents/{id}/revisions` - List revisions

### Revisions

**File**: `revision_api.py`

**Endpoints**:
- `POST /api/documents/{id}/revisions` - Create revision
- `POST /api/revisions/{id}/approve` - Approve revision

### Tasks

**File**: `task_api.py`

**Endpoints**:
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}/progress` - Update progress
- `POST /api/tasks/calculate-cpm` - Recalculate CPM

### Gamification

**File**: `gamification_api.py`

**Endpoints**:
- `GET /api/gamification/leaderboard` - Top users
- `GET /api/gamification/me` - Current user profile
- `GET /api/gamification/badges` - Available badges
- `GET /api/gamification/daily-quests` - Daily quests
- `GET /api/gamification/notifications` - Notifications
- `GET /api/gamification/notifications/unread-count` - Unread count

### Health & Monitoring

**File**: `health_api.py`

**Endpoints**:
- `GET /api/health` - Basic health check
- `GET /api/health/db` - Database connectivity
- `GET /api/health/cache` - Cache (Redis) status
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/metrics` - Application metrics

### Tenders

**File**: `tender_api.py`

**Endpoints**:
- `GET /api/tenders` - List tenders
- `POST /api/tenders` - Create tender
- `POST /api/tenders/{id}/assess` - Assess tender
- `PUT /api/tenders/{id}/status` - Update status

### Remarks

**File**: `remarks_api.py`

**Endpoints**:
- `GET /api/remarks` - List remarks
- `POST /api/remarks` - Create remark
- `PUT /api/remarks/{id}/resolve` - Resolve remark
- `POST /api/remarks/{id}/responses` - Add response

## Authentication

All endpoints except `/api/auth/*` require authentication:

```python
from core.auth import get_current_user

@router.get("/projects")
def list_projects(current_user: User = Depends(get_current_user)):
    # current_user is validated and injected
    ...
```

## Rate Limiting

Rate limiting is applied via `slowapi`:

```python
from core.rate_limiter import limiter

@router.post("/tenders/assess")
@limiter.limit("10/minute")
async def assess_tender(request: Request, ...):
    # Limited to 10 requests per minute
    ...
```

## Error Handling

Errors follow standard format:

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "errors": [...]
  }
}
```

## OpenAPI Documentation

FastAPI auto-generates documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Best Practices

1. **Validate early**: Use Pydantic models for request/response
2. **Keep handlers thin**: Delegate to services
3. **Use dependencies**: Inject auth, rate limits, etc.
4. **Document endpoints**: Add summary and description
5. **Handle errors gracefully**: Return meaningful error messages

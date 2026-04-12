# ДокПоток IRIS API Documentation

## Overview

This is the API documentation for the DokPotok IRIS system. The API follows REST principles and uses JSON for requests/responses.

**Base URL**: `http://localhost:8000`

**Authentication**: Bearer token (JWT)

## Authentication

All API endpoints (except `/health` and `/api/auth/*`) require authentication via Bearer token.

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "role": "admin",
  "is_active": true
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Refresh Token

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

## Projects API

### List Projects

```http
GET /api/projects?limit=20&offset=0
Authorization: Bearer <token>
```

**Query Parameters**:
- `limit` (int, default=20, max=1000): Number of items per page
- `offset` (int, default=0): Pagination offset

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "code": "PRJ-2026-001",
      "name": "Project Name",
      "status": "active"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

### Create Project from Tender

```http
POST /api/projects/create-from-tender
Authorization: Bearer <token>
Content-Type: application/json

{
  "tender_name": "Engineering Project",
  "customer": "Customer Name",
  "deadline_date": "2026-12-31",
  "documents": [
    {
      "doc_type": "VDR",
      "count": 10,
      "hours_per_doc": 8.0,
      "discipline": "Engineering"
    }
  ],
  "team_size": 5,
  "vdr_required": true,
  "otk_required": false,
  "logistics_complexity": "normal"
}
```

**Response**:
```json
{
  "project": {
    "id": 1,
    "code": "PRJ-2026-001",
    "name": "Engineering Project",
    "status": "planned"
  },
  "tasks_created": 12,
  "message": "Проект создан из тендера. Задачи запланированы."
}
```

## Documents API

### List Documents

```http
GET /api/documents?project_id=1&status=in_work&search=keyword&limit=20&offset=0
Authorization: Bearer <token>
```

**Query Parameters**:
- `project_id` (int, optional): Filter by project
- `status` (string, optional): Filter by status (in_work, on_review, approved, archived)
- `search` (string, optional): Search in document code/title
- `limit` (int, default=20, max=1000): Page size
- `offset` (int, default=0): Pagination offset

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "code": "DOC-001",
      "title": "Technical Specification",
      "project_id": 1,
      "status": "in_work",
      "discipline": "Engineering",
      "current_revision_id": 5
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

### Get Document Details

```http
GET /api/documents/{doc_id}
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "code": "DOC-001",
  "title": "Technical Specification",
  "project_id": 1,
  "status": "in_work",
  "discipline": "Engineering",
  "current_revision_id": 5,
  "revisions": [
    {
      "id": 5,
      "revision_index": 1,
      "revision_letter": "A",
      "status": "draft",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

## Gamification API

### Get Leaderboard

```http
GET /api/gamification/leaderboard
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "rank": 1,
    "user_id": 5,
    "username": "engineer1",
    "full_name": "John Doe",
    "score": 1500,
    "level": 5,
    "level_title": "Expert",
    "badges_count": 3,
    "badges": [
      {"id": "first_doc", "name": "First Document"}
    ]
  }
]
```

### Get My Profile

```http
GET /api/gamification/me
Authorization: Bearer <token>
```

**Response**:
```json
{
  "user_id": 1,
  "username": "admin",
  "full_name": "Admin User",
  "score": 500,
  "level": 2,
  "level_title": "Beginner",
  "badges": [],
  "next_level_at": 1000,
  "recent_events": [
    {
      "event_type": "task_completed",
      "points_delta": 50,
      "created_at": "2026-01-15T10:30:00Z",
      "comment": "Задача выполнена"
    }
  ]
}
```

### Get Daily Quests

```http
GET /api/gamification/daily-quests
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "id": 1,
    "quest_type": "tasks_completed",
    "title": "Daily Tasks",
    "description": "Complete 3 tasks today",
    "target_count": 3,
    "current_count": 1,
    "reward_points": 100,
    "reward_xp": 50,
    "is_completed": false,
    "completed_at": null
  }
]
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Login endpoint**: 5 requests per minute per IP

If rate limited, you'll receive a `429 Too Many Requests` response.

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## OpenAPI/Swagger

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Versioning

Current API version: **0.3.0**

Version is included in the response headers and `/health` endpoint.

## Support

For issues or questions, please contact the development team.

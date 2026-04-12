# DokPotok IRIS API Reference

**Version**: 0.3.0  
**Last Updated**: 2026-01-22

---

## Overview

DokPotok IRIS — система управления инженерной документацией с планированием по методу CPM.

**Base URL**: `http://localhost:8000`

**API Documentation**:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

---

## Authentication

All endpoints except `/api/auth/login` and `/api/auth/refresh` require authentication.

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "ivan.petrov",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Using Tokens

Include access token in Authorization header:
```http
Authorization: Bearer <access_token>
```

---

## Health & Monitoring

### Health Check

```http
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-22T10:30:00+00:00",
  "service": "DokPotok IRIS",
  "version": "0.1.0"
}
```

### Database Health

```http
GET /api/health/db
```

**Response**:
```json
{
  "status": "healthy",
  "database": "PostgreSQL",
  "query_time_ms": 0.5,
  "timestamp": "2026-01-22T10:30:00+00:00"
}
```

### Cache Health

```http
GET /api/health/cache
```

**Response**:
```json
{
  "status": "healthy",
  "cache_type": "Redis",
  "connected": true,
  "timestamp": "2026-01-22T10:30:00+00:00"
}
```

### Readiness Check

```http
GET /api/health/ready
```

**Response**:
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "cache": true
  },
  "timestamp": "2026-01-22T10:30:00+00:00"
}
```

### Application Metrics

```http
GET /api/health/metrics
```

**Response**:
```json
{
  "timestamp": "2026-01-22T10:30:00+00:00",
  "application": {
    "status": "healthy",
    "version": "0.1.0"
  },
  "python": {
    "version": "3.12.7",
    "implementation": "cpython"
  },
  "process": {
    "memory_mb": 125.5,
    "cpu_percent": 5.2,
    "threads": 12
  }
}
```

---

## Projects

### List Projects

```http
GET /api/projects?limit=20&offset=0&status=active
Authorization: Bearer <token>
```

**Response**:
```json
{
  "projects": [...],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

### Get Project

```http
GET /api/projects/{project_id}
Authorization: Bearer <token>
```

### Create Project

```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "PRJ-002",
  "name": "New Project",
  "customer": "Acme Corp",
  "start_date": "2026-02-01",
  "end_date_planned": "2026-12-31"
}
```

### Update Project Status

```http
PUT /api/projects/{project_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "completed",
  "end_date_actual": "2026-11-15"
}
```

### Portfolio Overview

```http
GET /api/projects/portfolio/today?target_date=2026-01-22
Authorization: Bearer <token>
```

**Response**:
```json
{
  "date": "2026-01-22",
  "portfolio_summary": {
    "projects_total": 10,
    "projects_at_risk": 2,
    "avg_spi": 0.85,
    "avg_cpi": 0.92
  },
  "projects": [...]
}
```

---

## Documents

### List Documents

```http
GET /api/documents?project_id=1&limit=20&status=in_work
Authorization: Bearer <token>
```

### Get Document

```http
GET /api/documents/{document_id}
Authorization: Bearer <token>
```

### Create Document

```http
POST /api/documents
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 1,
  "code": "DOC-001",
  "title": "Technical Specification",
  "discipline": "Electrical"
}
```

### Upload Document File

```http
POST /api/documents/{document_id}/file
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
```

---

## Revisions

### List Revisions

```http
GET /api/documents/{document_id}/revisions
Authorization: Bearer <token>
```

### Create Revision

```http
POST /api/documents/{document_id}/revisions
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
is_major: true
```

**Response**:
```json
{
  "id": 1,
  "document_id": 1,
  "revision_index": "A01",
  "revision_letter": "A",
  "revision_number": 1,
  "version_number": 1,
  "status": "draft",
  "file_path": "/storage/PRJ001/DOC001/v0001_test.pdf"
}
```

### Approve Revision

```http
POST /api/revisions/{revision_id}/approve
Authorization: Bearer <token>
```

---

## Tasks

### List Tasks

```http
GET /api/tasks?project_id=1&status=not_started
Authorization: Bearer <token>
```

### Create Task

```http
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 1,
  "name": "Design circuit diagram",
  "task_type": "engineering",
  "assigned_to": 5,
  "duration_days_planned": 5,
  "work_hours_planned": 40.0,
  "start_date_planned": "2026-02-01",
  "end_date_planned": "2026-02-07"
}
```

### Update Task Progress

```http
PUT /api/tasks/{task_id}/progress
Authorization: Bearer <token>
Content-Type: application/json

{
  "percent_complete": 50,
  "status": "in_progress"
}
```

### Recalculate CPM

```http
POST /api/tasks/calculate-cpm
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 1
}
```

---

## Gamification

### Leaderboard

```http
GET /api/gamification/leaderboard?limit=50
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "user_id": 5,
    "username": "ivan.petrov",
    "full_name": "Иван Петров",
    "score": 1250,
    "level": 4,
    "level_title": "Эксперт",
    "badges_count": 8,
    "rank": 1
  }
]
```

### My Profile

```http
GET /api/gamification/me
Authorization: Bearer <token>
```

### Available Badges

```http
GET /api/gamification/badges
Authorization: Bearer <token>
```

### Daily Quests

```http
GET /api/gamification/daily-quests
Authorization: Bearer <token>
```

### Update Quest Progress

```http
POST /api/gamification/daily-quests/{quest_type}/progress
Authorization: Bearer <token>
```

### Notifications

```http
GET /api/gamification/notifications
Authorization: Bearer <token>
```

### Mark Notification Read

```http
PUT /api/gamification/notifications/{notification_id}/read
Authorization: Bearer <token>
```

### Unread Count

```http
GET /api/gamification/notifications/unread-count
Authorization: Bearer <token>
```

---

## Tenders

### List Tenders

```http
GET /api/tenders?limit=20&status=pending
Authorization: Bearer <token>
```

### Get Tender

```http
GET /api/tenders/{tender_id}
Authorization: Bearer <token>
```

### Create Tender

```http
POST /api/tenders
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Project X Documentation",
  "customer": "Acme Corp",
  "deadline": "2026-03-01",
  "documents_count": 50
}
```

### Assess Tender

```http
POST /api/tenders/{tender_id}/assess
Authorization: Bearer <token>
Content-Type: application/json

{
  "decision": "GO",
  "feasibility_pct": 85,
  "comments": "Feasible with current team"
}
```

---

## Remarks

### List Project Remarks

```http
GET /api/remarks?project_id=1&status=open
Authorization: Bearer <token>
```

### Create Remark

```http
POST /api/remarks
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 1,
  "text": "Не соответствует ГОСТ 2.105-95",
  "author_id": 3,
  "revision_id": 5
}
```

### Resolve Remark

```http
PUT /api/remarks/{remark_id}/resolve
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "resolved",
  "resolution_comment": "Исправлено в ревизии B02"
}
```

### Add Response

```http
POST /api/remarks/{remark_id}/responses
Authorization: Bearer <token>
Content-Type: application/json

{
  "author_id": 5,
  "text": "Согласен, исправим"
}
```

---

## Work Schedule

### Get Default Schedule

```http
GET /api/work-schedule/default
Authorization: Bearer <token>
```

### List Schedules

```http
GET /api/work-schedule
Authorization: Bearer <token>
```

### Create Schedule

```http
POST /api/work-schedule
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Shift Schedule",
  "work_days": [0, 1, 2, 3, 4, 5],  // Sat-Fri
  "work_hours_start": "08:00",
  "work_hours_end": "16:00",
  "is_default": false
}
```

---

## Heatmap

### Weekly Heatmap

```http
GET /api/heatmap/weekly?user_id=5&year=2026&week=3
Authorization: Bearer <token>
```

**Response**:
```json
{
  "2026-W03": {
    "Mon": 8.0,
    "Tue": 6.5,
    "Wed": 7.0,
    "Thu": 8.0,
    "Fri": 4.0,
    "Sat": 0.0,
    "Sun": 0.0
  }
}
```

### Monthly Heatmap

```http
GET /api/heatmap/monthly?user_id=5&year=2026&month=1
Authorization: Bearer <token>
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limiting

API is rate limited to prevent abuse.

**Default limits**:
- Login: 5 requests per minute
- General API: 100 requests per minute

Exceeding limits returns `429 Too Many Requests`.

---

## Versioning

API versioning is handled via URL path:

- `/api/v1/...` - Current stable version
- `/api/...` - Default (current version)

Deprecated versions are supported for 6 months with migration guides.

---

## Support

- **Documentation**: `/docs`
- **Issues**: GitHub Issues (if open source)
- **Email**: support@example.com

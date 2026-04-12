# Core Module

Core utilities and infrastructure for DokPotok IRIS.

## Overview

The `core` module contains shared utilities, infrastructure components, and cross-cutting concerns used throughout the application.

## Components

### Authentication

**File**: `auth.py`

**Purpose**: JWT token-based authentication.

**Features**:
- Access token generation and validation
- Refresh token rotation
- Password hashing with bcrypt
- Role-based authorization

**Usage**:
```python
from core.auth import create_access_token, verify_token

# Generate token
token = create_access_token(user_id=1, username="john.doe")

# Validate token
payload = verify_token(token)
user_id = payload["sub"]
```

### Authorization

**File**: `authorization.py`

**Purpose**: Role-based access control (RBAC).

**Roles**:
- `admin` - Full access
- `manager` - Project management
- `engineer` - Document and task work

**Usage**:
```python
from core.auth import require_role

@router.post("/projects")
@require_role(["admin", "manager"])
def create_project(...):
    # Only admin or manager can create projects
    ...
```

### Caching

**File**: `cache.py`

**Purpose**: Redis-based caching with in-memory fallback.

**Features**:
- Redis backend
- In-memory fallback (if Redis unavailable)
- TTL support
- Pattern-based invalidation
- Decorator for automatic caching

**Usage**:
```python
from core.cache import cached, cache_delete_pattern

# Manual cache
from core.cache import cache_get, cache_set
cache_set("key", value, ttl=300)
value = cache_get("key")

# Decorator
@cached(ttl=300, key_prefix="portfolio")
def get_portfolio_today(target_date):
    # Automatically cached
    ...

# Invalidation
cache_delete_pattern("cache:portfolio:*")
```

### Rate Limiting

**File**: `rate_limiter.py`

**Purpose**: Prevent abuse and DOS attacks.

**Configuration**:
```python
from slowapi import Limiter
from core.rate_limiter import limiter

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
    # Limited to 5 attempts per minute
    ...
```

**Limits**:
- Login: 5/minute
- General API: 100/minute

### DateTime Utilities

**File**: `datetime_utils.py`

**Purpose**: Timezone-aware datetime handling.

**Features**:
- UTC timezone enforcement
- ISO format utilities
- Timezone conversion

**Usage**:
```python
from core.datetime_utils import utc_now, format_iso

now = utc_now()  # timezone-aware UTC
iso = format_iso(now)  # "2026-01-22T10:30:00+00:00"
```

### Service Locator

**File**: `service_locator.py`

**Purpose**: Dependency injection container.

**Usage**:
```python
from core.service_locator import get_locator

locator = get_locator()
workflow = locator.document_workflow
dashboard = locator.project_dashboard
```

**Services Available**:
- `auth_service`
- `revision_service`
- `document_service`
- `document_workflow`
- `project_dashboard`
- `cpm_scheduler`
- `time_calculation`
- `heatmap_service`
- `storage`

### Exception Handling

**File**: `exceptions.py` (planned)

**Purpose**: Custom exceptions (not yet implemented).

**Planned**:
- `BusinessError` - Business logic violations
- `ValidationError` - Input validation failures
- `NotFoundError` - Resource not found
- `AuthenticationError` - Auth failures

## Best Practices

1. **UTC everywhere**: Always use UTC for timestamps
2. **Explicit dependencies**: Use service locator, not globals
3. **Cache wisely**: Only cache expensive, infrequently-changing data
4. **Rate limit sensitive endpoints**: Login, password reset, etc.
5. **Use decorators**: Prefer `@cached`, `@require_role` over manual checks

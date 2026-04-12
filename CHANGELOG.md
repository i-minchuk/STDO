# Changelog

All notable changes to DokPotok IRIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- E2E tests with Playwright for critical user journeys
- Performance testing with Locust
- Codecov integration for test coverage reports
- Sentry error monitoring (optional)
- API documentation with Swagger/OpenAPI
- Comprehensive developer setup guide
- Dependabot configuration for automated updates
- Pre-commit hooks for code quality

### Changed
- Updated CI/CD pipeline with security scanning
- Improved rate limiting configuration
- Enhanced error handling in main.py
- Updated pre-commit hooks with latest versions

### Fixed
- SQL injection vulnerability in base_repository order_by
- Missing rate limiter import in auth_api
- CPM scheduler error handling (ValueError → HTTPException)
- Login endpoint now properly rate limited

### Security
- Added file upload validation (extension check)
- Implemented SECRET_KEY validation with warnings
- Added Trivy security scanning in CI
- Safety package checks for Python dependencies

## [0.3.0] - 2026-01-15

### Added
- Gamification system with badges and daily quests
- Work schedule repository and time calculation service
- Tender management API
- Document validation with PyMuPDF
- Heatmap service for activity visualization
- Report generation service (Excel export)
- Workload management API
- Admin API for user management
- Notification system
- Combo achievements and streaks

### Changed
- Migrated to psycopg 3 for database connections
- Improved CPM algorithm with cycle detection
- Enhanced document workflow with revision tracking
- Updated authentication with JWT refresh tokens

### Fixed
- Recursion bug in project_repository.list_all()
- Datetime timezone handling in fixtures
- PlannedTask model fields
- Tender repository mocks in tests

## [0.2.0] - 2025-12-01

### Added
- Critical Path Method (CPM) scheduler
- Project dashboard with metrics
- Time logging system
- Document workflow automation
- Revision management
- Document service and validator

### Changed
- Refactored service locator pattern
- Improved repository base class
- Enhanced DTO structure

### Fixed
- Database connection pool configuration
- Transaction handling in services

## [0.1.0] - 2025-11-01

### Added
- Initial project structure
- User authentication system
- Project and document management
- Basic API endpoints
- Database migrations with Alembic
- Docker configuration
- Frontend with React + Vite

### Security
- Password hashing with bcrypt
- JWT token authentication
- CORS configuration

---

## How to Use This Changelog

### For Users
- Check "Added" for new features
- Check "Changed" for breaking changes
- Check "Fixed" for bug fixes
- Check "Security" for security patches

### For Developers
- Follow [Keep a Changelog](https://keepachangelog.com/) format
- Group changes by type: Added, Changed, Deprecated, Removed, Fixed, Security
- Reference issue/PR numbers where applicable
- Use semantic versioning for version numbers

### Automatic Changelog Generation

To generate changelog from git commits:

```bash
# Install conventional-changelog
npm install -g conventional-changelog-cli

# Generate changelog
conventional-changelog -p angular -i CHANGELOG.md -s

# Preview changes
conventional-changelog -p angular -p
```

### Commit Message Format

Use conventional commits for automatic changelog generation:

```
feat: add new feature          → Added
fix: fix bug                   → Fixed
docs: update documentation     → Changed
refactor: code restructuring   → Changed
test: add tests                → Added
chore: maintenance             → Changed
security: fix vulnerability    → Security
```

Examples:
```
feat(auth): add password reset functionality
fix(api): resolve pagination bug in documents endpoint
security(dependencies): update bcrypt to 4.0.1
docs: add API documentation for projects endpoint
```

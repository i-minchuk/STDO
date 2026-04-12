# Developer Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- npm or yarn

## Quick Start

### 1. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Optional: for development tools

# Copy environment file
cp .env.example .env

# Update .env with your database credentials
# DB_DSN=postgresql://user:password@localhost:5432/iris

# Run database migrations
python -m db.migrations_runner

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Development Tools

### Pre-commit Hooks

Pre-commit hooks ensure code quality before commits.

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Skip hooks for a single commit
git commit --no-verify -m "WIP"
```

**Available hooks**:
- `black` - Code formatting
- `ruff` - Linting and auto-fixes
- `pyupgrade` - Modernize Python syntax
- `pytest` - Run unit tests (optional)
- File checks (trailing whitespace, EOF newline, etc.)

### Running Tests

```bash
# All unit tests (default)
python -m pytest tests/ --ignore=tests/test_api.py --ignore=tests/test_integration.py

# Include integration tests (requires PostgreSQL)
python -m pytest tests/ -m integration

# E2E tests (requires running server)
python -m pytest tests/test_e2e.py -m e2e

# With coverage
python -m pytest tests/ --cov=services --cov=repositories --cov=api --cov-report=html

# Specific test file
python -m pytest tests/test_cpm_scheduler_service.py -v
```

### Linting

```bash
# Ruff (fast linter)
ruff check .
ruff check . --fix

# Black (code formatter)
black .
black --check .

# Combined (via pre-commit)
pre-commit run --all-files
```

## CI/CD Pipeline

The project uses GitHub Actions for CI/CD.

### Workflow Triggers

- **Push to main/develop**: Full pipeline runs
- **Pull Request**: Lint + unit tests + security scan

### Pipeline Stages

1. **Lint** - Code quality checks
2. **Test** - Unit tests with coverage
3. **Security Scan** - Trivy + Safety
4. **Docker Build** - Build container image
5. **Integration Tests** - DB integration tests

### Viewing CI Results

- GitHub Actions tab in repository
- Coverage reports via Codecov
- Security scan results in Security tab

## Sentry Integration (Optional)

For error monitoring and performance tracking:

```bash
# Install Sentry
pip install sentry-sdk[fastapi]

# Add to .env
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
```

Sentry will automatically:
- Capture unhandled exceptions
- Track performance metrics
- Provide error context and stack traces
- Send alerts for critical errors

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Common Development Tasks

### Add New API Endpoint

1. Create endpoint in `api/your_api.py` or new file
2. Add router to `main.py`
3. Update DTOs in `dto/` if needed
4. Add tests in `tests/`
5. Update API documentation

### Add New Service

1. Create `services/your_service.py`
2. Add to `core/service_locator.py`
3. Inject via ServiceLocator in API
4. Add unit tests

### Add New Repository

1. Create `repositories/your_repository.py`
2. Add to `core/service_locator.py`
3. Use BaseRepository pattern if applicable
4. Add tests with mocked DB

### Database Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
python -m db.migrations_runner
# or
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
python -c "import psycopg; print(psycopg.connect('postgresql://...'))"
```

### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Kill process
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Linux/Mac
```

### Frontend Build Issues

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Configure proper `DB_DSN` with production credentials
- [ ] Enable HTTPS/TLS
- [ ] Set up rate limiting (already configured)
- [ ] Configure CORS for specific origins
- [ ] Set up Sentry for error monitoring
- [ ] Run security scans: `safety check -r requirements.txt`
- [ ] Review and restrict file upload types
- [ ] Enable database connection pooling in production

## Performance Tips

- Use connection pooling (configured: min=2, max=10)
- Enable gzip compression in production
- Use CDN for static frontend assets
- Implement caching for frequently accessed data
- Monitor database query performance
- Use async operations where possible

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example**:
```
feat(auth): add password reset functionality

Implement password reset via email with token expiration

Closes #123
```

## Support

For questions or issues:
- Check existing issues and documentation
- Contact development team
- Review API documentation at `/docs`

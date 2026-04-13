"""Rate limiting configuration for API."""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter configuration: 100 requests per minute per IP (default)
# Note: FastAPI app must be passed via app.state.limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"], storage_uri="memory://")

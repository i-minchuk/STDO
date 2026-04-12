"""Rate limiting configuration for API."""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter configuration: 100 requests per minute per IP (default)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

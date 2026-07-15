"""
HTTP middleware for Project DNA:
- TimeoutMiddleware:    Returns 503 if a request takes longer than ANALYSIS_TIMEOUT_SECONDS.
- RateLimitMiddleware:  Returns 429 if a client IP exceeds RATE_LIMIT requests per minute.

The timeout only applies to routes that perform analysis (configurable via
TIMED_ROUTES set). All other routes pass through unconditionally.
"""
import time
import asyncio
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

ANALYSIS_TIMEOUT_SECONDS = 120
RATE_LIMIT_PER_MINUTE = 10
TIMED_ROUTES = {"/analyze", "/v1/analyze"}


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Abort slow analysis requests after ANALYSIS_TIMEOUT_SECONDS seconds.

    Uses asyncio.wait_for to actually enforce the timeout around the wrapped
    call_next coroutine. Previously this branch had no awaitable timeout and
    effectively never aborted a hung analysis.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in TIMED_ROUTES and request.method == "POST":
            try:
                return await asyncio.wait_for(
                    call_next(request), timeout=ANALYSIS_TIMEOUT_SECONDS
                )
            except asyncio.TimeoutError:
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": f"Analysis timed out after {ANALYSIS_TIMEOUT_SECONDS}s. "
                                  "The repository may be too large."
                    },
                )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Allow at most RATE_LIMIT_PER_MINUTE requests per client IP per 60-second window."""

    def __init__(self, app, limit: int = RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self._limit = limit
        self._windows: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        from dna.config import get_config
        if not get_config().network_mode:
            return await call_next(request)

        ip = self._get_client_ip(request)
        now = time.monotonic()
        window_start = now - 60.0

        # Evict timestamps outside the 60-second window
        timestamps = self._windows[ip]
        self._windows[ip] = [t for t in timestamps if t >= window_start]

        if len(self._windows[ip]) >= self._limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded: max {self._limit} requests per minute."
                },
                headers={"Retry-After": "60"},
            )

        self._windows[ip].append(now)
        return await call_next(request)

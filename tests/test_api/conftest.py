"""
conftest.py for test_api — resets shared state between tests.

The RateLimitMiddleware on the global `app` accumulates request counts
in-memory. This fixture clears that counter before each test so tests
don't bleed into each other.
"""
import pytest
from dna.api.app import app


def _find_rate_limiter():
    """Walk the middleware stack and return the RateLimitMiddleware instance."""
    from dna.api.middleware import RateLimitMiddleware
    # Starlette stores middleware as a stack on app.middleware_stack; however we
    # can reach them through app.middleware (the list stored before build).
    # The safest approach: iterate the router middleware list.
    middleware_obj = app.middleware_stack
    visited = set()
    queue = [middleware_obj]
    while queue:
        obj = queue.pop()
        if id(obj) in visited:
            continue
        visited.add(id(obj))
        if isinstance(obj, RateLimitMiddleware):
            return obj
        # Recurse into .app attribute (Starlette/ASGI chain)
        inner = getattr(obj, "app", None)
        if inner is not None:
            queue.append(inner)
    return None


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear the per-IP request windows before every test in this package."""
    rl = _find_rate_limiter()
    if rl is not None:
        rl._windows.clear()
    yield
    # clean up after test too
    if rl is not None:
        rl._windows.clear()

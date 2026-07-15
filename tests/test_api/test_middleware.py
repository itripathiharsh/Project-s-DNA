"""Tests for TimeoutMiddleware and RateLimitMiddleware."""
import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from dna.api.app import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Rate limit
# ---------------------------------------------------------------------------

def test_rate_limit_under_limit():
    """First RATE_LIMIT requests from the same IP should all succeed."""
    from dna.api.middleware import RateLimitMiddleware, RATE_LIMIT_PER_MINUTE
    with patch("dna.config.get_config") as mock_get_config:
        mock_get_config.return_value.network_mode = True
        responses = [client.get("/health") for _ in range(RATE_LIMIT_PER_MINUTE)]
        assert all(r.status_code == 200 for r in responses)


def test_rate_limit_exceeded():
    """After RATE_LIMIT requests in 60s, the next one should get 429."""
    from dna.api.middleware import RateLimitMiddleware, RATE_LIMIT_PER_MINUTE
    from starlette.applications import Starlette
    from starlette.requests import Request as StarletteRequest
    from starlette.responses import Response
    from starlette.routing import Route
    from starlette.testclient import TestClient as StarletteClient

    async def dummy(request):
        return Response("ok", status_code=200)

    inner_app = Starlette(routes=[Route("/ping", dummy)])
    mw_app = RateLimitMiddleware(inner_app, limit=3)
    sc = StarletteClient(mw_app)

    with patch("dna.config.get_config") as mock_get_config:
        mock_get_config.return_value.network_mode = True
        r1 = sc.get("/ping")
        r2 = sc.get("/ping")
        r3 = sc.get("/ping")
        r4 = sc.get("/ping")  # should be blocked

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 200
        assert r4.status_code == 429
        assert "detail" in r4.json()


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------

def test_timeout_not_triggered_for_normal_routes():
    """Non-analysis routes should not be timed out."""
    # Use a fresh TestClient with a freshly-built app so the rate-limit bucket is empty.
    from fastapi import FastAPI, Depends
    from dna.api.auth import require_auth
    from dna.api.middleware import TimeoutMiddleware, RateLimitMiddleware

    mini_app = FastAPI(dependencies=[Depends(require_auth)])
    mini_app.add_middleware(RateLimitMiddleware)
    mini_app.add_middleware(TimeoutMiddleware)

    @mini_app.get("/health")
    async def health():
        return {"status": "ok"}

    sc = TestClient(mini_app)
    r = sc.get("/health")
    assert r.status_code == 200


def test_timeout_middleware_fast_request():
    """A fast POST to /analyze (which will 400 immediately) should not time out."""
    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.responses import JSONResponse
    from dna.api.auth import require_auth
    from dna.api.middleware import TimeoutMiddleware, RateLimitMiddleware

    mini_app = FastAPI(dependencies=[Depends(require_auth)])
    mini_app.add_middleware(RateLimitMiddleware)
    mini_app.add_middleware(TimeoutMiddleware)

    @mini_app.post("/analyze")
    async def analyze():
        raise HTTPException(status_code=400, detail="does not exist")

    sc = TestClient(mini_app)
    r = sc.post("/analyze", json={})
    assert r.status_code == 400


def test_timeout_middleware_triggers(monkeypatch):
    """Simulate a slow request hitting the timeout."""
    from starlette.applications import Starlette
    from starlette.requests import Request as StarletteRequest
    from starlette.responses import Response
    from starlette.routing import Route
    from starlette.testclient import TestClient as StarletteClient
    import dna.api.middleware

    monkeypatch.setattr(dna.api.middleware, "ANALYSIS_TIMEOUT_SECONDS", 0.1)

    async def slow_handler(request):
        await asyncio.sleep(0.2)
        return Response("done", status_code=200)

    inner_app = Starlette(routes=[Route("/analyze", slow_handler, methods=["POST"])])
    mw_app = dna.api.middleware.TimeoutMiddleware(inner_app)
    sc = StarletteClient(mw_app, raise_server_exceptions=False)

    r = sc.post("/analyze", json={})
    assert r.status_code == 503
    assert "timed out" in r.json()["detail"].lower()

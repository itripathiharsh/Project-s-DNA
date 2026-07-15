"""Tests for API authentication (auth.py)."""
import os
import pytest
from fastapi.testclient import TestClient
from dna.config import reset_config
from dna.api.app import app

client = TestClient(app, raise_server_exceptions=True)


def _reset():
    reset_config()
    # Clean env vars set during tests
    for k in ("DNA_NETWORK_MODE", "DNA_API_KEYS"):
        os.environ.pop(k, None)


# ---------------------------------------------------------------------------
# localhost mode (network_mode=False, default)
# ---------------------------------------------------------------------------

def test_auth_localhost_no_key():
    """In localhost mode, requests without any key must succeed."""
    _reset()
    r = client.get("/health")
    assert r.status_code == 200


def test_auth_localhost_with_key():
    """In localhost mode, a key is accepted (but irrelevant)."""
    _reset()
    r = client.get("/health", headers={"X-API-Key": "any-key"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# network mode — no configured keys
# ---------------------------------------------------------------------------

def test_auth_network_mode_no_keys_configured():
    """Network mode with no keys → 401 for all requests."""
    _reset()
    os.environ["DNA_NETWORK_MODE"] = "true"
    _reset.__wrapped__ = None  # ensure reset picks up env
    reset_config()
    r = client.get("/health")
    assert r.status_code == 401
    _reset()


# ---------------------------------------------------------------------------
# network mode — with configured keys
# ---------------------------------------------------------------------------

def test_auth_network_mode_valid_bearer():
    """Valid Bearer token in network mode → request passes."""
    _reset()
    os.environ["DNA_NETWORK_MODE"] = "true"
    os.environ["DNA_API_KEYS"] = "secret-key-1,secret-key-2"
    reset_config()
    r = client.get("/health", headers={"Authorization": "Bearer secret-key-1"})
    assert r.status_code == 200
    _reset()


def test_auth_network_mode_valid_x_api_key():
    """Valid X-API-Key in network mode → request passes."""
    _reset()
    os.environ["DNA_NETWORK_MODE"] = "true"
    os.environ["DNA_API_KEYS"] = "secret-key-1"
    reset_config()
    r = client.get("/health", headers={"X-API-Key": "secret-key-1"})
    assert r.status_code == 200
    _reset()


def test_auth_network_mode_invalid_key():
    """Wrong key in network mode → 401."""
    _reset()
    os.environ["DNA_NETWORK_MODE"] = "true"
    os.environ["DNA_API_KEYS"] = "secret-key-1"
    reset_config()
    r = client.get("/health", headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 401
    _reset()


def test_auth_network_mode_missing_key():
    """No key header in network mode → 401."""
    _reset()
    os.environ["DNA_NETWORK_MODE"] = "true"
    os.environ["DNA_API_KEYS"] = "secret-key-1"
    reset_config()
    r = client.get("/health")
    assert r.status_code == 401
    _reset()


def test_auth_network_mode_second_key():
    """Any of the configured keys works."""
    _reset()
    os.environ["DNA_NETWORK_MODE"] = "true"
    os.environ["DNA_API_KEYS"] = "key-a,key-b,key-c"
    reset_config()
    r = client.get("/health", headers={"X-API-Key": "key-c"})
    assert r.status_code == 200
    _reset()

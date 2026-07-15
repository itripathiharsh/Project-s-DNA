"""
API key authentication for Project DNA.

Rules:
- In localhost mode (network_mode=False): all requests pass unconditionally.
- In network mode (network_mode=True): requests must carry a valid key in the
  `Authorization: Bearer <key>` header OR the `X-API-Key: <key>` header.
  Requests without a valid key receive HTTP 401.
"""
from fastapi import Request, HTTPException
from dna.config import get_config


def _extract_key(request: Request) -> str | None:
    # Try Authorization: Bearer <key>
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()

    # Try X-API-Key header
    return request.headers.get("X-API-Key", "").strip() or None


def require_auth(request: Request) -> None:
    """Dependency that enforces API-key authentication in network mode."""
    cfg = get_config()
    if not cfg.network_mode:
        return  # localhost / dev mode — no auth required

    # network mode — a valid key must be present
    if not cfg.api_keys:
        # network mode is on but no keys are configured → still block everything
        raise HTTPException(
            status_code=401,
            detail="Network mode is enabled but no API keys are configured. "
                   "Set DNA_API_KEYS or configure api_keys in dna.json.",
        )

    key = _extract_key(request)
    if not key or key not in cfg.api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. "
                   "Supply it via 'Authorization: Bearer <key>' or 'X-API-Key: <key>'.",
        )

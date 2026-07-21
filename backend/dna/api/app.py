from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dna.api.analysis import run_full_analysis
from dna.api.routers import entities as entities_router
from dna.api.routers import evidence as evidence_router
from dna.api.routers import insights as insights_router
from dna.api.routers import system as system_router
from dna.api.routers import search as search_router
from dna.api.routers import streaming as streaming_router
from dna.api.routers import advanced as advanced_router
from dna.api.routers import heatmaps as heatmaps_router
from dna.api.routers import predictive as predictive_router
from dna.api.routers import refactoring_suite as refactoring_suite_router
from dna.api.routers import journeys as journeys_router
from dna.api.routers import documentation as documentation_router
from dna.api.routers import intake as intake_router
from dna.api.routers import benchmarking as benchmarking_router
from dna.api.routers import intelligence as intelligence_router
from dna.api.auth import require_auth
from dna.api.middleware import TimeoutMiddleware, RateLimitMiddleware, BranchMiddleware
from dna.remote import is_github_url, get_local_repo_from_github
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import logging
from dna.config import get_config
from dna.logging import configure_logging, correlation_id

# Configure logging
configure_logging(level=get_config().log_level)
logger = logging.getLogger("dna.api")

FRONTEND_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend")
# Prefer the Vite production build if available, fall back to legacy vanilla HTML
_VITE_DIST = os.path.join(FRONTEND_ROOT, "dist")
FRONTEND_DIR = _VITE_DIST if os.path.isdir(_VITE_DIST) else FRONTEND_ROOT
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")

app = FastAPI(
    title="Project DNA API",
    description="Codebase analysis and reasoning engine",
    version="1.0.0",
    dependencies=[Depends(require_auth)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TimeoutMiddleware)

# Mount Vite static assets if the directory exists
_VITE_ASSETS = os.path.join(_VITE_DIST, "assets")
if os.path.isdir(_VITE_ASSETS):
    app.mount("/assets", StaticFiles(directory=_VITE_ASSETS), name="assets")

# Register /v1/ resource routers
app.include_router(entities_router.router)
app.include_router(evidence_router.router)
app.include_router(insights_router.router)
app.include_router(system_router.router)
app.include_router(search_router.router)
app.include_router(streaming_router.router)
app.include_router(advanced_router.router)
app.include_router(heatmaps_router.router)
app.include_router(predictive_router.router)
app.include_router(refactoring_suite_router.router)
app.include_router(journeys_router.router)
app.include_router(documentation_router.router)
app.include_router(intake_router.router)
app.include_router(benchmarking_router.router)
app.include_router(intelligence_router.router)

app.add_middleware(BranchMiddleware)

@app.middleware("http")
async def add_correlation_id_middleware(request: Request, call_next):
    cid = request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID")
    with correlation_id(cid) as actual_cid:
        logger.info("HTTP Request: %s %s", request.method, request.url.path)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = actual_cid
        # Prevent caching for index.html
        if request.url.path == "/" or request.url.path.endswith(".html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        logger.info("HTTP Response: %s", response.status_code)
        return response


@app.get("/")
async def serve_frontend():
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"message": "DNA API is running"}



class AnalysisRequest(BaseModel):
    repo_path: str
    branch: str = None


class AnalysisResponse(BaseModel):
    repository: dict
    summary: dict
    evolution: dict
    knowledge: dict
    risk: dict
    structural: dict
    insights: list


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/status")
async def status():
    return {
        "version": "1.0.0",
        "engines": ["structural", "evolution", "knowledge", "risk", "reasoning"],
        "ready": True,
    }


def validate_repo_path(path: str) -> str:
    if not path:
        raise ValueError("Repository path must not be empty")
        
    # Prevent null bytes and control characters
    if "\0" in path or any(ord(c) < 32 for c in path):
        raise ValueError("Invalid characters in path")
    
    # Normalize and resolve to absolute path
    resolved_path = os.path.abspath(path)
    
    # Prevent path traversal
    if ".." in path.replace("\\", "/").split("/"):
        raise ValueError("Path traversal not allowed")
        
    # Check exists
    if not os.path.exists(resolved_path):
        raise ValueError(f"Repository path does not exist: {resolved_path}")
        
    # Check is directory
    if not os.path.isdir(resolved_path):
        raise ValueError(f"Repository path is not a directory: {resolved_path}")
        
    # Check accessible
    if not os.access(resolved_path, os.R_OK):
        raise ValueError(f"Repository path is not accessible: {resolved_path}")
        
    return resolved_path


def resolve_path(input_path: str, branch: str = None) -> tuple[str, str | None]:
    """Resolve a repo path that may be a local path or a GitHub URL.
    
    Returns:
        A tuple of (local_filesystem_path, original_input).
        For local paths, original_input is None.
        For GitHub URLs, the clone path is returned along with the original URL.
    """
    stripped = input_path.strip()
    if is_github_url(stripped):
        # GitHub URL — clone/fetch to cache and return the local path
        local_path = get_local_repo_from_github(stripped, branch)
        return local_path, stripped
    else:
        # Local filesystem path — validate and return
        local_path = validate_repo_path(stripped)
        # If it's a local path, we do NOT run git checkout to avoid side effects on the user's working directory.
        return local_path, None


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(req: AnalysisRequest):
    try:
        local_path, github_url = await asyncio.to_thread(resolve_path, req.repo_path, req.branch)
        result = await asyncio.to_thread(run_full_analysis, local_path, req.branch)
        
        # For GitHub URLs, return the original URL (not the cache path)
        if github_url:
            result["repository"]["path"] = github_url
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except RuntimeError as e:
        # e.g. git not installed
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/analyze", response_model=AnalysisResponse)
async def analyze_v1(req: AnalysisRequest):
    """Versioned alias for /analyze."""
    return await analyze(req)


@app.get("/v1/analysis/latest", response_model=AnalysisResponse)
async def get_latest_analysis():
    from dna.api.context import current_branch
    branch = current_branch.get("")
    
    branch_suffix = f"_{branch.replace('/', '_')}" if branch else ""
    latest_path = os.path.join(os.getcwd(), f"latest_analysis{branch_suffix}.json")
    
    # Fallback to default if branch specific not found
    if not os.path.isfile(latest_path) and branch:
        latest_path = os.path.join(os.getcwd(), "latest_analysis.json")
        
    if not os.path.isfile(latest_path):
        raise HTTPException(status_code=404, detail="No previous analysis found. Please run analysis first.")
    try:
        import json
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read latest analysis: {e}")


@app.get("/{catchall:path}")
async def catchall(request: Request):
    # If the request is for an asset or API, don't fallback
    if request.url.path.startswith("/v1/") or request.url.path.startswith("/assets/"):
        raise HTTPException(status_code=404, detail="Not Found")
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"message": "DNA API is running"}

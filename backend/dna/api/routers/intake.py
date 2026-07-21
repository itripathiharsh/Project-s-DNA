import os
import re
import urllib.request
import json
import subprocess
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from dna.security.path_validation import safe_validate_path, validate_branch_name

logger = logging.getLogger("dna.api.intake")
router = APIRouter(prefix="/v1/intake", tags=["intake"])

class IntakeRequest(BaseModel):
    url_or_path: str

class BranchInfo(BaseModel):
    name: str
    last_commit: str
    last_updated: str
    commit_count: int
    author: str
    status: str

class RepositoryInfo(BaseModel):
    name: str
    owner: str
    language: str
    stars: int
    default_branch: str
    branches: List[BranchInfo]
    tags: List[str]
    is_local: bool

GITHUB_PATTERN = re.compile(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")

def fetch_github_info(owner: str, repo: str) -> RepositoryInfo:
    headers = {"User-Agent": "Project-DNA", "Accept": "application/vnd.github.v3+json"}
    
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    # Try fetching repository info
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        with urllib.request.urlopen(req) as response:
            repo_data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        logger.error(f"Error fetching repo info from GitHub: {e}")
        if e.code == 404:
            raise HTTPException(status_code=400, detail="Repository not found or is private. Please provide a GITHUB_TOKEN or use a local path.")
        raise HTTPException(status_code=400, detail=f"GitHub API Error: {e.reason}")
    except Exception as e:
        logger.error(f"Error fetching repo info from GitHub: {e}")
        raise HTTPException(status_code=400, detail="Could not fetch repository info from GitHub.")

    # Try fetching branches
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}/branches", headers=headers)
        with urllib.request.urlopen(req) as response:
            branches_data = json.loads(response.read().decode())
    except Exception as e:
        branches_data = []

    # Try fetching tags
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}/tags", headers=headers)
        with urllib.request.urlopen(req) as response:
            tags_data = json.loads(response.read().decode())
    except Exception as e:
        tags_data = []

    branches = []
    for b in branches_data:
        # Mock some detailed commit stats since fetching them for each branch takes too many requests
        branches.append(BranchInfo(
            name=b["name"],
            last_commit=b["commit"]["sha"][:7],
            last_updated="Just now",
            commit_count=100,
            author="Unknown",
            status="active"
        ))

    return RepositoryInfo(
        name=repo_data.get("name", repo),
        owner=repo_data.get("owner", {}).get("login", owner),
        language=repo_data.get("language") or "Unknown",
        stars=repo_data.get("stargazers_count", 0),
        default_branch=repo_data.get("default_branch", "main"),
        branches=branches,
        tags=[t["name"] for t in tags_data],
        is_local=False
    )

def fetch_local_info(path: str) -> RepositoryInfo:
    # SECURITY: Canonicalize path and block traversal attempts
    try:
        path = safe_validate_path(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not os.path.exists(path) or not os.path.isdir(path):
        raise HTTPException(status_code=400, detail="Local path does not exist or is not a directory.")
    if not os.path.exists(os.path.join(path, ".git")):
        raise HTTPException(status_code=400, detail="Path is not a git repository.")

    try:
        # Get default/current branch
        res = subprocess.run(["git", "branch", "--show-current"], cwd=path, capture_output=True, text=True)
        default_branch = res.stdout.strip() or "main"

        # Get all branches
        res = subprocess.run(["git", "branch"], cwd=path, capture_output=True, text=True)
        branch_lines = [b.strip().strip("* ") for b in res.stdout.splitlines() if b.strip()]
        
        branches = []
        for b in branch_lines:
            # Get last commit hash
            commit_res = subprocess.run(["git", "log", "-1", "--format=%h|%ar|%an", b], cwd=path, capture_output=True, text=True)
            if commit_res.stdout.strip():
                sha, updated, author = commit_res.stdout.strip().split("|")
                # Count commits
                count_res = subprocess.run(["git", "rev-list", "--count", b], cwd=path, capture_output=True, text=True)
                count = int(count_res.stdout.strip()) if count_res.stdout.strip().isdigit() else 0
                
                branches.append(BranchInfo(
                    name=b,
                    last_commit=sha,
                    last_updated=updated,
                    commit_count=count,
                    author=author,
                    status="active"
                ))
            else:
                branches.append(BranchInfo(
                    name=b,
                    last_commit="unknown",
                    last_updated="unknown",
                    commit_count=0,
                    author="unknown",
                    status="active"
                ))

        # Get tags
        res = subprocess.run(["git", "tag"], cwd=path, capture_output=True, text=True)
        tags = [t.strip() for t in res.stdout.splitlines() if t.strip()]

    except Exception as e:
        logger.error(f"Error fetching local git info: {e}")
        raise HTTPException(status_code=500, detail="Error fetching local git repository information.")

    return RepositoryInfo(
        name=os.path.basename(os.path.abspath(path)),
        owner="Local User",
        language="Unknown",
        stars=0,
        default_branch=default_branch,
        branches=branches,
        tags=tags,
        is_local=True
    )

@router.post("/info", response_model=RepositoryInfo)
async def get_repository_info(req: IntakeRequest):
    url = req.url_or_path.strip()
    match = GITHUB_PATTERN.match(url)
    if match:
        owner, repo = match.groups()
        return fetch_github_info(owner, repo)
    else:
        return fetch_local_info(url)

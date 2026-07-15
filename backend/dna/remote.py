import os
import re
import time
import subprocess
import logging
import stat
import shutil
from pathlib import Path
from dna.config import get_config

logger = logging.getLogger("dna.remote")

# Regex to validate GitHub URL
# Matches https://github.com/user/repo or https://github.com/user/repo.git
GITHUB_PATTERN = re.compile(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")

def is_github_url(path: str) -> bool:
    if not path or not isinstance(path, str):
        return False
    return bool(GITHUB_PATTERN.match(path.strip()))

def parse_github_url(url: str) -> tuple[str, str]:
    match = GITHUB_PATTERN.match(url.strip())
    if not match:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    owner, repo = match.groups()
    return owner, repo

class DirLock:
    def __init__(self, lock_path: str, timeout: float = 120.0, poll_interval: float = 0.5):
        self.lock_path = lock_path
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.acquired = False

    def acquire(self):
        start_time = time.time()
        while True:
            try:
                os.mkdir(self.lock_path)
                self.acquired = True
                return True
            except FileExistsError:
                # Check for stale lock
                try:
                    mtime = os.path.getmtime(self.lock_path)
                    # If lock is older than 5 minutes (300 seconds), assume the process crashed and release it
                    if time.time() - mtime > 300.0:
                        logger.warning(f"Lock at {self.lock_path} is stale. Cleaning up.")
                        try:
                            os.rmdir(self.lock_path)
                        except Exception:
                            pass
                        continue
                except Exception:
                    pass

                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"Could not acquire lock on {self.lock_path} within {self.timeout}s")
                time.sleep(self.poll_interval)

    def release(self):
        if self.acquired:
            try:
                os.rmdir(self.lock_path)
            except Exception:
                pass
            self.acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

def check_git_installed():
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        raise RuntimeError("Git is not installed or not found in system PATH")

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_rmtree(path):
    if os.path.exists(path):
        shutil.rmtree(path, onerror=remove_readonly)

def cleanup_cache(cache_dir: str, ttl_days: int):
    if not os.path.isdir(cache_dir):
        return
    now = time.time()
    ttl_seconds = ttl_days * 86400
    for name in os.listdir(cache_dir):
        repo_path = os.path.join(cache_dir, name)
        if not os.path.isdir(repo_path):
            continue
        
        # Skip locks
        if name.endswith(".lock"):
            continue
            
        lock_path = repo_path + ".lock"
        if os.path.exists(lock_path):
            # Skip if active lock exists
            continue
            
        last_used_file = os.path.join(repo_path, ".last_used")
        try:
            if os.path.exists(last_used_file):
                last_used = os.path.getmtime(last_used_file)
            else:
                last_used = os.path.getmtime(repo_path)
                
            if now - last_used > ttl_seconds:
                logger.info(f"Cleaning up expired repository cache: {repo_path}")
                safe_rmtree(repo_path)
        except Exception as e:
            logger.error(f"Error during cleanup of {repo_path}: {e}")

def get_local_repo_from_github(url: str) -> str:
    cfg = get_config()
    if not cfg.enable_remote_repos:
        raise ValueError("Remote GitHub repository analysis is disabled in configuration")

    check_git_installed()
    owner, repo = parse_github_url(url)

    # Determine paths
    cache_dir = os.path.abspath(cfg.repo_cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    
    # Run cache cleanup before processing
    cleanup_cache(cache_dir, cfg.repo_cache_ttl_days)

    repo_dir_name = f"{owner}_{repo}"
    local_path = os.path.join(cache_dir, repo_dir_name)
    lock_path = os.path.join(cache_dir, f"{repo_dir_name}.lock")

    logger.info(f"Accessing remote repository {url} (cache: {local_path})")

    # Use file-based lock for concurrency
    with DirLock(lock_path, timeout=float(cfg.git_clone_timeout + 10)):
        if not os.path.isdir(local_path):
            # First request -> Clone
            logger.info(f"Cloning {url} into {local_path}...")
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, local_path],
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=True,
                    timeout=cfg.git_clone_timeout
                )
            except subprocess.TimeoutExpired:
                logger.error(f"Git clone timed out for {url}")
                safe_rmtree(local_path)
                raise TimeoutError(f"Git clone timed out for repository: {url}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Git clone failed for {url}: {e.stderr}")
                safe_rmtree(local_path)
                err_msg = e.stderr.lower()
                if "not found" in err_msg or "404" in err_msg:
                    raise ValueError(f"GitHub repository not found: {url}")
                elif "auth" in err_msg or "permission" in err_msg or "terminal prompts disabled" in err_msg:
                    raise ValueError(f"Authentication failed or repository is private: {url}")
                else:
                    raise ValueError(f"Git clone failed: {e.stderr.strip()}")
        else:
            # Second request -> Fetch & Reset hard
            logger.info(f"Cache hit. Updating {url} in {local_path}...")
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            try:
                # Get current branch
                res = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=local_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=True,
                    env=env
                )
                branch = res.stdout.strip()
                
                # Fetch newest commit from upstream
                subprocess.run(
                    ["git", "fetch", "--depth", "1"],
                    cwd=local_path,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=True,
                    timeout=cfg.git_fetch_timeout
                )
                
                # Reset hard to origin/branch
                subprocess.run(
                    ["git", "reset", "--hard", f"origin/{branch}"],
                    cwd=local_path,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=True
                )
                
                # Clean untracked
                subprocess.run(
                    ["git", "clean", "-fdx"],
                    cwd=local_path,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=True
                )
            except subprocess.TimeoutExpired:
                logger.error(f"Git fetch timed out for {url}")
                raise TimeoutError(f"Git fetch timed out for repository: {url}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Git fetch/update failed for {url}: {e.stderr}")
                err_msg = e.stderr.lower()
                if "not found" in err_msg or "404" in err_msg:
                    raise ValueError(f"GitHub repository not found: {url}")
                elif "auth" in err_msg or "permission" in err_msg or "terminal prompts disabled" in err_msg:
                    raise ValueError(f"Authentication failed or repository is private: {url}")
                else:
                    raise ValueError(f"Git update failed: {e.stderr.strip()}")

        # Update last used timestamp
        try:
            last_used_file = os.path.join(local_path, ".last_used")
            Path(last_used_file).touch()
        except Exception:
            pass

    return local_path

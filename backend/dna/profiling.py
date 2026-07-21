"""Temporary timing instrumentation for the analysis pipeline.

This module adds start/end timestamps, per-call duration, files processed,
and cumulative elapsed time around every major pipeline function.

It prints to stderr with a bold tag so the slowest / hanging function is
visible in any console output.

Usage: this module is imported (no behavior change unless DNA_TIMING=1
in the environment, which defaults to ON for ad-hoc diagnostics).
"""

import os
import sys
import time
import functools
import inspect
from datetime import datetime, timezone

# Master switch. Defaults to ON so timestamps always print for diagnostics.
ENABLED = os.environ.get("DNA_TIMING", "1") not in ("0", "false", "False")

# Module start time captured once at import.
_T0 = time.perf_counter()
_WALL_T0 = datetime.now(timezone.utc)

# Global counters (readable from anywhere)
COUNTERS = {
    "files_discovered": 0,
    "files_ignored": 0,
    "files_parsed": 0,
    "ai_requests": 0,
    "db_writes": 0,
    "cache_hits": 0,
    "cache_misses": 0,
}


def _wall_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond:06d}"


def _bold(msg: str) -> str:
    # ANSI bold red so it stands out; terminals without ANSI just see text.
    return f"\033[1;31m{msg}\033[0m"


def _print(msg: str) -> None:
    if not ENABLED:
        return
    sys.stderr.flush()
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def reset() -> None:
    global _T0, _WALL_T0
    _T0 = time.perf_counter()
    _WALL_T0 = datetime.now(timezone.utc)
    for k in list(COUNTERS):
        COUNTERS[k] = 0


def elapsed_total() -> float:
    return time.perf_counter() - _T0


def timed(func=None, *, name: str | None = None):
    """Decorator that prints BEFORE and AFTER timestamps for a function.

    Captures: start wall time, end wall time, duration (s), cumulative
    elapsed time since module import, and (where possible) the number of
    items processed.
    """

    def decorator(fn):
        label = name or f"{fn.__module__}.{fn.__qualname__}"

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not ENABLED:
                return fn(*args, **kwargs)

            start_wall = _wall_now()
            start_perf = time.perf_counter()
            cum_before = time.perf_counter() - _T0
            _print(_bold(
                f"[DNA-TIMING] >>> {label} START wall={start_wall} "
                f"cumulative={cum_before:.4f}s"
            ))

            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                end_perf = time.perf_counter()
                dur = end_perf - start_perf
                cum_after = end_perf - _T0
                _print(_bold(
                    f"[DNA-TIMING] !!! {label} RAISED after {dur:.4f}s "
                    f"cumulative={cum_after:.4f}s exc={type(exc).__name__}: {exc}"
                ))
                raise

            end_perf = time.perf_counter()
            dur = end_perf - start_perf
            cum_after = end_perf - _T0
            items = _count_items(result)
            _print(_bold(
                f"[DNA-TIMING] <<< {label} END   wall={_wall_now()} "
                f"duration={dur:.4f}s cumulative={cum_after:.4f}s "
                f"items={items}"
            ))
            return result

        return wrapper

    if func is not None and callable(func):
        return decorator(func)
    return decorator


def _count_items(result) -> str:
    try:
        if result is None:
            return "-"
        if hasattr(result, "__len__"):
            return str(len(result))
        n = 0
        if hasattr(result, "files"):
            n += len(result.files)
        if hasattr(result, "entities"):
            n += len(result.entities)
        if hasattr(result, "commits"):
            n += len(result.commits)
        return str(n) if n else "?"
    except Exception:
        return "?"


def log_event(label: str, detail: str = "") -> None:
    """One-shot timing log point used inside functions that can't be wrapped."""
    if not ENABLED:
        return
    _print(_bold(
        f"[DNA-TIMING] --- {label} wall={_wall_now()} "
        f"cumulative={time.perf_counter() - _T0:.4f}s {detail}"
    ))


def banner(title: str) -> None:
    if not ENABLED:
        return
    line = "=" * 70
    _print(_bold(f"\n{line}\nDNA-TIMING {title}\n{line}"))


def summary() -> None:
    if not ENABLED:
        return
    banner("SUMMARY")
    _print(f"[DNA-TIMING] total elapsed: {elapsed_total():.4f}s")
    for k, v in COUNTERS.items():
        _print(f"[DNA-TIMING] counter {k} = {v}")

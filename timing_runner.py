"""Run the instrumented analysis pipeline against a real repository.

Usage:
    python timing_runner.py <repo_path>

This ONLY adds timing output; it does not change analysis behavior.
All output goes to stderr (bold red) so you can pipe stdout elsewhere.
"""

import sys
import os

# Ensure backend is importable regardless of CWD.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "backend"))

# Force timing ON even if someone set DNA_TIMING=0.
os.environ["DNA_TIMING"] = "1"

import dna.profiling as profiling
from dna.api.analysis import run_full_analysis


def main():
    if len(sys.argv) < 2:
        profiling.banner("ERROR: missing repo path argument")
        sys.exit(2)

    repo_path = os.path.abspath(sys.argv[1])
    if not os.path.isdir(repo_path):
        profiling.banner(f"ERROR: not a directory: {repo_path}")
        sys.exit(2)

    profiling.banner(f"timing_runner target={repo_path}")
    try:
        result = run_full_analysis(repo_path)
        profiling.banner(
            f"DONE result_files={result.get('summary', {}).get('total_files', '?')}"
        )
    except Exception as exc:
        profiling.banner(f"FATAL exc={type(exc).__name__}: {exc}")
        raise
    finally:
        profiling.summary()


if __name__ == "__main__":
    main()

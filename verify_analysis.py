"""Verification harness: runs run_full_analysis and dumps the result to a
JSON file for byte-for-byte comparison before/after optimizations.

Usage:
    python verify_analysis.py <repo_path> <out_json>

The dumped JSON is the EXACT dict returned by run_full_analysis (sorted keys,
default separators) so any behavioral change shows up as a diff.
"""

import sys
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "backend"))

# Quiet the timing output while measuring the actual analysis result.
os.environ["DNA_TIMING"] = "0"

from dna.api.analysis import run_full_analysis


def main():
    if len(sys.argv) < 3:
        print("usage: verify_analysis.py <repo_path> <out_json>", file=sys.stderr)
        sys.exit(2)
    repo_path = os.path.abspath(sys.argv[1])
    out_path = os.path.abspath(sys.argv[2])
    result = run_full_analysis(repo_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, sort_keys=True, separators=(",", ":"), default=str)
    print(f"OK wrote {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    main()

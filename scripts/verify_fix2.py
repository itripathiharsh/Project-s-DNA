import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from dna.api.analysis import run_full_analysis

path = "F:\\code\\ig\\ig-costing-main"
print(f"Analyzing: {path}")
start = time.perf_counter()
result = run_full_analysis(path)
elapsed = (time.perf_counter() - start) * 1000
print(f"Completed in {elapsed:.0f}ms ({elapsed/1000:.1f}s)")
print(f"  Files: {result['summary']['total_files']}")
print(f"  Source: {result['summary']['source_files']}")
print(f"  Commits: {result['summary']['total_commits']}")
print(f"  Authors: {result['summary']['total_authors']}")
print(f"  Insights: {len(result['insights'])}")

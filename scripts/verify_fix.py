import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from dna.api.analysis import run_full_analysis

path = "F:\\code\\ig\\ig-costing-main\\ig-costing-main"
result = run_full_analysis(path)
print("SUCCESS")
print(f"  Files: {result['summary']['total_files']}")
print(f"  Source: {result['summary']['source_files']}")
print(f"  Test: {result['summary']['test_files']}")
print(f"  Commits: {result['summary']['total_commits']}")
print(f"  Authors: {result['summary']['total_authors']}")
print(f"  Insights: {len(result['insights'])}")
print(f"  Risk indicators: {len(result['risk']['risk_indicators'])}")

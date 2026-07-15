"""Test each step of the pipeline individually on the outer path."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dna.discovery.orchestrator import discover_repository
from dna.indexer.orchestrator import index_repository
from dna.parser.orchestrator import parse_repository
from dna.models import FileCategory

path = "F:\\code\\ig\\ig-costing-main"
print(f"Testing on: {path}")

# Step 1
print("\n--- Step 1: discover_repository ---")
sys.stdout.flush()
t0 = time.perf_counter()
repo = discover_repository(path)
t1 = time.perf_counter()
print(f"  Elapsed: {(t1-t0)*1000:.0f}ms")
print(f"  Files: {repo.file_count}")
sys.stdout.flush()

# Step 2
print("\n--- Step 2: index_repository ---")
sys.stdout.flush()
t0 = time.perf_counter()
inv = index_repository(path, repo)
t1 = time.perf_counter()
print(f"  Elapsed: {(t1-t0)*1000:.0f}ms")
print(f"  Total files: {len(inv.files)}")
src = [f for f in inv.files if f.category == FileCategory.SOURCE]
print(f"  Source files: {len(src)}")
sys.stdout.flush()

# Step 3
print("\n--- Step 3: parse_repository ---")
sys.stdout.flush()
t0 = time.perf_counter()
parsed = parse_repository(inv)
t1 = time.perf_counter()
print(f"  Elapsed: {(t1-t0)*1000:.0f}ms")
print(f"  Parsed files: {len(parsed)}")
sys.stdout.flush()

print("\nDone")

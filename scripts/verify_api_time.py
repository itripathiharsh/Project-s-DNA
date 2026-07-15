import threading, time, requests, uvicorn, datetime as dt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from dna.api.app import app

def run():
    uvicorn.run(app, host="127.0.0.1", port=9882, log_level="error")

t = threading.Thread(target=run, daemon=True)
t.start()
time.sleep(3)

path = "F:\\code\\ig\\ig-costing-main"
print(f"POST /analyze on: {path}")
sys.stdout.flush()
start = dt.datetime.now()
r = requests.post("http://127.0.0.1:9882/analyze", json={"repo_path": path}, timeout=60)
elapsed = (dt.datetime.now() - start).total_seconds()
print(f"Status: {r.status_code}, elapsed: {elapsed:.1f}s")
data = r.json()
print(f"Files: {data['summary']['total_files']}")
print(f"Source: {data['summary']['source_files']}")
assert elapsed < 20, f"TOO SLOW: {elapsed:.1f}s > 20s limit"
print(f"PASS: completed in {elapsed:.1f}s (under 20s limit)")

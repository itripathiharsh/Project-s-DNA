import threading, time, requests, tempfile, os, subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from dna.api.app import app
import uvicorn

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=9879, log_level="error")

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(3)

base = "http://127.0.0.1:9879"
all_ok = True

def check(name, ok, detail=""):
    global all_ok
    status = "PASS" if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"  [{status}] {name} {detail}")

# 1. Health
r = requests.get(f"{base}/health")
check("GET /health", r.status_code == 200 and r.json().get("status") == "ok")

# 2. Status
r = requests.get(f"{base}/status")
j = r.json()
check("GET /status", r.status_code == 200 and j.get("ready") is True,
      f"version={j.get('version')}")

# 3. Frontend HTML
r = requests.get(f"{base}/")
check("GET /", r.status_code == 200 and "Project DNA" in r.text,
      f"length={len(r.text)}")

# 4. CSS
r = requests.get(f"{base}/styles.css")
check("GET /styles.css", r.status_code == 200 and len(r.content) > 100,
      f"length={len(r.content)}")

# 5. JS
r = requests.get(f"{base}/app.js")
check("GET /app.js", r.status_code == 200 and len(r.content) > 100,
      f"length={len(r.content)}")

# 6. Analyze - invalid path
r = requests.post(f"{base}/analyze", json={"repo_path": "C:\\nonexistent"})
check("POST /analyze (invalid)", r.status_code == 500)

# 7. Analyze - real temp repo
tmpdir = tempfile.mkdtemp()
subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmpdir, capture_output=True)
subprocess.run(["git", "config", "user.name", "T"], cwd=tmpdir, capture_output=True)
with open(os.path.join(tmpdir, "main.py"), "w") as f:
    f.write("x=1\n")
subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
subprocess.run(["git", "commit", "-m", "feat: init"], cwd=tmpdir, capture_output=True)

r = requests.post(f"{base}/analyze", json={"repo_path": tmpdir})
j = r.json()
check("POST /analyze (real repo)", r.status_code == 200,
      f"commits={j['summary']['total_commits']}, files={j['summary']['total_files']}, insights={len(j['insights'])}")

print(f"\nOverall: {'ALL PASSED' if all_ok else 'SOME FAILED'}")
sys.exit(0 if all_ok else 1)

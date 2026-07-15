import threading, time, sys
import uvicorn
from dna.api.app import app

def run():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

t = threading.Thread(target=run, daemon=True)
t.start()
time.sleep(2)

import requests
r = requests.get("http://127.0.0.1:8000/health")
print(f"Server running: {r.json()}")
print(f"Local URL:  http://127.0.0.1:8000")
print(f"API Docs:   http://127.0.0.1:8000/docs")
print(f"Dashboard:  http://127.0.0.1:8000")
print()
print("Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
    sys.exit(0)

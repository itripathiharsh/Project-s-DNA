import os
import sys

# Ensure the backend package is importable when starting from the repository root.
PROJECT_ROOT = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("dna.api.app:app", host="0.0.0.0", port=8000, reload=True)

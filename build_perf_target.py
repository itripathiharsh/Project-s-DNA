"""Build a throwaway test git repository inside the workspace so the analysis
pipeline (including git history mining and per-file git blame) exercises its
slow paths, and so optimizations can be validated to produce identical output.

The repo is created at F:\\code\\project DNA\\tests\\_perf_target and committed
several times. Safe to delete after validation.
"""

import os
import shutil
import subprocess
import sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "_perf_target")


def _git(args, cwd):
    proc = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {args}: {proc.stderr}")
    return proc.stdout


def build():
    if os.path.exists(TARGET):
        # allow re-run; preserve existing repo so blame history stays stable
        return TARGET
    os.makedirs(TARGET)
    _git(["init", "-q"], TARGET)
    _git(["config", "user.email", "alice@example.com"], TARGET)
    _git(["config", "user.name", "Alice"], TARGET)

    files = {
        "app.py": "def main():\n    return run()\n\ndef run():\n    return 1\n",
        "utils/math_tools.py": "def add(a, b):\n    return a + b\n\ndef mul(a, b):\n    return a * b\n",
        "utils/strings.py": "def upper(s):\n    return s.upper()\n",
        "models/user.py": "class User:\n    def __init__(self, name):\n        self.name = name\n",
        "models/order.py": "class Order:\n    def __init__(self, total):\n        self.total = total\n",
        "tests/test_app.py": "from app import main\n\ndef test_main():\n    assert main() == 1\n",
    }

    for rel, content in files.items():
        full = os.path.join(TARGET, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
    _git(["add", "-A"], TARGET)
    _git(["commit", "-q", "-m", "feat: initial import"], TARGET)

    # A few follow-up commits editing different files, by different authors.
    edits = [
        ("Bob", "bob@example.com", "app.py", "def main():\n    return run() + 1\n\ndef run():\n    return 2\n"),
        ("Bob", "bob@example.com", "utils/math_tools.py", "def add(a, b):\n    return a + b\n\ndef mul(a, b):\n    return a * b\n\ndef sub(a, b):\n    return a - b\n"),
        ("Alice", "alice@example.com", "models/user.py", "class User:\n    def __init__(self, name):\n        self.name = name\n    def greet(self):\n        return f'hi {self.name}'\n"),
        ("Charlie", "charlie@example.com", "tests/test_app.py", "from app import main\n\ndef test_main():\n    assert main() == 3\n"),
    ]
    for author, email, path, content in edits:
        _git(["config", "user.name", author], TARGET)
        _git(["config", "user.email", email], TARGET)
        with open(os.path.join(TARGET, path), "w", encoding="utf-8") as f:
            f.write(content)
        _git(["add", "-A"], TARGET)
        _git(["commit", "-q", "-m", f"chore: edit {path}"], TARGET)

    return TARGET


if __name__ == "__main__":
    p = build()
    print(p)

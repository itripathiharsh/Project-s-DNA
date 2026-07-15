import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "dna_system.db")

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS repositories (
    path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    analyzed_at TEXT NOT NULL,
    total_files INTEGER NOT NULL DEFAULT 0,
    source_files INTEGER NOT NULL DEFAULT 0,
    commits INTEGER NOT NULL DEFAULT 0,
    risk_score REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL,
    read INTEGER NOT NULL DEFAULT 0,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    repo_path TEXT NOT NULL,
    status TEXT NOT NULL,
    assignees TEXT NOT NULL, -- JSON list
    files TEXT NOT NULL,      -- JSON list
    comments TEXT NOT NULL,   -- JSON list
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS refactoring_pipelines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    tasks TEXT NOT NULL,      -- JSON list
    impact_report TEXT NOT NULL, -- JSON object
    execution_history TEXT NOT NULL, -- JSON list
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS organization_teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    members TEXT NOT NULL      -- JSON list of member objects
);
"""

class SystemDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn = None

    def open(self):
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()
        return self

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Repositories
    def add_repository(self, path: str, name: str, total_files: int, source_files: int, commits: int, risk_score: float):
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO repositories (path, name, analyzed_at, total_files, source_files, commits, risk_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (path, name, now, total_files, source_files, commits, risk_score)
        )
        self._conn.commit()

    def get_repositories(self):
        cursor = self._conn.execute("SELECT path, name, analyzed_at, total_files, source_files, commits, risk_score FROM repositories ORDER BY analyzed_at DESC")
        return [
            {
                "path": r[0],
                "name": r[1],
                "analyzed_at": r[2],
                "total_files": r[3],
                "source_files": r[4],
                "commits": r[5],
                "risk_score": r[6]
            }
            for r in cursor.fetchall()
        ]

    # Settings
    def set_setting(self, key: str, value: str):
        self._conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self._conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        cursor = self._conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

    def get_all_settings(self):
        cursor = self._conn.execute("SELECT key, value FROM settings")
        return {r[0]: r[1] for r in cursor.fetchall()}

    # Notifications
    def add_notification(self, title: str, message: str, type_: str = "info"):
        import uuid
        nid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO notifications (id, title, message, type, read, timestamp) VALUES (?, ?, ?, ?, 0, ?)",
            (nid, title, message, type_, now)
        )
        self._conn.commit()
        return nid

    def get_notifications(self, unread_only: bool = False):
        if unread_only:
            cursor = self._conn.execute("SELECT id, title, message, type, read, timestamp FROM notifications WHERE read = 0 ORDER BY timestamp DESC")
        else:
            cursor = self._conn.execute("SELECT id, title, message, type, read, timestamp FROM notifications ORDER BY timestamp DESC")
        return [
            {
                "id": r[0],
                "title": r[1],
                "message": r[2],
                "type": r[3],
                "read": bool(r[4]),
                "timestamp": r[5]
            }
            for r in cursor.fetchall()
        ]

    def mark_notification_read(self, nid: str):
        self._conn.execute("UPDATE notifications SET read = 1 WHERE id = ?", (nid,))
        self._conn.commit()

    def mark_all_notifications_read(self):
        self._conn.execute("UPDATE notifications SET read = 1")
        self._conn.commit()

    def delete_notification(self, nid: str):
        self._conn.execute("DELETE FROM notifications WHERE id = ?", (nid,))
        self._conn.commit()

    # Reviews
    def create_review(self, title: str, description: str, repo_path: str, assignees: list, files: list):
        import uuid
        rid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO reviews (id, title, description, repo_path, status, assignees, files, comments, created_at) VALUES (?, ?, ?, ?, 'open', ?, ?, '[]', ?)",
            (rid, title, description, repo_path, json.dumps(assignees), json.dumps(files), now)
        )
        self._conn.commit()
        return rid

    def get_reviews(self):
        cursor = self._conn.execute("SELECT id, title, description, repo_path, status, assignees, files, comments, created_at FROM reviews ORDER BY created_at DESC")
        return [
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "repo_path": r[3],
                "status": r[4],
                "assignees": json.loads(r[5]),
                "files": json.loads(r[6]),
                "comments": json.loads(r[7]),
                "created_at": r[8]
            }
            for r in cursor.fetchall()
        ]

    def get_review(self, rid: str):
        cursor = self._conn.execute("SELECT id, title, description, repo_path, status, assignees, files, comments, created_at FROM reviews WHERE id = ?", (rid,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "repo_path": row[3],
            "status": row[4],
            "assignees": json.loads(row[5]),
            "files": json.loads(row[6]),
            "comments": json.loads(row[7]),
            "created_at": row[8]
        }

    def update_review_status(self, rid: str, status: str):
        self._conn.execute("UPDATE reviews SET status = ? WHERE id = ?", (status, rid))
        self._conn.commit()

    def add_review_comment(self, rid: str, comment: dict):
        review = self.get_review(rid)
        if not review:
            return False
        comments = review["comments"]
        comments.append({
            "id": len(comments) + 1,
            "author": comment.get("author", "User"),
            "text": comment.get("text", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "file_path": comment.get("file_path"),
            "line": comment.get("line")
        })
        self._conn.execute("UPDATE reviews SET comments = ? WHERE id = ?", (json.dumps(comments), rid))
        self._conn.commit()
        return True

    # Refactoring Pipelines
    def create_pipeline(self, name: str, description: str, tasks: list, impact_report: dict):
        import uuid
        pid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO refactoring_pipelines (id, name, description, status, tasks, impact_report, execution_history, created_at) VALUES (?, ?, ?, 'pending', ?, ?, '[]', ?)",
            (pid, name, description, json.dumps(tasks), json.dumps(impact_report), now)
        )
        self._conn.commit()
        return pid

    def get_pipelines(self):
        cursor = self._conn.execute("SELECT id, name, description, status, tasks, impact_report, execution_history, created_at FROM refactoring_pipelines ORDER BY created_at DESC")
        return [
            {
                "id": r[0],
                "name": r[1],
                "description": r[2],
                "status": r[3],
                "tasks": json.loads(r[4]),
                "impact_report": json.loads(r[5]),
                "execution_history": json.loads(r[6]),
                "created_at": r[7]
            }
            for r in cursor.fetchall()
        ]

    def get_pipeline(self, pid: str):
        cursor = self._conn.execute("SELECT id, name, description, status, tasks, impact_report, execution_history, created_at FROM refactoring_pipelines WHERE id = ?", (pid,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "tasks": json.loads(row[4]),
            "impact_report": json.loads(row[5]),
            "execution_history": json.loads(row[6]),
            "created_at": row[7]
        }

    def update_pipeline_status(self, pid: str, status: str):
        self._conn.execute("UPDATE refactoring_pipelines SET status = ? WHERE id = ?", (status, pid))
        self._conn.commit()

    def run_pipeline_step(self, pid: str, step_index: int, status: str, log_message: str):
        pipeline = self.get_pipeline(pid)
        if not pipeline:
            return False
        
        # update task status
        tasks = pipeline["tasks"]
        if 0 <= step_index < len(tasks):
            tasks[step_index]["status"] = status
            tasks[step_index]["log"] = log_message
        
        # add to history
        history = pipeline["execution_history"]
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": f"Step {step_index} ('{tasks[step_index]['name'] if step_index < len(tasks) else ''}') updated to {status}",
            "log": log_message
        })
        
        # determine overall status
        all_done = all(t.get("status") == "success" for t in tasks)
        any_failed = any(t.get("status") == "failed" for t in tasks)
        
        overall_status = "running"
        if all_done:
            overall_status = "success"
        elif any_failed:
            overall_status = "failed"
            
        self._conn.execute(
            "UPDATE refactoring_pipelines SET tasks = ?, status = ?, execution_history = ? WHERE id = ?",
            (json.dumps(tasks), overall_status, json.dumps(history), pid)
        )
        self._conn.commit()
        return True

    # Teams / Organization
    def get_teams(self):
        cursor = self._conn.execute("SELECT id, name, role, members FROM organization_teams")
        rows = cursor.fetchall()
        if not rows:
            # Seed default teams
            self.seed_default_teams()
            cursor = self._conn.execute("SELECT id, name, role, members FROM organization_teams")
            rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "name": r[1],
                "role": r[2],
                "members": json.loads(r[3])
            }
            # Make sure we don't return raw DB format if it changes
            for r in rows
        ]

    def seed_default_teams(self):
        teams = [
            ("team-1", "Platform Engineering", "Architectural Governance", json.dumps([
                {"name": "Alice Johnson", "role": "Lead Architect", "email": "alice@company.com"},
                {"name": "Bob Smith", "role": "Senior Dev", "email": "bob@company.com"}
            ])),
            ("team-2", "Security & Quality", "Risk Management & Compliance", json.dumps([
                {"name": "Charlie Brown", "role": "Security Specialist", "email": "charlie@company.com"},
                {"name": "David Miller", "role": "QA Lead", "email": "david@company.com"}
            ]))
        ]
        for t in teams:
            self._conn.execute("INSERT OR REPLACE INTO organization_teams (id, name, role, members) VALUES (?, ?, ?, ?)", t)
        self._conn.commit()

    def update_team(self, team_id: str, name: str, role: str, members: list):
        self._conn.execute(
            "INSERT OR REPLACE INTO organization_teams (id, name, role, members) VALUES (?, ?, ?, ?)",
            (team_id, name, role, json.dumps(members))
        )
        self._conn.commit()

    def delete_team(self, team_id: str):
        self._conn.execute("DELETE FROM organization_teams WHERE id = ?", (team_id,))
        self._conn.commit()

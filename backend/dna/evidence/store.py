import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from dna.models import Evidence


_CURRENT_VERSION = 2

_SCHEMA_SQL_V1 = """
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL DEFAULT '',
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(type);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source);
"""

_SCHEMA_SQL_V2 = """
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    file_path TEXT NOT NULL DEFAULT '',
    timestamp TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 1.0
);

CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(type);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source);
"""


class EvidenceStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        # When > 0, add_evidence() defers its commit until the outermost
        # transaction block exits. This lets an analysis stage write many
        # rows with a single final commit.
        self._tx_depth = 0

    def open(self) -> None:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")

        # Check current user_version
        cursor = self._conn.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]

        if version == 0:
            # Check if evidence table already exists from a legacy/pre-migration DB (which would be v1)
            # If evidence table exists but user_version is 0, we can treat it as version 1.
            check_table = self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='evidence'"
            ).fetchone()
            if check_table:
                version = 1
            else:
                self._conn.executescript(_SCHEMA_SQL_V2)
                self._conn.execute(f"PRAGMA user_version = {_CURRENT_VERSION}")
                self._conn.commit()
                return

        if version < _CURRENT_VERSION:
            if version == 1:
                self._conn.execute("ALTER TABLE evidence ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0")
                self._conn.execute("PRAGMA user_version = 2")
                self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def transaction(self):
        """Batching context manager: inserts inside the block commit exactly
        once at the exit of the outermost block, with rollback on exception.

        Nestable: only the outermost transaction performs the final commit.
        Maintains identical database contents vs. per-row commits when no
        exception occurs; on exception, all writes in this block are rolled
        back (rollback safety that per-row commits did not provide).
        """
        if not self._conn:
            raise RuntimeError("Store not opened")
        outermost = self._tx_depth == 0
        self._tx_depth += 1
        # Begin an explicit transaction only at the outermost level. Nested
        # blocks reuse the in-flight transaction.
        if outermost:
            self._conn.execute("BEGIN")
        try:
            yield
        except Exception:
            if outermost:
                self._conn.execute("ROLLBACK")
                self._tx_depth = 0
            else:
                self._tx_depth -= 1
            raise
        else:
            if outermost:
                self._conn.execute("COMMIT")
            self._tx_depth -= 1

    def add_evidence(self, evidence_type: str = None, value: object = None, source: str = "",
                     file_path: str = "", **kwargs) -> Evidence:
        # Support both positional and keyword arguments for type and data/value
        if evidence_type is None:
            evidence_type = kwargs.pop('type', None)
        if evidence_type is None:
            raise TypeError('add_evidence missing required argument: evidence_type or type')
        if value is None:
            # Accept `value` or `data` keyword as the evidence payload
            value = kwargs.pop('value', None) or kwargs.pop('data', None)
        if value is None:
            raise TypeError('add_evidence missing required argument: value (or data)')
        if not self._conn:
            raise RuntimeError("Store not opened")

        ev = Evidence(
            id=str(uuid.uuid4()),
            type=evidence_type,
            value=json.dumps(value) if not isinstance(value, str) else value,
            source=source,
            file_path=file_path,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._conn.execute(
            "INSERT INTO evidence (id, type, value, source, file_path, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (ev.id, ev.type, ev.value, ev.source, ev.file_path, ev.timestamp),
        )
        # Commit immediately only when not inside an explicit batching
        # transaction; otherwise defer to the outermost block's commit.
        if self._tx_depth == 0:
            self._conn.commit()
        return ev

    def get_by_type(self, evidence_type: str) -> list[Evidence]:
        if not self._conn:
            raise RuntimeError("Store not opened")
        cursor = self._conn.execute(
            "SELECT id, type, value, source, file_path, timestamp FROM evidence WHERE type = ?"
            " ORDER BY timestamp DESC",
            (evidence_type,),
        )
        return [Evidence(id=r[0], type=r[1], value=r[2], source=r[3], file_path=r[4], timestamp=r[5])
                for r in cursor.fetchall()]

    def get_by_source(self, source: str) -> list[Evidence]:
        if not self._conn:
            raise RuntimeError("Store not opened")
        cursor = self._conn.execute(
            "SELECT id, type, value, source, file_path, timestamp FROM evidence WHERE source = ?"
            " ORDER BY timestamp DESC",
            (source,),
        )
        return [Evidence(id=r[0], type=r[1], value=r[2], source=r[3], file_path=r[4], timestamp=r[5])
                for r in cursor.fetchall()]

    def get_by_file(self, file_path: str) -> list[Evidence]:
        if not self._conn:
            raise RuntimeError("Store not opened")
        cursor = self._conn.execute(
            "SELECT id, type, value, source, file_path, timestamp FROM evidence WHERE file_path = ?"
            " ORDER BY timestamp DESC",
            (file_path,),
        )
        return [Evidence(id=r[0], type=r[1], value=r[2], source=r[3], file_path=r[4], timestamp=r[5])
                for r in cursor.fetchall()]

    def get_all(self) -> list[Evidence]:
        if not self._conn:
            raise RuntimeError("Store not opened")
        cursor = self._conn.execute(
            "SELECT id, type, value, source, file_path, timestamp FROM evidence ORDER BY timestamp DESC"
        )
        return [Evidence(id=r[0], type=r[1], value=r[2], source=r[3], file_path=r[4], timestamp=r[5])
                for r in cursor.fetchall()]

    def count(self) -> int:
        if not self._conn:
            raise RuntimeError("Store not opened")
        return self._conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]

    def clear(self) -> None:
        if not self._conn:
            raise RuntimeError("Store not opened")
        self._conn.execute("DELETE FROM evidence")
        self._conn.commit()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

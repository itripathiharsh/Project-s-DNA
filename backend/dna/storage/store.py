import sqlite3
import json
from dna.models import EntityGraph, Entity, EntityRelation


_CURRENT_VERSION = 2

_SCHEMA_SQL_V1 = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    uid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    file_path TEXT NOT NULL DEFAULT '',
    line INTEGER NOT NULL DEFAULT 0,
    properties TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_uid TEXT NOT NULL,
    target_uid TEXT NOT NULL,
    kind TEXT NOT NULL,
    FOREIGN KEY (source_uid) REFERENCES entities(uid),
    FOREIGN KEY (target_uid) REFERENCES entities(uid)
);

CREATE INDEX IF NOT EXISTS idx_entities_kind ON entities(kind);
CREATE INDEX IF NOT EXISTS idx_entities_file ON entities(file_path);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_uid);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_uid);
"""

_SCHEMA_SQL_V2 = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    uid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    file_path TEXT NOT NULL DEFAULT '',
    line INTEGER NOT NULL DEFAULT 0,
    properties TEXT NOT NULL DEFAULT '{}',
    hash TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_uid TEXT NOT NULL,
    target_uid TEXT NOT NULL,
    kind TEXT NOT NULL,
    FOREIGN KEY (source_uid) REFERENCES entities(uid),
    FOREIGN KEY (target_uid) REFERENCES entities(uid)
);

CREATE INDEX IF NOT EXISTS idx_entities_kind ON entities(kind);
CREATE INDEX IF NOT EXISTS idx_entities_file ON entities(file_path);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_uid);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_uid);
"""


class SCStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def open(self) -> None:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        
        # Check current user_version
        cursor = self._conn.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        
        if version == 0:
            # Check if entities table already exists from a legacy/pre-migration DB (which would be v1)
            # If entities table exists but user_version is 0, we can treat it as version 1.
            check_table = self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='entities'"
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
                self._conn.execute("ALTER TABLE entities ADD COLUMN hash TEXT NOT NULL DEFAULT ''")
                self._conn.execute("PRAGMA user_version = 2")
                self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def save_entity_graph(self, graph: EntityGraph) -> None:
        if not self._conn:
            raise RuntimeError("Store not opened")

        files_in_new_graph = {e.file_path for e in graph.entities if e.file_path}

        if not files_in_new_graph:
            self._conn.execute("DELETE FROM entities")
            self._conn.execute("DELETE FROM relations")
        else:
            placeholders = ",".join("?" for _ in files_in_new_graph)
            q = f"SELECT uid FROM entities WHERE file_path IN ({placeholders})"
            cursor = self._conn.execute(q, tuple(files_in_new_graph))
            uids_to_delete = [row[0] for row in cursor]
            
            if uids_to_delete:
                uid_placeholders = ",".join("?" for _ in uids_to_delete)
                self._conn.execute(
                    f"DELETE FROM relations WHERE source_uid IN ({uid_placeholders}) OR target_uid IN ({uid_placeholders})",
                    tuple(uids_to_delete) * 2
                )
                self._conn.execute(
                    f"DELETE FROM entities WHERE file_path IN ({placeholders})",
                    tuple(files_in_new_graph)
                )

        for entity in graph.entities:
            self._conn.execute(
                "INSERT OR REPLACE INTO entities (uid, name, kind, file_path, line, properties) VALUES (?, ?, ?, ?, ?, ?)",
                (entity.uid, entity.name, entity.kind, entity.file_path, entity.line,
                 json.dumps(entity.properties)),
            )

        for rel in graph.relations:
            self._conn.execute(
                "INSERT INTO relations (source_uid, target_uid, kind) VALUES (?, ?, ?)",
                (rel.source_uid, rel.target_uid, rel.kind),
            )

        self._conn.commit()

    def load_entity_graph(self) -> EntityGraph:
        if not self._conn:
            raise RuntimeError("Store not opened")

        graph = EntityGraph()

        cursor = self._conn.execute("SELECT uid, name, kind, file_path, line, properties FROM entities")
        for row in cursor:
            graph.add_entity(Entity(
                uid=row[0], name=row[1], kind=row[2],
                file_path=row[3], line=row[4],
                properties=json.loads(row[5]) if row[5] else {},
            ))

        cursor = self._conn.execute("SELECT source_uid, target_uid, kind FROM relations")
        for row in cursor:
            graph.add_relation(EntityRelation(
                source_uid=row[0], target_uid=row[1], kind=row[2],
            ))

        return graph

    def set_metadata(self, key: str, value: str) -> None:
        if not self._conn:
            raise RuntimeError("Store not opened")
        self._conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value),
        )
        self._conn.commit()

    def get_metadata(self, key: str) -> str | None:
        if not self._conn:
            raise RuntimeError("Store not opened")
        cursor = self._conn.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_stats(self) -> dict:
        if not self._conn:
            raise RuntimeError("Store not opened")
        entity_count = self._conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        relation_count = self._conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        metadata_count = self._conn.execute("SELECT COUNT(*) FROM metadata").fetchone()[0]
        return {
            "entities": entity_count,
            "relations": relation_count,
            "metadata_keys": metadata_count,
        }

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_store(path: str) -> SCStore:
    return SCStore(path)

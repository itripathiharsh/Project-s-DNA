import json
import uuid
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

from dna.models import Evidence
from dna.storage.db import get_db_session, EvidenceModel

logger = logging.getLogger("dna.evidence.store")

_SCHEMA_SQL_V1 = """
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT,
    file_path TEXT,
    timestamp TEXT NOT NULL
);
PRAGMA user_version = 1;
"""

class EvidenceStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self._session = None
        self._tx_depth = 0
        self._transaction = None
        self._legacy_conns = []

    @property
    def _conn(self):
        import sqlite3
        if not self._legacy_conns:
            conn = sqlite3.connect(self.db_path or "dna_production.db")
            self._legacy_conns.append(conn)
        return self._legacy_conns[0]

    def open(self) -> None:
        import os
        if self.db_path and os.path.exists(self.db_path):
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(evidence)")
                    cols = [c[1] for c in cursor.fetchall()]
                    if cols and "confidence" not in cols:
                        cursor.execute("ALTER TABLE evidence ADD COLUMN confidence REAL DEFAULT 1.0")
                        cursor.execute("PRAGMA user_version = 2")
                        conn.commit()
                finally:
                    conn.close()
            except Exception:
                logger.warning("Failed to migrate evidence schema (ALTER TABLE)")
        self._session = get_db_session(self.db_path)

    def close(self) -> None:
        for conn in self._legacy_conns:
            try:
                conn.close()
            except Exception:
                logger.warning("Failed to close legacy SQLite connection")
        self._legacy_conns.clear()
        if self._session:
            self._session.close()
            self._session = None
        if self.db_path:
            import os
            db_path_or_url = self.db_path
            if "://" not in db_path_or_url:
                db_path_or_url = f"sqlite:///{os.path.abspath(db_path_or_url)}"
            from dna.storage.db import _engines, _sessions
            if db_path_or_url in _engines:
                try:
                    _engines[db_path_or_url].dispose()
                except Exception:
                    logger.warning("Failed to dispose engine for %s", db_path_or_url)
                del _engines[db_path_or_url]
            if db_path_or_url in _sessions:
                del _sessions[db_path_or_url]

    @contextmanager
    def transaction(self):
        """Batching context manager: commits exactly once at the exit of the outermost block."""
        if not self._session:
            raise RuntimeError("Store not opened")
        
        outermost = self._tx_depth == 0
        self._tx_depth += 1
        
        if outermost:
            self._transaction = self._session.begin()
        
        try:
            yield
            if outermost:
                self._transaction.commit()
                self._transaction = None
        except Exception:
            if outermost and self._transaction:
                self._transaction.rollback()
                self._transaction = None
            raise
        finally:
            self._tx_depth -= 1

    def add_evidence(self, evidence_type: str = None, value: object = None, source: str = "",
                      file_path: str = "", **kwargs) -> Evidence:
        if evidence_type is None:
            evidence_type = kwargs.pop('type', None)
        if evidence_type is None:
            raise TypeError('add_evidence missing required argument: evidence_type or type')
        if value is None:
            value = kwargs.pop('value', None) or kwargs.pop('data', None)
        if value is None:
            raise TypeError('add_evidence missing required argument: value (or data)')
            
        if not self._session:
            raise RuntimeError("Store not opened")

        ev_id = str(uuid.uuid4())
        val_str = json.dumps(value) if not isinstance(value, str) else value
        
        # New evidence fields support
        origin = kwargs.get("origin", "")
        engine = kwargs.get("engine", "")
        references = json.dumps(kwargs.get("references", []))
        supporting_metrics = json.dumps(kwargs.get("supporting_metrics", {}))
        graph_references = json.dumps(kwargs.get("graph_references", []))
        source_locations = json.dumps(kwargs.get("source_locations", []))
        line_numbers = json.dumps(kwargs.get("line_numbers", []))
        reasoning_chain = json.dumps(kwargs.get("reasoning_chain", []))
        confidence = float(kwargs.get("confidence", 1.0))

        db_ev = EvidenceModel(
            id=ev_id,
            repo_path=kwargs.get("repo_path", ""),
            type=evidence_type,
            value_json=val_str,
            source=source,
            file_path=file_path,
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=confidence,
            origin=origin,
            engine=engine,
            references_json=references,
            supporting_metrics_json=supporting_metrics,
            graph_references_json=graph_references,
            source_locations_json=source_locations,
            line_numbers_json=line_numbers,
            reasoning_chain_json=reasoning_chain
        )
        
        self._session.add(db_ev)
        
        if self._tx_depth == 0:
            self._session.commit()
            
        # Return standard Evidence dataclass object for backward compatibility
        ev = Evidence(
            id=ev_id,
            type=evidence_type,
            value=val_str,
            source=source,
            file_path=file_path,
            timestamp=db_ev.timestamp
        )
        setattr(ev, "confidence", confidence)
        return ev

    def _map_to_dataclass(self, db_ev: EvidenceModel) -> Evidence:
        ev = Evidence(
            id=db_ev.id,
            type=db_ev.type,
            value=db_ev.value_json,
            source=db_ev.source,
            file_path=db_ev.file_path,
            timestamp=db_ev.timestamp
        )
        setattr(ev, "confidence", db_ev.confidence)
        # Attach extended metadata properties for engines to read
        setattr(ev, "origin", db_ev.origin)
        setattr(ev, "engine", db_ev.engine)
        setattr(ev, "references", json.loads(db_ev.references_json))
        setattr(ev, "supporting_metrics", json.loads(db_ev.supporting_metrics_json))
        setattr(ev, "graph_references", json.loads(db_ev.graph_references_json))
        setattr(ev, "source_locations", json.loads(db_ev.source_locations_json))
        setattr(ev, "line_numbers", json.loads(db_ev.line_numbers_json))
        setattr(ev, "reasoning_chain", json.loads(db_ev.reasoning_chain_json))
        return ev

    def get_by_type(self, evidence_type: str) -> List[Evidence]:
        if not self._session:
            raise RuntimeError("Store not opened")
        results = self._session.query(EvidenceModel).filter_by(type=evidence_type).order_by(EvidenceModel.timestamp.desc()).all()
        return [self._map_to_dataclass(r) for r in results]

    def get_by_source(self, source: str) -> List[Evidence]:
        if not self._session:
            raise RuntimeError("Store not opened")
        results = self._session.query(EvidenceModel).filter_by(source=source).order_by(EvidenceModel.timestamp.desc()).all()
        return [self._map_to_dataclass(r) for r in results]

    def get_by_file(self, file_path: str) -> List[Evidence]:
        if not self._session:
            raise RuntimeError("Store not opened")
        results = self._session.query(EvidenceModel).filter_by(file_path=file_path).order_by(EvidenceModel.timestamp.desc()).all()
        return [self._map_to_dataclass(r) for r in results]

    def get_all(self) -> List[Evidence]:
        if not self._session:
            raise RuntimeError("Store not opened")
        results = self._session.query(EvidenceModel).order_by(EvidenceModel.timestamp.desc()).all()
        return [self._map_to_dataclass(r) for r in results]

    def count(self) -> int:
        if not self._session:
            raise RuntimeError("Store not opened")
        return self._session.query(EvidenceModel).count()

    def clear(self) -> None:
        if not self._session:
            raise RuntimeError("Store not opened")
        self._session.query(EvidenceModel).delete()
        self._session.commit()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self._session:
            self._session.rollback()
        self.close()

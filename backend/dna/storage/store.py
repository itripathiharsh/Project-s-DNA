import json
from typing import Optional
from dna.models import EntityGraph, Entity, EntityRelation
from dna.storage.db import get_db_session, EntityModel, RelationModel, SettingModel

_SCHEMA_SQL_V1 = """
CREATE TABLE IF NOT EXISTS entities (
    uid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line INTEGER DEFAULT 0,
    properties TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS relations (
    source_uid TEXT NOT NULL,
    target_uid TEXT NOT NULL,
    kind TEXT NOT NULL,
    properties TEXT DEFAULT '{}',
    FOREIGN KEY(source_uid) REFERENCES entities(uid),
    FOREIGN KEY(target_uid) REFERENCES entities(uid)
);
PRAGMA user_version = 1;
"""

class SCStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self._session = None

    @property
    def _conn(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path or "dna_production.db")
        if not hasattr(self, "_legacy_conns"):
            self._legacy_conns = []
        self._legacy_conns.append(conn)
        return conn

    def open(self) -> None:
        import os
        if self.db_path and os.path.exists(self.db_path):
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(entities)")
                cols = [c[1] for c in cursor.fetchall()]
                if cols and "hash" not in cols:
                    cursor.execute("ALTER TABLE entities ADD COLUMN hash TEXT DEFAULT ''")
                    cursor.execute("PRAGMA user_version = 2")
                    conn.commit()
                conn.close()
            except Exception:
                pass
        self._session = get_db_session(self.db_path)

    def close(self) -> None:
        if hasattr(self, "_legacy_conns"):
            for conn in self._legacy_conns:
                try:
                    conn.close()
                except Exception:
                    pass
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
                    pass
                del _engines[db_path_or_url]
            if db_path_or_url in _sessions:
                del _sessions[db_path_or_url]

    def save_entity_graph(self, graph: EntityGraph) -> None:
        if not self._session:
            raise RuntimeError("Store not opened")

        # Determine which files are in the new graph to perform incremental deletion of old records
        files_in_new_graph = {e.file_path for e in graph.entities if e.file_path}

        if not files_in_new_graph:
            # Delete all entities and relations
            self._session.query(RelationModel).delete()
            self._session.query(EntityModel).delete()
        else:
            # Delete only the entities and relations associated with the files being updated
            uids_to_delete = [
                row[0] for row in self._session.query(EntityModel.uid)
                .filter(EntityModel.file_path.in_(files_in_new_graph)).all()
            ]
            
            if uids_to_delete:
                self._session.query(RelationModel).filter(
                    (RelationModel.source_uid.in_(uids_to_delete)) | 
                    (RelationModel.target_uid.in_(uids_to_delete))
                ).delete(synchronize_session=False)
                
                self._session.query(EntityModel).filter(
                    EntityModel.file_path.in_(files_in_new_graph)
                ).delete(synchronize_session=False)
        
        self._session.commit()

        # Save new entities
        for entity in graph.entities:
            # Map Entity dataclass to SQLAlchemy EntityModel
            properties_json = json.dumps(entity.properties) if hasattr(entity, "properties") else "{}"
            db_entity = EntityModel(
                uid=entity.uid,
                name=entity.name,
                kind=entity.kind,
                file_path=entity.file_path,
                line=entity.line,
                properties_json=properties_json,
                hash=getattr(entity, "hash", "")
            )
            self._session.add(db_entity)

        self._session.commit()

        # Save relations
        for rel in graph.relations:
            db_relation = RelationModel(
                source_uid=rel.source_uid,
                target_uid=rel.target_uid,
                kind=rel.kind,
                metadata_json="{}"
            )
            self._session.add(db_relation)

        self._session.commit()

    def load_entity_graph(self) -> EntityGraph:
        if not self._session:
            raise RuntimeError("Store not opened")

        graph = EntityGraph()

        # Load all entities
        db_entities = self._session.query(EntityModel).all()
        for e in db_entities:
            props = json.loads(e.properties_json) if e.properties_json else {}
            entity = Entity(
                uid=e.uid,
                name=e.name,
                kind=e.kind,
                file_path=e.file_path,
                line=e.line,
                properties=props
            )
            setattr(entity, "hash", e.hash)
            graph.add_entity(entity)

        # Load all relations
        db_relations = self._session.query(RelationModel).all()
        for r in db_relations:
            graph.add_relation(EntityRelation(
                source_uid=r.source_uid,
                target_uid=r.target_uid,
                kind=r.kind
            ))

        return graph

    def set_metadata(self, key: str, value: str) -> None:
        if not self._session:
            raise RuntimeError("Store not opened")
        # Prefix the metadata key to prevent setting collisions
        meta_key = f"meta_{key}"
        setting = self._session.query(SettingModel).filter_by(key=meta_key).first()
        if not setting:
            setting = SettingModel(key=meta_key)
        setting.value = value
        self._session.add(setting)
        self._session.commit()

    def get_metadata(self, key: str) -> Optional[str]:
        if not self._session:
            raise RuntimeError("Store not opened")
        meta_key = f"meta_{key}"
        setting = self._session.query(SettingModel).filter_by(key=meta_key).first()
        return setting.value if setting else None

    def get_stats(self) -> dict:
        if not self._session:
            raise RuntimeError("Store not opened")
        entity_count = self._session.query(EntityModel).count()
        relation_count = self._session.query(RelationModel).count()
        metadata_count = self._session.query(SettingModel).filter(SettingModel.key.like("meta_%")).count()
        return {
            "entities": entity_count,
            "relations": relation_count,
            "metadata_keys": metadata_count,
        }

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self._session:
            self._session.rollback()
        self.close()


def create_store(path: str) -> SCStore:
    return SCStore(path)

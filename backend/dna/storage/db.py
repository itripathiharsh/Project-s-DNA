import os
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, Index, UniqueConstraint, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.engine import Engine
from dna.config import get_config

logger = logging.getLogger("dna.storage.db")

Base = declarative_base()

# ----------------- Database Setup & Registry -----------------

_engines: Dict[str, Engine] = {}
_sessions: Dict[str, sessionmaker] = {}

def get_database_url() -> str:
    url = os.environ.get("DNA_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if url:
        return url
    
    cfg = get_config()
    db_dir = os.getcwd()
    return f"sqlite:///{os.path.join(db_dir, 'dna_production.db')}"

def clear_db_registry():
    global _engines, _sessions
    for url, engine in list(_engines.items()):
        try:
            engine.dispose()
        except Exception:
            pass
    _engines.clear()
    _sessions.clear()

# Event listener to enforce SQLite foreign keys and WAL mode
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        if hasattr(dbapi_connection, "execute"):
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
    except Exception:
        pass

def get_db_session(db_path_or_url: str = None):
    """
    Returns a SQLAlchemy session. If db_path_or_url is provided, it creates/uses
    a cached sessionmaker for that specific path or URL, ensuring isolation.
    """
    if not db_path_or_url:
        db_path_or_url = get_database_url()

    # Convert simple file paths to sqlite URLs
    if "://" not in db_path_or_url:
        db_path_or_url = f"sqlite:///{os.path.abspath(db_path_or_url)}"

    if db_path_or_url in _sessions:
        return _sessions[db_path_or_url]()

    logger.info("Initializing database registry entry for URL: %s", db_path_or_url)
    
    connect_args = {}
    if db_path_or_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    from sqlalchemy.pool import NullPool
    if db_path_or_url.startswith("sqlite"):
        engine = create_engine(db_path_or_url, connect_args=connect_args, poolclass=NullPool)
    else:
        engine = create_engine(db_path_or_url, connect_args=connect_args, pool_pre_ping=True)
    
    # Enable SQLite pragmas
    if db_path_or_url.startswith("sqlite"):
        # Explicit trigger on connection for test databases
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma_local(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
            except Exception:
                pass

    Base.metadata.create_all(bind=engine)
    if db_path_or_url.startswith("sqlite"):
        try:
            with engine.begin() as conn:
                conn.exec_driver_sql("PRAGMA user_version = 2")
        except Exception:
            pass
    
    sm = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    _engines[db_path_or_url] = engine
    _sessions[db_path_or_url] = sm
    
    return sm()

# ----------------- Declarative Models -----------------

class RepositoryModel(Base):
    __tablename__ = "repositories"
    
    uid = Column(String, primary_key=True)
    path = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    analyzed_at = Column(String, nullable=False)
    total_files = Column(Integer, default=0)
    source_files = Column(Integer, default=0)
    commits = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    metadata_json = Column(Text, default="{}")

    entities = relationship("EntityModel", back_populates="repository", cascade="all, delete-orphan")


class EntityModel(Base):
    __tablename__ = "entities"
    
    uid = Column(String, primary_key=True)
    repo_uid = Column(String, ForeignKey("repositories.uid", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String, nullable=False, index=True)
    kind = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False, index=True)
    line = Column(Integer, default=0)
    properties_json = Column(Text, default="{}")
    hash = Column(String, default="")
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    repository = relationship("RepositoryModel", back_populates="entities")

    __table_args__ = (
        Index("idx_entities_kind_file", "kind", "file_path"),
    )


class RelationModel(Base):
    __tablename__ = "relations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_uid = Column(String, ForeignKey("entities.uid", ondelete="CASCADE"), nullable=False, index=True)
    target_uid = Column(String, ForeignKey("entities.uid", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String, nullable=False, index=True)
    metadata_json = Column(Text, default="{}")

    __table_args__ = (
        UniqueConstraint("source_uid", "target_uid", "kind", name="uq_source_target_kind"),
    )


class EvidenceModel(Base):
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True)
    repo_path = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    value_json = Column(Text, nullable=False)
    source = Column(String, default="", index=True)
    file_path = Column(String, default="", index=True)
    timestamp = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)
    
    origin = Column(String, default="")
    engine = Column(String, default="")
    references_json = Column(Text, default="[]")
    supporting_metrics_json = Column(Text, default="{}")
    graph_references_json = Column(Text, default="[]")
    source_locations_json = Column(Text, default="[]")
    line_numbers_json = Column(Text, default="[]")
    reasoning_chain_json = Column(Text, default="[]")

    __table_args__ = (
        Index("idx_evidence_type_file", "type", "file_path"),
    )


class InsightModel(Base):
    __tablename__ = "insights"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    severity = Column(String, nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    
    supporting_evidence_json = Column(Text, default="[]")
    affected_entities_json = Column(Text, default="[]")
    recommendations_json = Column(Text, default="[]")
    impact = Column(String, default="")
    risk_score = Column(Float, default=0.0)
    visualization_hints_json = Column(Text, default="{}")
    actions_json = Column(Text, default="[]")
    related_insights_json = Column(Text, default="[]")
    
    category = Column(String, default="", index=True)
    file_path = Column(String, default="", index=True)
    evidence_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SettingModel(Base):
    __tablename__ = "settings"
    
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)


class NotificationModel(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    timestamp = Column(String, nullable=False)


class ReviewModel(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    repo_path = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    assignees_json = Column(Text, nullable=False, default="[]")
    files_json = Column(Text, nullable=False, default="[]")
    comments_json = Column(Text, nullable=False, default="[]")
    created_at = Column(String, nullable=False)


class RefactoringPipelineModel(Base):
    __tablename__ = "refactoring_pipelines"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, index=True)
    tasks_json = Column(Text, nullable=False, default="[]")
    impact_report_json = Column(Text, nullable=False, default="{}")
    execution_history_json = Column(Text, nullable=False, default="[]")
    created_at = Column(String, nullable=False)


class OrganizationTeamModel(Base):
    __tablename__ = "organization_teams"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    members_json = Column(Text, nullable=False, default="[]")

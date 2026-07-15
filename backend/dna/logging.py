import contextvars
import json
import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

correlation_id_var = contextvars.ContextVar("correlation_id", default=None)
stage_var = contextvars.ContextVar("stage", default=None)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add correlation ID from contextvar
        cid = correlation_id_var.get()
        if cid:
            log_data["correlation_id"] = cid
        elif hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add stage from contextvar or record
        stage = stage_var.get()
        if stage:
            log_data["stage"] = stage
        elif hasattr(record, "stage"):
            log_data["stage"] = record.stage

        # Add duration_ms if present in record or extra
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        # Add other custom extra attributes
        standard_attrs = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module",
            "msecs", "message", "msg", "name", "pathname", "process",
            "processName", "relativeCreated", "stack_info", "thread",
            "threadName"
        }
        for key, val in record.__dict__.items():
            if key not in standard_attrs and key not in ("stage", "duration_ms", "correlation_id"):
                log_data[key] = val

        return json.dumps(log_data)


def configure_logging(level: str = "INFO"):
    root = logging.getLogger()
    # Clear existing handlers
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


@contextmanager
def correlation_id(cid: Optional[str] = None):
    if not cid:
        cid = str(uuid.uuid4())
    token = correlation_id_var.set(cid)
    try:
        yield cid
    finally:
        correlation_id_var.reset(token)


@contextmanager
def log_stage(stage_name: str):
    token = stage_var.set(stage_name)
    start_time = time.perf_counter()
    logger = logging.getLogger("dna")
    logger.info(f"Starting stage: {stage_name}")
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            f"Completed stage: {stage_name}",
            extra={"duration_ms": round(duration_ms, 2)}
        )
        stage_var.reset(token)

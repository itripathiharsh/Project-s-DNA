import json
import logging
from dna.logging import JSONFormatter, configure_logging, correlation_id, log_stage


def test_json_formatter_basic():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path.py",
        lineno=10,
        msg="Hello World",
        args=(),
        exc_info=None
    )
    res = formatter.format(record)
    data = json.loads(res)
    assert data["level"] == "INFO"
    assert data["message"] == "Hello World"
    assert "timestamp" in data
    assert "correlation_id" not in data
    assert "stage" not in data


def test_json_formatter_with_correlation_id_and_stage():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="test_path.py",
        lineno=10,
        msg="Warning message",
        args=(),
        exc_info=None
    )

    with correlation_id("my-correlation-id"):
        with log_stage("my-stage"):
            res = formatter.format(record)

    data = json.loads(res)
    assert data["level"] == "WARNING"
    assert data["message"] == "Warning message"
    assert data["correlation_id"] == "my-correlation-id"
    assert data["stage"] == "my-stage"


def test_json_formatter_extra_fields():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path.py",
        lineno=10,
        msg="Log message",
        args=(),
        exc_info=None
    )
    record.duration_ms = 12.34
    record.custom_field = "custom_val"

    res = formatter.format(record)
    data = json.loads(res)
    assert data["duration_ms"] == 12.34
    assert data["custom_field"] == "custom_val"


def test_configure_logging():
    configure_logging(level="DEBUG")
    root = logging.getLogger()
    assert len(root.handlers) >= 1
    assert isinstance(root.handlers[0].formatter, JSONFormatter)
    assert root.level == logging.DEBUG


def test_log_stage_duration(caplog):
    caplog.set_level(logging.INFO, logger="dna")

    with log_stage("test_duration"):
        pass

    records = [r for r in caplog.records if r.name == "dna"]
    assert len(records) == 2
    assert records[0].message == "Starting stage: test_duration"
    assert records[1].message == "Completed stage: test_duration"
    assert hasattr(records[1], "duration_ms")
    assert isinstance(records[1].duration_ms, float)

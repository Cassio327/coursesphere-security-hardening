import json
import logging
import os
import sys
import time
import uuid

from flask import g, request
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Info


STANDARD_LOG_FIELDS = {
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "module", "msecs",
    "message", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        event = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
            "instance": os.getenv("INSTANCE_ID", "local"),
        }
        for key, value in record.__dict__.items():
            if key not in STANDARD_LOG_FIELDS and not key.startswith("_"):
                event[key] = value
        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)
        return json.dumps(event, default=str)


def configure_logging():
    root = logging.getLogger()
    if getattr(root, "_coursesphere_configured", False):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    root._coursesphere_configured = True


def register_observability(app):
    registry = CollectorRegistry()
    instance = os.getenv("INSTANCE_ID", "local")
    requests_total = Counter(
        "coursesphere_http_requests_total",
        "Total HTTP requests.",
        ["method", "endpoint", "status", "instance"],
        registry=registry,
    )
    request_duration = Histogram(
        "coursesphere_http_request_duration_seconds",
        "HTTP request duration in seconds.",
        ["method", "endpoint", "instance"],
        buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
        registry=registry,
    )
    in_progress = Gauge(
        "coursesphere_http_requests_in_progress",
        "HTTP requests currently being processed.",
        ["instance"],
        registry=registry,
    )
    build = Info(
        "coursesphere_build",
        "CourseSphere build information.",
        registry=registry,
    )
    build.info({"version": os.getenv("APP_VERSION", "development")})
    app.extensions["prometheus_registry"] = registry

    @app.before_request
    def request_started():
        g.request_started_at = time.perf_counter()
        incoming_request_id = request.headers.get("X-Request-ID", "")
        g.request_id = (
            incoming_request_id[:128]
            if incoming_request_id and incoming_request_id.isprintable()
            else str(uuid.uuid4())
        )
        in_progress.labels(instance=instance).inc()

    @app.after_request
    def request_finished(response):
        duration = time.perf_counter() - g.get(
            "request_started_at", time.perf_counter()
        )
        endpoint = request.endpoint or "unmatched"
        requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(response.status_code),
            instance=instance,
        ).inc()
        request_duration.labels(
            method=request.method, endpoint=endpoint, instance=instance
        ).observe(duration)
        in_progress.labels(instance=instance).dec()
        response.headers["X-Request-ID"] = g.get("request_id", "")
        logging.getLogger("coursesphere.http").info(
            "request_completed",
            extra={
                "request_id": g.get("request_id"),
                "method": request.method,
                "path": request.path,
                "endpoint": endpoint,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )
        return response

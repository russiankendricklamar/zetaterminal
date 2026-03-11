"""
ASGI middleware for tracking requests, errors, and active tasks.

Stores recent requests/errors in ring buffers (in-memory).
Exposes helpers for the admin API to query.
"""
import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_START_TIME = time.time()

MAX_REQUESTS = 500
MAX_ERRORS = 200


@dataclass
class RequestRecord:
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    client_ip: str
    timestamp: float


@dataclass
class ErrorRecord:
    request_id: str
    method: str
    path: str
    status_code: int
    error: str
    traceback_short: str
    client_ip: str
    timestamp: float


@dataclass
class ActiveRequest:
    request_id: str
    method: str
    path: str
    client_ip: str
    started_at: float
    task: asyncio.Task[Any] | None = field(default=None, repr=False)


_recent_requests: deque[RequestRecord] = deque(maxlen=MAX_REQUESTS)
_recent_errors: deque[ErrorRecord] = deque(maxlen=MAX_ERRORS)
_active_requests: dict[str, ActiveRequest] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Rightmost entry = set by the nearest trusted proxy (Render)
        parts = [p.strip() for p in forwarded.split(",")]
        return parts[-1]
    if request.client:
        return request.client.host
    return "unknown"


class RequestTrackerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = uuid.uuid4().hex[:12]
        ip = _client_ip(request)
        method = request.method
        path = request.url.path

        active = ActiveRequest(
            request_id=request_id,
            method=method,
            path=path,
            client_ip=ip,
            started_at=time.time(),
            task=asyncio.current_task(),
        )
        _active_requests[request_id] = active

        start = time.time()
        status_code = 500
        error_msg = ""
        tb_short = ""

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            status_code = 500
            error_msg = f"{type(exc).__name__}: {str(exc)[:200]}"
            tb_short = ""
            raise
        finally:
            duration_ms = round((time.time() - start) * 1000, 2)
            _active_requests.pop(request_id, None)

            _recent_requests.appendleft(RequestRecord(
                request_id=request_id,
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                client_ip=ip,
                timestamp=start,
            ))

            if status_code >= 400:
                _recent_errors.appendleft(ErrorRecord(
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=status_code,
                    error=error_msg or f"HTTP {status_code}",
                    traceback_short=tb_short,
                    client_ip=ip,
                    timestamp=start,
                ))


# ── Public helpers for admin API ──────────────────────────────────────────


def get_recent_requests(
    limit: int = 50,
    status_code: int | None = None,
    path_contains: str | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for r in _recent_requests:
        if status_code is not None and r.status_code != status_code:
            continue
        if path_contains and path_contains not in r.path:
            continue
        results.append({
            "request_id": r.request_id,
            "method": r.method,
            "path": r.path,
            "status_code": r.status_code,
            "duration_ms": r.duration_ms,
            "client_ip": r.client_ip,
            "timestamp": r.timestamp,
        })
        if len(results) >= limit:
            break
    return results


def get_recent_errors(limit: int = 50) -> list[dict[str, Any]]:
    return [
        {
            "request_id": e.request_id,
            "method": e.method,
            "path": e.path,
            "status_code": e.status_code,
            "error": e.error,
            "traceback_short": e.traceback_short,
            "client_ip": e.client_ip,
            "timestamp": e.timestamp,
        }
        for e in list(_recent_errors)[:limit]
    ]


def get_active_requests() -> list[dict[str, Any]]:
    now = time.time()
    return [
        {
            "request_id": a.request_id,
            "method": a.method,
            "path": a.path,
            "client_ip": a.client_ip,
            "elapsed_ms": round((now - a.started_at) * 1000, 2),
        }
        for a in _active_requests.values()
    ]


def cancel_request(request_id: str) -> bool:
    active = _active_requests.get(request_id)
    if not active or not active.task:
        return False
    active.task.cancel()
    return True


def get_uptime_seconds() -> float:
    return round(time.time() - _START_TIME, 1)

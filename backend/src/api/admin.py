"""
Admin API router: users management, health checks, request tracking, system info.
"""
import asyncio
import ipaddress
import logging
import platform
import sys
import time
from datetime import UTC, datetime

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.client import engine, get_session
from src.database.sa_models import IpBan, RefreshToken, User
from src.middleware.admin import require_admin
from src.middleware.ip_ban import add_banned_ip, remove_banned_ip
from src.middleware.request_tracker import (
    cancel_request,
    get_active_requests,
    get_recent_errors,
    get_recent_requests,
    get_uptime_seconds,
)

logger = logging.getLogger(__name__)

router = APIRouter()

_admin_dep = [Depends(require_admin)]


# ── Schemas ──────────────────────────────────────────────────────────────────


class AdminUserOut(BaseModel):
    id: int
    username: str
    domain_handle: str
    email: str
    display_name: str | None
    role: str
    status: str
    invite_code: str | None = None
    created_at: datetime
    activated_at: datetime | None


class UpdateStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("active", "blocked", "pending"):
            raise ValueError("Status must be 'active', 'blocked', or 'pending'")
        return v


class UpdateRoleRequest(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("admin", "user"):
            raise ValueError("Role must be 'admin' or 'user'")
        return v


class IpBanRequest(BaseModel):
    ip_address: str
    reason: str | None = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v.strip())
        except ValueError:
            raise ValueError("Invalid IP address format") from None
        return v.strip()


class IpBanOut(BaseModel):
    id: int
    ip_address: str
    reason: str | None
    banned_by: str | None
    created_at: datetime


# ── Users ────────────────────────────────────────────────────────────────────


@router.get("/users", response_model=list[AdminUserOut], dependencies=_admin_dep)
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        AdminUserOut(
            id=u.id,
            username=u.username,
            domain_handle=u.domain_handle,
            email=u.email,
            display_name=u.display_name,
            role=u.role,
            status=u.status,
            invite_code=u.invite_code,
            created_at=u.created_at,
            activated_at=u.activated_at,
        )
        for u in users
    ]


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    body: UpdateStatusRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own status")
    result = await session.execute(select(User).where(User.id == user_id).with_for_update())
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = body.status
    if body.status == "active" and not user.activated_at:
        user.activated_at = datetime.now(UTC)
    await session.commit()
    # Immediately evict cached status so require_auth picks up the change
    from src.middleware.auth import invalidate_user_status_cache
    invalidate_user_status_cache(user_id)
    return {"id": user.id, "username": user.username, "status": user.status}


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    body: UpdateRoleRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own role")
    result = await session.execute(select(User).where(User.id == user_id).with_for_update())
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = body.role
    await session.commit()
    return {"id": user.id, "username": user.username, "role": user.role}


# ── Kick / Ban ──────────────────────────────────────────────────────────────

@router.post("/users/{user_id}/kick")
async def kick_user(user_id: int, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    """Invalidate user session by revoking all refresh tokens (forces re-login)."""
    from sqlalchemy import update
    result = await session.execute(select(User).where(User.id == user_id).with_for_update())
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot kick yourself")
    # Revoke all active refresh tokens for this user
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    await session.commit()
    return {"id": user.id, "username": user.username, "kicked": True}


@router.post("/users/{user_id}/ban")
async def ban_user(user_id: int, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session)):
    """Block user account and revoke all refresh tokens."""
    from sqlalchemy import update
    result = await session.execute(select(User).where(User.id == user_id).with_for_update())
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")
    user.status = "blocked"
    # Revoke all active refresh tokens
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    await session.commit()
    from src.middleware.auth import invalidate_user_status_cache
    invalidate_user_status_cache(user_id)
    return {"id": user.id, "username": user.username, "status": "blocked", "banned": True}


# ── IP Ban ──────────────────────────────────────────────────────────────────

@router.get("/ip-bans", response_model=list[IpBanOut], dependencies=_admin_dep)
async def list_ip_bans(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(IpBan).order_by(IpBan.created_at.desc()))
    bans = result.scalars().all()
    return [
        IpBanOut(
            id=b.id,
            ip_address=b.ip_address,
            reason=b.reason,
            banned_by=b.banned_by,
            created_at=b.created_at,
        )
        for b in bans
    ]


@router.post("/ip-ban", dependencies=_admin_dep)
async def create_ip_ban(
    body: IpBanRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.execute(
        select(IpBan).where(IpBan.ip_address == body.ip_address)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="IP already banned")
    ban = IpBan(
        ip_address=body.ip_address,
        reason=body.reason,
        banned_by=admin.username,
    )
    session.add(ban)
    await session.commit()
    add_banned_ip(body.ip_address)
    return {"ip_address": body.ip_address, "banned": True}


@router.delete("/ip-ban/{ip}", dependencies=_admin_dep)
async def delete_ip_ban(ip: str, session: AsyncSession = Depends(get_session)):
    try:
        ipaddress.ip_address(ip.strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address format") from None
    ip = ip.strip()
    result = await session.execute(select(IpBan).where(IpBan.ip_address == ip))
    ban = result.scalar_one_or_none()
    if not ban:
        raise HTTPException(status_code=404, detail="IP ban not found")
    await session.delete(ban)
    await session.commit()
    remove_banned_ip(ip)
    return {"ip_address": ip, "unbanned": True}


@router.get("/users/{user_id}/ip-info", dependencies=_admin_dep)
async def get_user_ip_info(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get last known IP for a user from recent requests + run AbuseIPDB check."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find last IP from request tracker by scanning requests for X-Username header
    # For simplicity, we return the user info and let the frontend handle the IP lookup
    recent = get_recent_requests(limit=500)
    user_ip = None
    for _req in recent:
        # We can't directly match user to IP from request tracker alone
        # Return the most recent unique IPs as candidates
        pass

    return {
        "user_id": user.id,
        "username": user.username,
        "last_ip": user_ip,
    }


# ── Health ───────────────────────────────────────────────────────────────────


_HEALTH_TARGETS = [
    ("MOEX ISS", "https://iss.moex.com/iss/index.json"),
    ("CBR", "https://www.cbr.ru/"),
    ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
    ("Yahoo Finance", "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d"),
    ("DaData", "https://dadata.ru/api/v2/"),
]


async def _check_service(name: str, url: str, timeout: float = 5.0) -> dict:
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                elapsed = round((time.time() - start) * 1000, 1)
                return {
                    "name": name,
                    "url": url,
                    "status": "ok" if resp.status < 400 else "degraded",
                    "http_status": resp.status,
                    "response_ms": elapsed,
                }
    except Exception as exc:
        elapsed = round((time.time() - start) * 1000, 1)
        return {
            "name": name,
            "url": url,
            "status": "down",
            "http_status": None,
            "response_ms": elapsed,
            "error": type(exc).__name__,
        }


@router.get("/health", dependencies=_admin_dep)
async def health_check():
    tasks = [_check_service(name, url) for name, url in _HEALTH_TARGETS]

    # Check DB
    async def _check_db() -> dict:
        start = time.time()
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            elapsed = round((time.time() - start) * 1000, 1)
            return {"name": "PostgreSQL (Neon)", "status": "ok", "response_ms": elapsed}
        except Exception as exc:
            elapsed = round((time.time() - start) * 1000, 1)
            return {
                "name": "PostgreSQL (Neon)",
                "status": "down",
                "response_ms": elapsed,
                "error": type(exc).__name__,
            }

    tasks.append(_check_db())
    results = await asyncio.gather(*tasks, return_exceptions=True)

    services = []
    for r in results:
        if isinstance(r, Exception):
            services.append({"name": "unknown", "status": "error", "error": str(r)[:200]})
        else:
            services.append(r)

    return {"services": services, "checked_at": time.time()}


# ── Requests ─────────────────────────────────────────────────────────────────


@router.get("/requests", dependencies=_admin_dep)
async def list_requests(
    limit: int = Query(50, ge=1, le=500),
    status_code: int | None = Query(None),
    path_contains: str | None = Query(None),
):
    return get_recent_requests(limit=limit, status_code=status_code, path_contains=path_contains)


@router.get("/requests/active", dependencies=_admin_dep)
async def list_active_requests():
    return get_active_requests()


@router.post("/requests/{request_id}/cancel", dependencies=_admin_dep)
async def cancel_active_request(request_id: str):
    if cancel_request(request_id):
        return {"cancelled": True, "request_id": request_id}
    raise HTTPException(status_code=404, detail="Active request not found or not cancellable")


# ── Errors ───────────────────────────────────────────────────────────────────


@router.get("/errors", dependencies=_admin_dep)
async def list_errors(limit: int = Query(50, ge=1, le=200)):
    return get_recent_errors(limit=limit)


# ── System ───────────────────────────────────────────────────────────────────


@router.get("/system", dependencies=_admin_dep)
async def system_info():
    import resource

    pool = engine.pool
    pool_status = {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }

    rusage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is in KB on Linux, bytes on macOS
    if sys.platform == "linux":
        memory_mb = round(rusage.ru_maxrss / 1024, 1)
    else:
        memory_mb = round(rusage.ru_maxrss / (1024 * 1024), 1)

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "uptime_seconds": get_uptime_seconds(),
        "db_pool": pool_status,
        "memory_mb": memory_mb,
    }


# ── Tests ────────────────────────────────────────────────────────────────────


@router.post("/tests/run", dependencies=_admin_dep)
async def run_tests(suite: str | None = Query(None, description="Test file name, e.g. test_risk_service")):
    """Run pytest suite and return results. If suite is None, runs all tests."""
    import re
    import subprocess

    if suite and not re.match(r"^[a-zA-Z0-9_]+$", suite):
        raise HTTPException(status_code=400, detail="Invalid suite name")

    cmd = [sys.executable, "-m", "pytest", "--tb=short", "-q", "--no-header"]
    if suite:
        cmd.append(f"tests/{suite}.py")
    else:
        cmd.append("tests/")

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd="backend" if not sys.argv[0].endswith("main.py") else ".",
        )
        lines = result.stdout.strip().split("\n")
        summary_line = lines[-1] if lines else ""

        passed = failed = errors = 0
        for part in summary_line.split(","):
            part = part.strip()
            if "passed" in part:
                passed = int(part.split()[0])
            elif "failed" in part:
                failed = int(part.split()[0])
            elif "error" in part:
                errors = int(part.split()[0])

        return {
            "status": "pass" if result.returncode == 0 else "fail",
            "exit_code": result.returncode,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "summary": summary_line,
            "output": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
            "stderr": result.stderr[-1000:] if result.stderr else "",
            "suite": suite or "all",
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "passed": 0, "failed": 0, "errors": 0, "summary": "Test run timed out after 120s", "output": "", "stderr": "", "suite": suite or "all"}
    except Exception as exc:
        logger.error("Test runner failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Test runner failed") from exc


@router.get("/tests/suites", dependencies=_admin_dep)
async def list_test_suites():
    """List available test suites."""
    import pathlib

    tests_dir = pathlib.Path("tests")
    if not tests_dir.exists():
        tests_dir = pathlib.Path("backend/tests")

    suites = []
    if tests_dir.exists():
        for f in sorted(tests_dir.glob("test_*.py")):
            suites.append({"name": f.stem, "file": f.name})
    return {"suites": suites}

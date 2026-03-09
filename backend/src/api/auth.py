"""
Authentication router: register, activate, login, list users.
"""
import os
import re
import string
import secrets
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

from src.database.client import get_session
from src.database.sa_models import User
from src.middleware.auth import require_api_key

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERNAME_RE = re.compile(r"^[a-zA-Z0-9.\-]{3,30}$")

DOMAIN = "zetaterminal.dev"


def _generate_invite_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


# ── Schemas ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_RE.match(v):
            raise ValueError(
                "Username must be 3-30 chars: latin letters, digits, dot, hyphen"
            )
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class RegisterResponse(BaseModel):
    username: str
    domain_handle: str
    status: str
    message: str


class ActivateRequest(BaseModel):
    code: str


class ActivateResponse(BaseModel):
    username: str
    status: str
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    domain_handle: str
    role: str
    api_key: str


class UserOut(BaseModel):
    id: int
    username: str
    domain_handle: str
    email: str
    display_name: str | None
    role: str
    status: str
    invite_code: str
    created_at: datetime
    activated_at: datetime | None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    import logging as _log
    _logger = _log.getLogger(__name__)
    try:
        # Check username uniqueness
        existing = await session.execute(
            select(User).where(User.username == body.username)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        # Check email uniqueness
        existing_email = await session.execute(
            select(User).where(User.email == body.email)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        domain_handle = f"{body.username}@{DOMAIN}"
        invite_code = _generate_invite_code()

        user = User(
            username=body.username,
            domain_handle=domain_handle,
            email=body.email,
            password_hash=pwd_context.hash(body.password),
            role="user",
            status="pending",
            invite_code=invite_code,
        )
        session.add(user)
        await session.commit()

        return RegisterResponse(
            username=user.username,
            domain_handle=domain_handle,
            status="pending",
            message="Registration successful. Await invite code from admin.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        _logger.error("Register failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Register error: {exc}")


@router.post("/activate", response_model=ActivateResponse)
async def activate(body: ActivateRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(User.invite_code == body.code.strip().upper())
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code",
        )
    if user.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already activated",
        )
    if user.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked",
        )

    user.status = "active"
    user.activated_at = datetime.utcnow()
    await session.commit()

    return ActivateResponse(
        username=user.username,
        status="active",
        message="Account activated successfully. You can now log in.",
    )


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(User.username == body.username.lower())
    )
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if user.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not yet activated. Enter your invite code first.",
        )
    if user.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked",
        )

    api_key = os.getenv("API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform API key not configured",
        )

    return LoginResponse(
        username=user.username,
        domain_handle=user.domain_handle,
        role=user.role,
        api_key=api_key,
    )


class UpdateRoleRequest(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("admin", "user"):
            raise ValueError("Role must be 'admin' or 'user'")
        return v


@router.put("/users/{user_id}/role", dependencies=[Depends(require_api_key)])
async def update_user_role(user_id: int, body: UpdateRoleRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = body.role
    await session.commit()
    return {"id": user.id, "username": user.username, "role": user.role}


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(require_api_key)])
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        UserOut(
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

"""
Authentication router: register, activate, login (JWT), refresh, logout, users, profile.
"""
import logging
import re
import secrets
import string
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.client import get_session
from src.database.sa_models import RefreshToken, User
from src.middleware.admin import require_admin
from src.middleware.auth import require_auth
from src.middleware.rate_limit import limiter
from src.utils.jwt_utils import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    TokenPayload,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)

logger = logging.getLogger(__name__)

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERNAME_RE = re.compile(r"^[a-zA-Z0-9.\-]{3,30}$")

DOMAIN = "zetaterminal.dev"


def _generate_invite_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12))


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
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be 128 characters or fewer")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
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
    user_id: int
    username: str
    domain_handle: str
    role: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    username: str
    domain_handle: str
    email: str
    display_name: str | None
    role: str
    status: str
    created_at: datetime
    activated_at: datetime | None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=RegisterResponse)
@limiter.limit("3/minute")
async def register(request: Request, body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    try:
        existing = await session.execute(
            select(User).where(
                (User.username == body.username) | (User.email == body.email)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already in use",
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
        logger.error("Register failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed") from exc


@router.post("/activate", response_model=ActivateResponse)
@limiter.limit("10/minute")
async def activate(request: Request, body: ActivateRequest, session: AsyncSession = Depends(get_session)):
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
    user.activated_at = datetime.now(UTC)
    user.invite_code = f"USED-{user.id}"
    await session.commit()

    return ActivateResponse(
        username=user.username,
        status="active",
        message="Account activated successfully. You can now log in.",
    )


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(User.username == body.username.lower()).with_for_update()
    )
    user = result.scalar_one_or_none()

    # Account lockout check
    if user and user.locked_until and user.locked_until > datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked. Try again later.",
        )

    if not user or not pwd_context.verify(body.password, user.password_hash):
        # Track failed attempts
        if user:
            user.failed_login_count = (user.failed_login_count or 0) + 1
            if user.failed_login_count >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
            await session.commit()
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

    # Reset lockout on successful login
    user.failed_login_count = 0
    user.locked_until = None

    access_token = create_access_token(user.id, user.username, user.role)
    refresh_token = create_refresh_token(user.id, user.username, user.role)

    # Store refresh token hash in DB
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(rt)
    await session.commit()

    return LoginResponse(
        user_id=user.id,
        username=user.username,
        domain_handle=user.domain_handle,
        role=user.role,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("20/minute")
async def refresh(request: Request, body: RefreshRequest, session: AsyncSession = Depends(get_session)):
    """Exchange a valid refresh token for a new access token."""
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None

    if payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Check token is not revoked and not expired in DB (row lock prevents race condition)
    token_hash = hash_token(body.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            not RefreshToken.revoked,
            RefreshToken.expires_at > datetime.now(UTC),
        ).with_for_update()
    )
    stored_token = result.scalar_one_or_none()
    if not stored_token:
        # Token was valid JWT but not in DB or already revoked — possible reuse attack.
        # Revoke ALL tokens for this user as a safety measure.
        from sqlalchemy import update
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == payload.sub, not RefreshToken.revoked)
            .values(revoked=True)
        )
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or not found",
        )

    # Verify user is still active
    user_result = await session.execute(
        select(User).where(User.id == payload.sub)
    )
    user = user_result.scalar_one_or_none()
    if not user or user.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked or not found",
        )

    # Rotate refresh token: revoke old, issue new
    stored_token.revoked = True

    new_access_token = create_access_token(user.id, user.username, user.role)
    new_refresh_token = create_refresh_token(user.id, user.username, user.role)

    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(new_rt)
    await session.commit()

    return RefreshResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    _payload: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Revoke the refresh token."""
    token_hash = hash_token(body.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == _payload.sub,
        )
    )
    stored_token = result.scalar_one_or_none()
    if stored_token:
        stored_token.revoked = True
        await session.commit()
    return {"message": "Logged out"}


@router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_admin)],
)
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
            created_at=u.created_at,
            activated_at=u.activated_at,
        )
        for u in users
    ]


# ── Profile ─────────────────────────────────────────────────────────────────


class ProfileResponse(BaseModel):
    id: int
    username: str
    domain_handle: str
    email: str
    display_name: str | None
    phone: str | None
    bio: str | None
    role: str
    status: str
    preferences: dict | None
    created_at: datetime
    activated_at: datetime | None


_MAX_PREFERENCES_SIZE = 4096  # bytes


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    bio: str | None = None
    preferences: dict | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("Display name must be 100 characters or fewer")
        return v

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, v: dict | None) -> dict | None:
        if v is not None:
            import json
            serialized = json.dumps(v)
            if len(serialized) > _MAX_PREFERENCES_SIZE:
                raise ValueError(f"Preferences too large (max {_MAX_PREFERENCES_SIZE} bytes)")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None and v.strip():
            cleaned = re.sub(r"[\s\-\(\)]+", "", v.strip())
            if not re.match(r"^\+?\d{7,15}$", cleaned):
                raise ValueError("Invalid phone number")
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("Bio must be 500 characters or fewer")
        return v


@router.get("/me/{username}", response_model=ProfileResponse)
async def get_profile(
    username: str,
    payload: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    # IDOR protection: users can only view their own profile (admins can view any)
    if payload.username != username.lower() and payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    result = await session.execute(
        select(User).where(User.username == username.lower())
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return ProfileResponse(
        id=user.id,
        username=user.username,
        domain_handle=user.domain_handle,
        email=user.email,
        display_name=user.display_name,
        phone=user.phone,
        bio=user.bio,
        role=user.role,
        status=user.status,
        preferences=user.preferences,
        created_at=user.created_at,
        activated_at=user.activated_at,
    )


@router.put("/me/{username}", response_model=ProfileResponse)
async def update_profile(
    username: str,
    body: ProfileUpdateRequest,
    payload: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    # IDOR protection: users can only edit their own profile (admins can edit any)
    if payload.username != username.lower() and payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    result = await session.execute(
        select(User).where(User.username == username.lower())
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.display_name is not None:
        user.display_name = body.display_name
    if body.email is not None:
        existing = await session.execute(
            select(User).where(User.email == body.email, User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = body.email
    if body.phone is not None:
        user.phone = body.phone
    if body.bio is not None:
        user.bio = body.bio
    if body.preferences is not None:
        user.preferences = body.preferences

    await session.commit()
    await session.refresh(user)

    return ProfileResponse(
        id=user.id,
        username=user.username,
        domain_handle=user.domain_handle,
        email=user.email,
        display_name=user.display_name,
        phone=user.phone,
        bio=user.bio,
        role=user.role,
        status=user.status,
        preferences=user.preferences,
        created_at=user.created_at,
        activated_at=user.activated_at,
    )

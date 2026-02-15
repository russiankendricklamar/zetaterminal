"""
Platform Services Router — Auth, Email, Storage, Media, Business, Developer

Prefix: /api/platform
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from src.services.platform_services_service import (
    # Auth
    auth0_get_token,
    stytch_authenticate,
    mojoauth_send_magic_link,
    warrant_check,
    warrant_create,
    # Email
    sendgrid_send,
    mailcheck_validate,
    # Storage
    jsonbin_create,
    jsonbin_read,
    jsonbin_update,
    pantry_get_basket,
    pantry_create_item,
    pastebin_create,
    # Media
    cloudinary_upload,
    cloudinary_list_resources,
    cloudconvert_create_job,
    cloudconvert_get_job,
    # Business
    lob_verify_address,
    vatlayer_validate,
    klarna_create_session,
    # Developer
    github_list_repos,
    github_repo_details,
    github_repo_issues,
    httpbin_get,
    httpbin_post,
    # Health
    platform_health,
)

router = APIRouter()


# ─── Auth ────────────────────────────────────────────────────────────────────

class Auth0TokenRequest(BaseModel):
    audience: str
    grant_type: str = "client_credentials"


@router.post("/auth/auth0/token")
async def auth0_token(req: Auth0TokenRequest):
    try:
        return await auth0_get_token(req.audience, req.grant_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StytchAuthRequest(BaseModel):
    method: str = "magic_link"
    token: str


@router.post("/auth/stytch/authenticate")
async def stytch_auth(req: StytchAuthRequest):
    try:
        return await stytch_authenticate(req.method, req.token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MojoAuthRequest(BaseModel):
    email: str


@router.post("/auth/mojoauth/send-link")
async def mojoauth_link(req: MojoAuthRequest):
    try:
        return await mojoauth_send_magic_link(req.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WarrantCheckRequest(BaseModel):
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str


@router.post("/auth/warrant/check")
async def warrant_check_endpoint(req: WarrantCheckRequest):
    try:
        return await warrant_check(
            req.object_type, req.object_id, req.relation,
            req.subject_type, req.subject_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/warrant/create-warrant")
async def warrant_create_endpoint(req: WarrantCheckRequest):
    try:
        return await warrant_create(
            req.object_type, req.object_id, req.relation,
            req.subject_type, req.subject_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Email ───────────────────────────────────────────────────────────────────

class SendEmailRequest(BaseModel):
    to_email: str
    from_email: str
    subject: str
    content: str
    content_type: str = "text/plain"


@router.post("/email/send")
async def send_email(req: SendEmailRequest):
    try:
        return await sendgrid_send(
            req.to_email, req.from_email, req.subject,
            req.content, req.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email/validate/{email}")
async def validate_email(email: str):
    try:
        return await mailcheck_validate(email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Storage ─────────────────────────────────────────────────────────────────

class JsonBinCreateRequest(BaseModel):
    data: Any
    name: Optional[str] = None


@router.post("/storage/jsonbin/create")
async def jb_create(req: JsonBinCreateRequest):
    try:
        return await jsonbin_create(req.data, req.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage/jsonbin/{bin_id}")
async def jb_read(bin_id: str):
    try:
        return await jsonbin_read(bin_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class JsonBinUpdateRequest(BaseModel):
    data: Any


@router.put("/storage/jsonbin/{bin_id}")
async def jb_update(bin_id: str, req: JsonBinUpdateRequest):
    try:
        return await jsonbin_update(bin_id, req.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage/pantry/{basket}")
async def pantry_basket(basket: str):
    try:
        return await pantry_get_basket(basket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PantryItemRequest(BaseModel):
    data: Any


@router.post("/storage/pantry/{basket}/{key}")
async def pantry_item(basket: str, key: str, req: PantryItemRequest):
    try:
        return await pantry_create_item(key, req.data, basket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PastebinRequest(BaseModel):
    content: str
    title: Optional[str] = None
    syntax: str = "text"
    expiration: str = "1M"


@router.post("/storage/pastebin/create")
async def pb_create(req: PastebinRequest):
    try:
        return await pastebin_create(req.content, req.title, req.syntax, req.expiration)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Media ───────────────────────────────────────────────────────────────────

class CloudinaryUploadRequest(BaseModel):
    file_url: str
    folder: str = ""


@router.post("/media/cloudinary/upload")
async def cloud_upload(req: CloudinaryUploadRequest):
    try:
        return await cloudinary_upload(req.file_url, req.folder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/media/cloudinary/resources")
async def cloud_resources(resource_type: str = "image", max_results: int = 30):
    try:
        return await cloudinary_list_resources(resource_type, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CloudConvertRequest(BaseModel):
    input_url: str
    input_format: str
    output_format: str


@router.post("/media/cloudconvert/convert")
async def cc_convert(req: CloudConvertRequest):
    try:
        return await cloudconvert_create_job(req.input_url, req.input_format, req.output_format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/media/cloudconvert/job/{job_id}")
async def cc_job(job_id: str):
    try:
        return await cloudconvert_get_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Business ────────────────────────────────────────────────────────────────

class LobAddressRequest(BaseModel):
    line1: str
    city: str
    state: str
    zip_code: str
    country: str = "US"


@router.post("/business/lob/verify-address")
async def lob_verify(req: LobAddressRequest):
    try:
        return await lob_verify_address(
            req.line1, req.city, req.state, req.zip_code, req.country,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business/vat/validate")
async def vat_validate(vat_number: str):
    try:
        return await vatlayer_validate(vat_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class KlarnaSessionRequest(BaseModel):
    purchase_country: str
    purchase_currency: str
    locale: str
    order_amount: int
    order_lines: List[Dict[str, Any]]


@router.post("/business/klarna/create-session")
async def klarna_session(req: KlarnaSessionRequest):
    try:
        return await klarna_create_session(
            req.purchase_country, req.purchase_currency,
            req.locale, req.order_amount, req.order_lines,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Developer ───────────────────────────────────────────────────────────────

@router.get("/dev/github/repos/{owner}")
async def gh_repos(owner: str):
    try:
        return await github_list_repos(owner)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dev/github/repo/{owner}/{repo}")
async def gh_repo(owner: str, repo: str):
    try:
        return await github_repo_details(owner, repo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dev/github/repo/{owner}/{repo}/issues")
async def gh_issues(owner: str, repo: str, state: str = "open", per_page: int = 20):
    try:
        return await github_repo_issues(owner, repo, state, per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dev/httpbin/get")
async def hb_get():
    try:
        return await httpbin_get()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class HttpbinPostRequest(BaseModel):
    payload: Any = {}


@router.post("/dev/httpbin/post")
async def hb_post(req: HttpbinPostRequest):
    try:
        return await httpbin_post(req.payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Health ──────────────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return await platform_health()

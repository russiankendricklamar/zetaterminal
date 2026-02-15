"""
Platform Services — Auth, Email, Storage, Media, Business, Developer

Consolidated utility services for infrastructure and platform integrations.
"""

import os
from typing import Dict, Any, List, Optional
import aiohttp

from src.services.cache_service import cache_get, cache_set, make_cache_key

# ─── Env Keys ────────────────────────────────────────────────────────────────

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")
WARRANT_API_KEY = os.getenv("WARRANT_API_KEY", "")
STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID", "")
STYTCH_SECRET = os.getenv("STYTCH_SECRET", "")
MOJOAUTH_API_KEY = os.getenv("MOJOAUTH_API_KEY", "")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
MAILBOXVALIDATOR_KEY = os.getenv("MAILBOXVALIDATOR_API_KEY", "")

JSONBIN_ACCESS_KEY = os.getenv("JSONBIN_ACCESS_KEY", "")
JSONBIN_MASTER_KEY = os.getenv("JSONBIN_MASTER_KEY", "")
PANTRY_BASKET_ID = os.getenv("PANTRY_BASKET_ID", "")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY", "")

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY", "")

LOB_API_KEY = os.getenv("LOB_API_KEY", "")
VATLAYER_API_KEY = os.getenv("VATLAYER_API_KEY", "")
KLARNA_API_USERNAME = os.getenv("KLARNA_API_USERNAME", "")
KLARNA_API_PASSWORD = os.getenv("KLARNA_API_PASSWORD", "")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

async def auth0_get_token(audience: str, grant_type: str = "client_credentials") -> Dict[str, Any]:
    """Exchange credentials for an Auth0 access token."""
    body = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": audience,
        "grant_type": grant_type,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            json=body,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {
        "access_token": data.get("access_token", ""),
        "token_type": data.get("token_type", ""),
        "expires_in": data.get("expires_in", 0),
        "provider": "auth0",
    }


async def stytch_authenticate(method: str, token: str) -> Dict[str, Any]:
    """Authenticate via Stytch (magic_link or otp)."""
    import base64
    auth_str = base64.b64encode(f"{STYTCH_PROJECT_ID}:{STYTCH_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_str}", "Content-Type": "application/json"}

    endpoint_map = {
        "magic_link": "magic_links/authenticate",
        "otp": "otps/authenticate",
    }
    endpoint = endpoint_map.get(method, "magic_links/authenticate")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.stytch.com/v1/{endpoint}",
            headers=headers,
            json={"token": token},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    return {
        "user_id": data.get("user_id", ""),
        "session_token": data.get("session_token", ""),
        "status_code": data.get("status_code", 0),
        "provider": "stytch",
    }


async def mojoauth_send_magic_link(email: str) -> Dict[str, Any]:
    """Send passwordless magic link via MojoAuth."""
    headers = {"api_key": MOJOAUTH_API_KEY}
    params = {"email": email}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.mojoauth.com/users/magiclink",
            headers=headers,
            params=params,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {
        "state_id": data.get("state_id", ""),
        "provider": "mojoauth",
    }


async def warrant_check(
    object_type: str, object_id: str, relation: str, subject_type: str, subject_id: str
) -> Dict[str, Any]:
    """Check an authorization warrant."""
    headers = {"Authorization": f"ApiKey {WARRANT_API_KEY}", "Content-Type": "application/json"}
    body = {
        "warrants": [{
            "objectType": object_type,
            "objectId": object_id,
            "relation": relation,
            "subject": {"objectType": subject_type, "objectId": subject_id},
        }]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.warrant.dev/v2/check",
            headers=headers,
            json=body,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {
        "result": data.get("result", ""),
        "is_authorized": data.get("result", "") == "Authorized",
        "provider": "warrant",
    }


async def warrant_create(
    object_type: str, object_id: str, relation: str, subject_type: str, subject_id: str
) -> Dict[str, Any]:
    """Create an authorization warrant."""
    headers = {"Authorization": f"ApiKey {WARRANT_API_KEY}", "Content-Type": "application/json"}
    body = {
        "objectType": object_type,
        "objectId": object_id,
        "relation": relation,
        "subject": {"objectType": subject_type, "objectId": subject_id},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.warrant.dev/v2/warrants",
            headers=headers,
            json=body,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {**data, "provider": "warrant"}


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL
# ═══════════════════════════════════════════════════════════════════════════════

async def sendgrid_send(
    to_email: str, from_email: str, subject: str, content: str, content_type: str = "text/plain"
) -> Dict[str, Any]:
    """Send email via Sendgrid."""
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": content_type, "value": content}],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers=headers,
            json=body,
        ) as resp:
            if resp.status in (200, 201, 202):
                return {"status": "sent", "provider": "sendgrid"}
            resp.raise_for_status()
            return {"status": "error", "provider": "sendgrid"}


async def mailcheck_validate(email: str) -> Dict[str, Any]:
    """Validate email via Mailcheck.ai (free) or MailboxValidator."""
    # Try free Mailcheck.ai first
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.mailcheck.ai/email/{email}") as resp:
            if resp.ok:
                data = await resp.json(content_type=None)
                return {
                    "email": email,
                    "status": data.get("status", ""),
                    "disposable": data.get("disposable", False),
                    "mx": data.get("mx", False),
                    "provider": "mailcheck",
                }

    # Fallback to MailboxValidator
    if MAILBOXVALIDATOR_KEY:
        params = {"key": MAILBOXVALIDATOR_KEY, "email": email}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.mailboxvalidator.com/v1/validation/single",
                params=params,
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                return {
                    "email": email,
                    "status": data.get("status", ""),
                    "is_disposable": data.get("is_disposable", ""),
                    "is_free": data.get("is_free", ""),
                    "provider": "mailboxvalidator",
                }

    return {"email": email, "status": "unknown", "provider": "none"}


# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

async def jsonbin_create(data: Any, name: Optional[str] = None) -> Dict[str, Any]:
    """Create a JSON bin."""
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "X-Access-Key": JSONBIN_ACCESS_KEY,
    }
    if JSONBIN_MASTER_KEY:
        headers["X-Master-Key"] = JSONBIN_MASTER_KEY
    if name:
        headers["X-Bin-Name"] = name

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.jsonbin.io/v3/b",
            headers=headers,
            json=data,
        ) as resp:
            resp.raise_for_status()
            result = await resp.json(content_type=None)
    meta = result.get("metadata", {})
    return {
        "id": meta.get("id", ""),
        "name": meta.get("name", ""),
        "created_at": meta.get("createdAt", ""),
        "provider": "jsonbin",
    }


async def jsonbin_read(bin_id: str) -> Dict[str, Any]:
    """Read a JSON bin."""
    key = make_cache_key("jsonbin", bin_id)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {"X-Access-Key": JSONBIN_ACCESS_KEY}
    if JSONBIN_MASTER_KEY:
        headers["X-Master-Key"] = JSONBIN_MASTER_KEY

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.jsonbin.io/v3/b/{bin_id}/latest",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            result = await resp.json(content_type=None)

    data = {"record": result.get("record", {}), "provider": "jsonbin"}
    cache_set(key, data, ttl_seconds=300)
    return data


async def jsonbin_update(bin_id: str, data: Any) -> Dict[str, Any]:
    """Update a JSON bin."""
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "X-Access-Key": JSONBIN_ACCESS_KEY,
    }
    if JSONBIN_MASTER_KEY:
        headers["X-Master-Key"] = JSONBIN_MASTER_KEY

    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"https://api.jsonbin.io/v3/b/{bin_id}",
            headers=headers,
            json=data,
        ) as resp:
            resp.raise_for_status()
            result = await resp.json(content_type=None)
    meta = result.get("metadata", {})
    return {
        "id": meta.get("id", ""),
        "version": meta.get("version", 0),
        "provider": "jsonbin",
    }


async def pantry_get_basket(basket_id: Optional[str] = None) -> Dict[str, Any]:
    """Get pantry basket contents."""
    bid = basket_id or PANTRY_BASKET_ID
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://getpantry.cloud/apiv1/pantry/{bid}") as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {**data, "provider": "pantry"}


async def pantry_create_item(
    key: str, data: Any, basket_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create or update a pantry item."""
    bid = basket_id or PANTRY_BASKET_ID
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://getpantry.cloud/apiv1/pantry/{bid}/basket/{key}",
            json=data,
        ) as resp:
            resp.raise_for_status()
            return {"status": "ok", "key": key, "provider": "pantry"}


async def pastebin_create(
    content: str,
    title: Optional[str] = None,
    syntax: str = "text",
    expiration: str = "1M",
) -> Dict[str, Any]:
    """Create a paste on Pastebin."""
    form = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": content,
        "api_paste_format": syntax,
        "api_paste_expire_date": expiration,
    }
    if title:
        form["api_paste_name"] = title

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://pastebin.com/api/api_post.php",
            data=form,
        ) as resp:
            resp.raise_for_status()
            text = await resp.text()
    return {"paste_url": text.strip(), "provider": "pastebin"}


# ═══════════════════════════════════════════════════════════════════════════════
# MEDIA
# ═══════════════════════════════════════════════════════════════════════════════

async def cloudinary_upload(file_url: str, folder: str = "") -> Dict[str, Any]:
    """Upload an image/file to Cloudinary via URL."""
    import hashlib
    import time

    timestamp = str(int(time.time()))
    params_str = f"folder={folder}&timestamp={timestamp}{CLOUDINARY_API_SECRET}"
    signature = hashlib.sha1(params_str.encode()).hexdigest()

    form = aiohttp.FormData()
    form.add_field("file", file_url)
    form.add_field("folder", folder)
    form.add_field("timestamp", timestamp)
    form.add_field("api_key", CLOUDINARY_API_KEY)
    form.add_field("signature", signature)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload",
            data=form,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    return {
        "public_id": data.get("public_id", ""),
        "url": data.get("secure_url", ""),
        "format": data.get("format", ""),
        "width": data.get("width", 0),
        "height": data.get("height", 0),
        "bytes": data.get("bytes", 0),
        "provider": "cloudinary",
    }


async def cloudinary_list_resources(
    resource_type: str = "image", max_results: int = 30
) -> Dict[str, Any]:
    """List Cloudinary resources."""
    import base64

    auth = base64.b64encode(f"{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    params = {"max_results": str(max_results)}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/resources/{resource_type}",
            headers=headers,
            params=params,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    resources = data.get("resources", [])
    return {
        "resources": [
            {
                "public_id": r.get("public_id", ""),
                "url": r.get("secure_url", ""),
                "format": r.get("format", ""),
                "bytes": r.get("bytes", 0),
                "created_at": r.get("created_at", ""),
            }
            for r in resources
        ],
        "total": len(resources),
        "provider": "cloudinary",
    }


async def cloudconvert_create_job(
    input_url: str, input_format: str, output_format: str
) -> Dict[str, Any]:
    """Start a file conversion job on CloudConvert."""
    headers = {
        "Authorization": f"Bearer {CLOUDCONVERT_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "tasks": {
            "import-file": {"operation": "import/url", "url": input_url},
            "convert": {
                "operation": "convert",
                "input": ["import-file"],
                "input_format": input_format,
                "output_format": output_format,
            },
            "export-file": {
                "operation": "export/url",
                "input": ["convert"],
            },
        },
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.cloudconvert.com/v2/jobs",
            headers=headers,
            json=body,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    job = data.get("data", {})
    return {
        "job_id": job.get("id", ""),
        "status": job.get("status", ""),
        "created_at": job.get("created_at", ""),
        "provider": "cloudconvert",
    }


async def cloudconvert_get_job(job_id: str) -> Dict[str, Any]:
    """Check CloudConvert job status."""
    headers = {"Authorization": f"Bearer {CLOUDCONVERT_API_KEY}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.cloudconvert.com/v2/jobs/{job_id}",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    job = data.get("data", {})
    tasks = job.get("tasks", [])
    export_task = next((t for t in tasks if t.get("operation") == "export/url"), None)

    result: Dict[str, Any] = {
        "job_id": job.get("id", ""),
        "status": job.get("status", ""),
        "provider": "cloudconvert",
    }

    if export_task and export_task.get("result", {}).get("files"):
        files = export_task["result"]["files"]
        result["files"] = [{"filename": f.get("filename", ""), "url": f.get("url", "")} for f in files]

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# BUSINESS
# ═══════════════════════════════════════════════════════════════════════════════

async def lob_verify_address(
    line1: str, city: str, state: str, zip_code: str, country: str = "US"
) -> Dict[str, Any]:
    """Verify a postal address via Lob.com."""
    import base64

    auth = base64.b64encode(f"{LOB_API_KEY}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    body = {
        "primary_line": line1,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": country,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.lob.com/v1/us_verifications",
            headers=headers,
            json=body,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    return {
        "primary_line": data.get("primary_line", ""),
        "city": data.get("components", {}).get("city", ""),
        "state": data.get("components", {}).get("state", ""),
        "zip_code": data.get("components", {}).get("zip_code", ""),
        "deliverability": data.get("deliverability", ""),
        "provider": "lob",
    }


async def vatlayer_validate(vat_number: str) -> Dict[str, Any]:
    """Validate a VAT number via vatlayer."""
    key = make_cache_key("vat", vat_number)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"access_key": VATLAYER_API_KEY, "vat_number": vat_number}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://apilayer.net/api/validate",
            params=params,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    result = {
        "valid": data.get("valid", False),
        "country_code": data.get("country_code", ""),
        "vat_number": data.get("vat_number", ""),
        "company_name": data.get("company_name", ""),
        "company_address": data.get("company_address", ""),
        "provider": "vatlayer",
    }
    cache_set(key, result, ttl_seconds=86400)
    return result


async def klarna_create_session(
    purchase_country: str,
    purchase_currency: str,
    locale: str,
    order_amount: int,
    order_lines: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Create a Klarna checkout session."""
    import base64

    auth = base64.b64encode(f"{KLARNA_API_USERNAME}:{KLARNA_API_PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    body = {
        "purchase_country": purchase_country,
        "purchase_currency": purchase_currency,
        "locale": locale,
        "order_amount": order_amount,
        "order_lines": order_lines,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.klarna.com/checkout/v3/orders",
            headers=headers,
            json=body,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    return {
        "order_id": data.get("order_id", ""),
        "status": data.get("status", ""),
        "html_snippet": data.get("html_snippet", ""),
        "provider": "klarna",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPER
# ═══════════════════════════════════════════════════════════════════════════════

async def github_list_repos(owner: str) -> Dict[str, Any]:
    """List GitHub repos for a user/org."""
    key = make_cache_key("gh", "repos", owner)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.github.com/users/{owner}/repos",
            headers=headers,
            params={"per_page": "30", "sort": "updated"},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    repos = [
        {
            "name": r.get("name", ""),
            "full_name": r.get("full_name", ""),
            "description": r.get("description", ""),
            "language": r.get("language", ""),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "updated_at": r.get("updated_at", ""),
            "html_url": r.get("html_url", ""),
        }
        for r in data
    ]
    result = {"repos": repos, "total": len(repos), "provider": "github"}
    cache_set(key, result, ttl_seconds=600)
    return result


async def github_repo_details(owner: str, repo: str) -> Dict[str, Any]:
    """Get GitHub repo details."""
    key = make_cache_key("gh", "repo", owner, repo)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    result = {
        "name": data.get("name", ""),
        "full_name": data.get("full_name", ""),
        "description": data.get("description", ""),
        "language": data.get("language", ""),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "license": (data.get("license") or {}).get("spdx_id", ""),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
        "html_url": data.get("html_url", ""),
        "provider": "github",
    }
    cache_set(key, result, ttl_seconds=600)
    return result


async def github_repo_issues(
    owner: str, repo: str, state: str = "open", per_page: int = 20
) -> Dict[str, Any]:
    """List GitHub repo issues."""
    key = make_cache_key("gh", "issues", owner, repo, state)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers=headers,
            params={"state": state, "per_page": str(per_page)},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    issues = [
        {
            "number": i.get("number", 0),
            "title": i.get("title", ""),
            "state": i.get("state", ""),
            "user": i.get("user", {}).get("login", ""),
            "created_at": i.get("created_at", ""),
            "html_url": i.get("html_url", ""),
            "labels": [l.get("name", "") for l in i.get("labels", [])],
        }
        for i in data
    ]
    result = {"issues": issues, "total": len(issues), "provider": "github"}
    cache_set(key, result, ttl_seconds=300)
    return result


async def httpbin_get() -> Dict[str, Any]:
    """HTTP testing — GET via httpbin."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://httpbin.org/get") as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {**data, "provider": "httpbin"}


async def httpbin_post(payload: Any) -> Dict[str, Any]:
    """HTTP testing — POST via httpbin."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://httpbin.org/post",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    return {**data, "provider": "httpbin"}


# ─── Health ──────────────────────────────────────────────────────────────────

async def platform_health() -> Dict[str, Any]:
    """Check platform service health."""
    return {"status": "ok", "service": "platform"}

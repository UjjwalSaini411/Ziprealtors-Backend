import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Simple in-memory token cache
_cache = {"access_token": None, "expires_at": 0, "instance_url": None}

SF_AUTH_TIMEOUT = 20
SF_API_TIMEOUT = 30


def _require_creds():
    missing = [k for k in ("SF_CLIENT_ID", "SF_CLIENT_SECRET", "SF_USERNAME", "SF_PASSWORD", "SF_LOGIN_BASE_URL")
               if not getattr(settings, k, None)]
    if missing:
        raise RuntimeError(f"Missing Salesforce credentials/settings: {', '.join(missing)}")


def _fetch_token():
    _require_creds()
    url = f"{settings.SF_LOGIN_BASE_URL.rstrip('/')}/services/oauth2/token"
    data = {
        "grant_type": "password",
        "client_id": settings.SF_CLIENT_ID,
        "client_secret": settings.SF_CLIENT_SECRET,
        "username": settings.SF_USERNAME,
        "password": settings.SF_PASSWORD,  # append security token to password if your org requires
    }

    try:
        r = requests.post(url, data=data, timeout=SF_AUTH_TIMEOUT)
    except requests.RequestException as e:
        raise RuntimeError(f"Cannot reach Salesforce auth endpoint: {e}") from e

    if not r.ok:
        # Log SF error body for diagnosis, but raise a concise error upward
        logger.error("Salesforce auth failed (%s): %s", r.status_code, r.text[:1000])
        raise RuntimeError(f"Salesforce authentication failed (HTTP {r.status_code})")

    j = r.json()
    instance_url = j.get("instance_url") or getattr(settings, "SF_INSTANCE_URL", None)
    if not instance_url:
        raise RuntimeError("Salesforce auth did not return instance_url; set SF_INSTANCE_URL as fallback")

    _cache.update({
        "access_token": j["access_token"],
        "instance_url": instance_url.rstrip("/"),
        "expires_at": time.time() + 3600,  # token TTL; adjust if your org differs
    })
    return _cache["access_token"], _cache["instance_url"]


def _token():
    # Refresh 30s before expiry for safety
    if _cache["access_token"] and time.time() < _cache["expires_at"] - 30:
        return _cache["access_token"], _cache["instance_url"]
    return _fetch_token()


def _join_url(base: str, path: str) -> str:
    base = (base or "").rstrip("/")
    path = (path or "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def create_enquiry(payload: dict) -> dict:
    """
    Sends an enquiry payload to Salesforce.
    - Retries once on 401/403 by refreshing the token.
    - Returns JSON if available; otherwise returns a dict with raw text.
    - Handles 204/empty body gracefully.
    """
    token, instance = _token()
    endpoint = getattr(settings, "SF_ENQUIRY_ENDPOINT", None)
    if not endpoint:
        raise RuntimeError("SF_ENQUIRY_ENDPOINT not configured")
    if not instance:
        raise RuntimeError("Salesforce instance URL not available")

    url = _join_url(instance, endpoint)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def _post():
        try:
            return requests.post(url, json=payload, headers=headers, timeout=SF_API_TIMEOUT)
        except requests.RequestException as e:
            raise RuntimeError(f"Error calling Salesforce enquiry endpoint: {e}") from e

    r = _post()

    # Retry once on auth failures
    if r.status_code in (401, 403):
        token, instance = _fetch_token()
        headers["Authorization"] = f"Bearer {token}"
        r = _post()

    content_type = (r.headers.get("Content-Type") or "").lower()
    body_snippet = (r.text or "")[:1000]

    if not r.ok:
        # Try to parse JSON error details; fall back to raw text
        try:
            err_json = r.json()
        except ValueError:
            err_json = {"raw": body_snippet, "content_type": content_type}
        logger.error("Salesforce enquiry failed %s: %s", r.status_code, body_snippet)
        raise RuntimeError(f"Salesforce enquiry failed (HTTP {r.status_code})", err_json)

    # 204 No Content or empty body → return minimal success
    if r.status_code == 204 or not r.content:
        return {"status": "ok", "message": "No content from Salesforce", "http_status": r.status_code}

    # Try JSON; if not JSON, return raw
    try:
        return r.json()
    except ValueError:
        logger.warning(
            "Salesforce returned non-JSON success (status %s, content_type=%s): %s",
            r.status_code, content_type, body_snippet
        )
        return {
            "status": "ok",
            "http_status": r.status_code,
            "content_type": content_type,
            "raw": r.text,
        }

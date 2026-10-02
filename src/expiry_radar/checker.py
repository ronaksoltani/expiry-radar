from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import requests


def days_until(expiry: datetime, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return (expiry.astimezone(timezone.utc) - current.astimezone(timezone.utc)).days


def normalize_host(value: str) -> str:
    candidate = value.strip()
    parsed = urlparse(candidate if "://" in candidate else f"//{candidate}")
    host = parsed.hostname
    if not host or "/" in host or ".." in host:
        raise ValueError(f"invalid hostname: {value}")
    return host.encode("idna").decode("ascii").lower()


def check_tls(host: str, timeout: float = 5.0) -> dict[str, object]:
    context = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=timeout) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
            certificate = tls_socket.getpeercert()
    expiry = datetime.strptime(certificate["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    return {"expires_at": expiry.isoformat(), "days_remaining": days_until(expiry)}


def check_registration(host: str, timeout: float = 8.0) -> dict[str, object]:
    response = requests.get(f"https://rdap.org/domain/{quote(host, safe='.-')}", timeout=timeout,
                            headers={"Accept": "application/rdap+json", "User-Agent": "ExpiryRadar/1.0"})
    if response.status_code in {404, 501}:
        return {"expires_at": None, "days_remaining": None, "status": "unavailable"}
    response.raise_for_status()
    payload = response.json()
    events = payload.get("events", [])
    expiration = next((event.get("eventDate") for event in events
                       if "expir" in event.get("eventAction", "").lower()), None)
    if not expiration:
        return {"expires_at": None, "days_remaining": None, "status": "not-published"}
    parsed = datetime.fromisoformat(expiration.replace("Z", "+00:00"))
    return {"expires_at": parsed.isoformat(), "days_remaining": days_until(parsed), "status": "ok"}


def inspect_domain(value: str) -> dict[str, object]:
    host = normalize_host(value)
    result: dict[str, object] = {"domain": host}
    for key, check in (("tls", check_tls), ("registration", check_registration)):
        try:
            result[key] = check(host)
        except Exception as error:
            result[key] = {"status": "error", "message": f"{type(error).__name__}: {error}"}
    return result

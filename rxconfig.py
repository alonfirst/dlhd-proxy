import os
from dataclasses import dataclass
from urllib.parse import urlparse


def _bool_env(name: str, default: str = "FALSE") -> bool:
    return os.environ.get(name, default).strip().upper() == "TRUE"


def _api_url() -> str:
    raw = os.environ.get("API_URL", "").strip()
    if raw:
        parsed = urlparse(raw)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("API_URL must include a valid http(s) scheme and host")
        return raw.rstrip("/")

    port = os.environ.get("PORT", "3000").strip()
    if port and port.isdigit():
        return f"http://localhost:{port}"
    return "http://localhost:3000"


def _flaresolverr_url() -> str:
    raw = os.environ.get("FLARESOLVERR_URL", "").strip()
    if not raw:
        return ""

    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("FLARESOLVERR_URL must include a valid http(s) scheme and host")
    return raw


def _flaresolverr_timeout() -> int:
    raw = os.environ.get("FLARESOLVERR_TIMEOUT", "60")
    try:
        timeout = int(raw)
    except ValueError as exc:
        raise ValueError("FLARESOLVERR_TIMEOUT must be an integer number of seconds") from exc
    if timeout <= 0:
        raise ValueError("FLARESOLVERR_TIMEOUT must be greater than zero")
    return timeout


@dataclass(slots=True)
class AppConfig:
    app_name: str
    api_url: str
    proxy_content: bool
    socks5: str
    timezone: str
    guide_update: str
    flaresolverr_url: str
    flaresolverr_timeout: int


config = AppConfig(
    app_name="dlhd_proxy",
    api_url=_api_url(),
    proxy_content=_bool_env("PROXY_CONTENT", "TRUE"),
    socks5=os.environ.get("SOCKS5", ""),
    timezone=os.environ.get("TZ", "UTC"),
    guide_update=os.environ.get("GUIDE_UPDATE", "03:00"),
    flaresolverr_url=_flaresolverr_url(),
    flaresolverr_timeout=_flaresolverr_timeout(),
)

import os
import time
import requests
from dotenv import load_dotenv

# Module-level cache (per Python process)
_TOKEN_CACHE = {
    "access_token": None,
    "expires_at": 0,  # epoch seconds
}


def get_cdogs_token(env: str = "test", refresh_skew_seconds: int = 30) -> str:
    """
    Retrieve a CDOGS OAuth access token with automatic refresh.

    - Caches token in memory
    - Refreshes automatically when expired or near expiry

    :param env: "dev", "test", or "prod"
    :param refresh_skew_seconds: refresh token this many seconds before expiry
    :return: Bearer access token string
    """

    now = time.time()

    # ✅ Return cached token if still valid
    if (
        _TOKEN_CACHE["access_token"]
        and now < (_TOKEN_CACHE["expires_at"] - refresh_skew_seconds)
    ):
        return _TOKEN_CACHE["access_token"]

    # ⏳ Token missing or expired -> fetch new one
    load_dotenv()

    CONFIG = {
        "dev": {
            "client_id": os.getenv("cdogs_client_id_dev"),
            "client_secret": os.getenv("cdogs_client_secret_dev"),
            "token_url": os.getenv("cdogs_login_proxy_dev"),
            "api_url": os.getenv("cdogs_api_url_dev"),
        },
        "test": {
            "client_id": os.getenv("cdogs_client_id_test"),
            "client_secret": os.getenv("cdogs_client_secret_test"),
            "token_url": os.getenv("cdogs_login_proxy_test"),
            "api_url": os.getenv("cdogs_api_url_test"),
        },
        "prod": {
            "client_id": os.getenv("cdogs_client_id_prod"),
            "client_secret": os.getenv("cdogs_client_secret_prod"),
            "token_url": os.getenv("cdogs_login_proxy_prod"),
            "api_url": os.getenv("cdogs_api_url_prod"),
        },
    }

    if env not in CONFIG:
        raise ValueError("ENV must be one of: dev, test, prod")

    cfg = CONFIG[env]

    if not all(cfg.values()):
        raise RuntimeError(f"Missing CDOGS configuration values for env '{env}'")

    # Normalize shared env vars for callers
    os.environ["cdogs_api_url"] = cfg["api_url"]

    body = {
        "grant_type": "client_credentials",
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("Refreshing CDOGS token…")
    response = requests.post(
        cfg["token_url"],
        data=body,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    access_token = data.get("access_token")
    expires_in = data.get("expires_in")

    if not access_token or not expires_in:
        raise RuntimeError("Invalid token response from login proxy")

    # ✅ Cache token + expiry
    _TOKEN_CACHE["access_token"] = access_token
    _TOKEN_CACHE["expires_at"] = now + int(expires_in)

    return access_token

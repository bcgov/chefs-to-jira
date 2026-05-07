import os
import requests
from cdogs_auth import get_cdogs_token

ENV = "test"

# Get a valid bearer token (auto-refresh enabled)
token = get_cdogs_token(ENV)

api_url = os.getenv("cdogs_api_url")
if not api_url:
    raise RuntimeError("cdogs_api_url not set")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

# ============================================================
# Token-only validation: OpenAPI spec
# ============================================================

response = requests.get(
    f"{api_url}/api-spec.json",
    headers=headers,
    timeout=30,
)

response.raise_for_status()

spec = response.json()

print("✅ Token validation succeeded")
print("OpenAPI version:", spec.get("openapi"))
print("API title:", spec.get("info", {}).get("title"))
print("Available paths:", list(spec.get("paths", {}).keys()))

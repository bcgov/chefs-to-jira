import requests
import os
from dotenv import load_dotenv

load_dotenv()

# =============================
# Environment configuration
# Requirements: an .env file in the same folder that contains the 
# credentials for CONFIG (below)
# =============================

ENV = "dev"  # change to: "dev", "test", or "prod"

CONFIG = {
    "dev": {
        "client_id": os.getenv('cdogs_client_id_dev'),
        "client_secret": os.getenv('cdogs_client_secret_dev'),
        "uri": os.getenv('cdogs_login_proxy_dev'),
        "api_url": os.getenv('cdogs_api_url_dev')
    },
    "test": {
        "client_id": os.getenv('cdogs_client_id_test'),
        "client_secret": os.getenv('cdogs_client_secret_test'),
        "uri": os.getenv('cdogs_login_proxy_test'),
        "api_url": os.getenv('cdogs_api_url_test')
    },
    "prod": {
        "client_id": os.getenv('cdogs_client_id_prod'),
        "client_secret": os.getenv('cdogs_client_secret_prod'),
        "uri": os.getenv('cdogs_login_proxy_prod'),
        "api_url": os.getenv('cdogs_api_url_test')
    }
}

client_id = CONFIG[ENV]["client_id"]
client_secret = CONFIG[ENV]["client_secret"]
uri = CONFIG[ENV]["uri"]
api_url = CONFIG[ENV]["api_url"]

# =============================
# Request body (form-encoded)
# =============================

body = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# =============================
# POST request (Invoke-RestMethod equivalent)
# =============================

response = requests.post(
    uri,
    data=body,
    headers=headers
)

response.raise_for_status()

# =============================
# Access token
# =============================

access_token = response.json().get("access_token")
token = access_token

print(token)

# The following calls test that the token works.
# =============================
# Minimal sample request using an access token
# =============================
 
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

response = requests.get(
    api_url,
    headers=headers,
    timeout=30
)

response.raise_for_status()

print(response.status_code)
print(response.json())

# =============================
# Health Check
# =============================

response = requests.get(
    api_url + f'(health)',
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=30
)

print(response.status_code)
print(response.json())

# =============================
# List supported file types
# =============================

response = requests.get(
    api_url + f'fileTypes',
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=30
)

print(response.status_code)
print(response.json())

# =============================
# View the OpenAPI spec
# =============================

response = requests.get(
    api_url + f'api-spec.json',
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=30
)

print(response.status_code)
print(response.json().keys())
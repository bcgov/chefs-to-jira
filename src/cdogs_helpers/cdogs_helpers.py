from cdogs_helpers.constants import CDOGS_API_BASE_URL, CDOGS_CLIENT_ID, CDOGS_CLIENT_SECRET, CDOGS_LOGIN_PROXY, CDOGS_APP_ID
import json
import requests
import time

_TOKEN_CACHE = {
    "access_token": None,
    "expires_at": 0,  # epoch seconds
}

def get_cdogs_token(refresh_skew_seconds: int = 30) -> str:

    now = time.time()

    # ✅ Return cached token if still valid
    if (
        _TOKEN_CACHE["access_token"]
        and now < (_TOKEN_CACHE["expires_at"] - refresh_skew_seconds)
    ):
        return _TOKEN_CACHE["access_token"]

    body = {
        "grant_type": "client_credentials",
        "client_id": CDOGS_CLIENT_ID,
        "client_secret": CDOGS_CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("Refreshing CDOGS token…")
    response = requests.post(
        CDOGS_LOGIN_PROXY,
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


def generate_cdogs_document(answer_data, outfile_name: str, output_type: str, template_data: str, template_encoding: str, template_ext: str):
    options = {
        "convertTo": output_type,
        "overwrite": True,
        "reportName": outfile_name,
        }
    template = {
        "content": template_data,
        "encodingType": template_encoding,
        "fileType": template_ext
    }
    # Optionally support json as string
    if isinstance(answer_data, str):
        try:
            answer_data = json.loads(answer_data)
        except json.JSONDecodeError as e:
            pass
    body = {
        "data": answer_data,
        "options": options,
        "template": template
    }

    url = f"{CDOGS_API_BASE_URL}/template/render"

    try:
        response = requests.post(url, headers={"Authorization": f"Bearer {get_cdogs_token()}"}, json=body, timeout=30)
        response.raise_for_status()
        return response.content

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to CDOGS API {url}: {e}")
        raise

import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- CDOGS ----
CDOGS_CLIENT_ID_DEV = os.getenv('cdogs_client_id_dev', '')
CDOGS_CLIENT_SECRET_DEV = os.getenv('cdogs_client_secret_dev', '')
CDOGS_LOGIN_PROXY_DEV = os.getenv('cdogs_login_proxy_dev', '')
CDOGS_API_URL_DEV = os.getenv('cdogs_api_url_dev', '')

CDOGS_CLIENT_ID_TEST = os.getenv('cdogs_client_id_test', '')
CDOGS_CLIENT_SECRET_TEST = os.getenv('cdogs_client_secret_test', '')
CDOGS_LOGIN_PROXY_TEST = os.getenv('cdogs_login_proxy_test', '')
CDOGS_API_URL_TEST = os.getenv('cdogs_api_url_test', '')

CDOGS_CLIENT_ID_PROD = os.getenv('cdogs_client_id_prod', '')
CDOGS_CLIENT_SECRET_PROD = os.getenv('cdogs_client_secret_prod', '')
CDOGS_LOGIN_PROXY_PROD = os.getenv('cdogs_login_proxy_prod', '')
CDOGS_API_URL_PROD = os.getenv('cdogs_api_url_prod', '')

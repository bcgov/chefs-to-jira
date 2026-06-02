import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- CDOGS ----
CDOGS_CLIENT_ID_DEV = os.getenv('CDOGS_CLIENT_ID_DEV', '')
CDOGS_CLIENT_SECRET_DEV = os.getenv('CDOGS_CLIENT_SECRET_DEV', '')
CDOGS_LOGIN_PROXY_DEV = os.getenv('CDOGS_LOGIN_PROXY_DEV', '')
CDOGS_API_URL_DEV = os.getenv('CDOGS_API_URL_DEV', '')

CDOGS_CLIENT_ID_TEST = os.getenv('CDOGS_CLIENT_ID_TEST', '')
CDOGS_CLIENT_SECRET_TEST = os.getenv('CDOGS_CLIENT_SECRET_TEST', '')
CDOGS_LOGIN_PROXY_TEST = os.getenv('CDOGS_LOGIN_PROXY_TEST', '')
CDOGS_API_URL_TEST = os.getenv('CDOGS_API_URL_TEST', '')

CDOGS_CLIENT_ID_PROD = os.getenv('CDOGS_CLIENT_ID_PROD', '')
CDOGS_CLIENT_SECRET_PROD = os.getenv('CDOGS_CLIENT_SECRET_PROD', '')
CDOGS_LOGIN_PROXY_PROD = os.getenv('CDOGS_LOGIN_PROXY_PROD', '')
CDOGS_API_URL_PROD = os.getenv('CDOGS_API_URL_PROD', '')

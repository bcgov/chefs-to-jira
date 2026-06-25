import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- CDOGS ----
CDOGS_CLIENT_ID = os.getenv('CDOGS_CLIENT_ID', '')
CDOGS_CLIENT_SECRET = os.getenv('CDOGS_CLIENT_SECRET', '')
CDOGS_APP_ID = os.getenv('CDOGS_APP_ID', '')
CDOGS_LOGIN_PROXY = os.getenv('CDOGS_LOGIN_PROXY', '')
CDOGS_API_BASE_URL = os.getenv('CDOGS_API_BASE_URL', '')

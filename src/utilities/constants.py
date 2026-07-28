import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- File Helper ----
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')

# ---- Logging Helper ----
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

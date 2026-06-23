import os
from dotenv import load_dotenv, find_dotenv

# Load .env file only if not running in GitHub Actions (to avoid overriding secrets)
if not os.getenv('GITHUB_ACTIONS'):
    envPath = find_dotenv(usecwd=True)
    if envPath:
        load_dotenv(dotenv_path=envPath, override=False)

# ---- CHEFS ----
CHEFS_FORM_ID = os.getenv('CHEFS_FORM_ID')
CHEFS_API_KEY = os.getenv('CHEFS_API_KEY', '')
CHEFS_API_BASE_URL = os.getenv('CHEFS_API_BASE_URL')
CHEFS_FORM_ATTACHMENT_FIELD_NAME = os.getenv('CHEFS_FORM_ATTACHMENT_FIELD_NAME', 'fileUpload5MbMax')

# ---- CHEFS Test Constants ----
CHEFS_TEST_FORM_ID = os.getenv('CHEFS_TEST_FORM_ID')
CHEFS_TEST_SUBMISSION_ID = os.getenv('CHEFS_TEST_SUBMISSION_ID')
CHEFS_TEST_CONFIRMATION_ID = os.getenv('CHEFS_TEST_CONFIRMATION_ID')



import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- Email / SMTP ----
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
DEBUG_EMAIL = os.getenv('DEBUG_EMAIL', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', '')

# ---- JIRA ----
JIRA_API_URL = os.getenv('JIRA_API_URL', '')
JIRA_CLIENT_ID = os.getenv('JIRA_CLIENT_ID', '')
JIRA_CLIENT_EMAIL = os.getenv('JIRA_CLIENT_EMAIL', '')
JIRA_CLIENT_SECRET = os.getenv('JIRA_CLIENT_SECRET', '')
JIRA_CLIENT_TOKEN = os.getenv('JIRA_CLIENT_TOKEN', '')
JIRA_PROJECT = os.getenv('JIRA_PROJECT', '')
JIRA_COMPONENT = os.getenv('JIRA_COMPONENT', '')
JIRA_YOUNGER_THAN_MINUTES = int(os.getenv('JIRA_YOUNGER_THAN_MINUTES', '0'))


# ---- JIRA Test Constants ----
JIRA_TEST_FILE_PATH = os.getenv('JIRA_TEST_FILE_PATH', '')
JIRA_TEST_ISSUE_KEY = os.getenv('JIRA_TEST_ISSUE_KEY', '')
JIRA_PROJECT = os.getenv('JIRA_PROJECT', '')
JIRA_COMPONENT = os.getenv('JIRA_COMPONENT', '')

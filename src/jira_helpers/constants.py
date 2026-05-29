import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- JIRA ----
JIRA_API_URL = os.getenv('jira_api_url', '')
JIRA_CLIENT_ID = os.getenv('jira_client_id', '')
JIRA_CLIENT_EMAIL = os.getenv('jira_client_email', '')
JIRA_CLIENT_SECRET = os.getenv('jira_client_secret', '')
JIRA_CLIENT_TOKEN = os.getenv('jira_client_token', '')
JIRA_PROJECT = os.getenv('jira_project', '')
JIRA_COMPONENT = os.getenv('jira_component', '')
JIRA_YOUNGER_THAN_MINUTES = int(os.getenv('jira_younger_than_minutes', '0'))


# ---- JIRA Test Constants ----
JIRA_TEST_FILE_PATH = os.getenv('jira_test_file_path', '')
JIRA_TEST_ISSUE_KEY = os.getenv('jira_test_issue_key', '')
JIRA_PROJECT = os.getenv('jira_project', '')
JIRA_COMPONENT = os.getenv('jira_component', '')

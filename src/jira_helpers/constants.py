import os
import dotenv

envPath = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(envPath):
    print("loading dot env...")
    dotenv.load_dotenv()

JIRA_API_URL = os.environ['jira_api_url']

# JIRA Client setup
# Note: Secret and Token are not both required. Token authentication is in development, secret will be deprecated.
JIRA_CLIENT_ID = os.environ['jira_client_id']
JIRA_CLIENT_EMAIL = os.environ['jira_client_email']
JIRA_CLIENT_SECRET = os.environ['jira_client_secret']
JIRA_CLIENT_TOKEN = os.environ['jira_client_token']

# JIRA Project specific constants
JIRA_PROJECT = os.environ['jira_project']
JIRA_COMPONENT = os.environ['jira_component']

# JIRA Search constants
JIRA_YOUNGER_THAN_MINUTES = int(os.environ['jira_younger_than_minutes'])

# JIRA Test Script Items
JIRA_TEST_FILE_PATH = os.environ['jira_test_file_path']
JIRA_TEST_ISSUE_KEY = os.environ['jira_test_issue_key']

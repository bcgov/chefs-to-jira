import os
import dotenv

envPath = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(envPath):
    print("loading dot env...")
    dotenv.load_dotenv()

JIRA_API_URL = os.environ['jira_api_url']
JIRA_CLIENT_ID = os.environ['jira_client_id']
JIRA_CLIENT_EMAIL = os.environ['jira_client_email']
JIRA_CLIENT_SECRET = os.environ['jira_client_secret']
JIRA_CLIENT_TOKEN = os.environ['jira_client_token']

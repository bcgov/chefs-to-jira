from jira_helpers.constants import JIRA_PROJECT, JIRA_COMPONENT
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_searches import get_jira_tickets

# Get a JIRA client instance
jira_client = get_jira_client()
# Test the search function
try:
    get_jira_tickets(jira_client, JIRA_PROJECT, JIRA_COMPONENT)
    print("✅ JIRA search successful")
except Exception as e:
    print(f"Error searching for JIRA tickets: {e}")
    raise

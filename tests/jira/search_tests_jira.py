from jira_helpers.constants import JIRA_PROJECT, JIRA_COMPONENT
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_searches import get_jira_tickets
from jira_helpers.jira_searches import get_jira_ticket

# Get a JIRA client instance
jira_client = get_jira_client()

# Test the search function
try:
    issues = get_jira_tickets(jira_client, JIRA_PROJECT, JIRA_COMPONENT)

    if not issues:
        print("❌ No issues found matching the criteria.")
    else:
      for issue in issues:
          print(f"{issue.key}: {issue.fields.summary}")
    print("✅ JIRA search successful")
except Exception as e:
    print(f"❌ Error searching for JIRA tickets: {e}")
    raise

# Test field retrieval from an issue
try:
    issue = get_jira_ticket(jira_client, "PINT-3013")
    print(f"✅ JIRA ticket retrieval successful: {issue.key} - {issue.fields.summary}")

except Exception as e:
    print(f"❌ Error fetching JIRA ticket: {e}")
    raise

from jira_helpers.constants import JIRA_PROJECT, JIRA_COMPONENT
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_searches import get_jira_tickets, get_jira_tickets_query, get_jira_ticket

# Get a JIRA client instance
jira_client = get_jira_client()

# Test the search function
try:
    default_query = get_jira_tickets_query(JIRA_PROJECT, component=JIRA_COMPONENT)
    issues = get_jira_tickets(jira_client, default_query)
    if not issues:
        print("No issues found matching the default criteria, expanding search.")
        expanded_query = get_jira_tickets_query(JIRA_PROJECT, reporter=None, component=None)
        issues = get_jira_tickets(jira_client, expanded_query)

    if not issues:
        print("❌ JIRA No issues found with get_jira_tickets regardless of component.")
        print(f"Generated JQL queries for debugging: {default_query}")
        print(f"Generated JQL queries for debugging: {expanded_query}")
    else:
      print("✅ JIRA API get_jira_tickets returned results without error:")
      for issue in issues:
          print(f"{issue.key}: {issue.fields.summary}")

except Exception as e:
    print(f"❌ Error searching for JIRA tickets: {e}")
    raise

# Test field retrieval from an issue
try:
    issue = get_jira_ticket(jira_client, "PINT-3013")
    print(f"✅ JIRA get_jira_ticket retrieval successful: {issue.key} - {issue.fields.summary}")

except Exception as e:
    print(f"❌ Error fetching JIRA ticket: {e}")
    raise

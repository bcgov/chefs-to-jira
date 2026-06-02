from jira_helpers.constants import JIRA_PROJECT, JIRA_COMPONENT, JIRA_TEST_ISSUE_KEY
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_searches import get_jira_tickets, get_jira_tickets_query, get_jira_ticket

def test_jira_searches():
  """Test that we can search for JIRA tickets and retrieve them successfully"""
  # Get a JIRA client instance
  jira_client = get_jira_client()
  assert jira_client is not None, "Should get a valid JIRA client"

  # Test the search function
  try:
      default_query = get_jira_tickets_query(JIRA_PROJECT, reporter="donotreplyCHEFS@gov.bc.ca", component=JIRA_COMPONENT)
      issues = get_jira_tickets(jira_client, default_query)
      if not issues:
          print("No issues found matching the default criteria, expanding search.")
          expanded_query = get_jira_tickets_query(JIRA_PROJECT, reporter=None, component=None, younger_than_minutes=50400)
          issues = get_jira_tickets(jira_client, expanded_query)

      if not issues:
          print(f"Generated JQL queries for debugging: {default_query}")
          print(f"Generated JQL queries for debugging: {expanded_query}")
      assert issues is not None, "Should be able to find some JIRA issues"
      if issues:
          print(f"✅ JIRA search successful - Found {len(issues)} issues matching criteria.")

  except Exception as e:
      print(f"❌ Error searching for JIRA tickets: {e}")
      raise

  # Test field retrieval from an issue
  try:
      issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
      assert issue is not None, "Should get a valid JIRA issue"

      print(f"✅ JIRA ticket retrieval successful - Retrieved issue {issue.key}")

      # Did some advance scouting for functionality we might want to use in the future.
      # Leaving these prints in for now.
      # We can remove them later if they aren't useful.
      print_debugs=False
      if print_debugs:
        print(f"Issue summary: {issue.fields.summary}")
        print(f"Issue reporter: {issue.fields.reporter.displayName}")
        print(f"Issue components: {[component.name for component in issue.fields.components]}")
        print(f"Issue assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}  ")
        print(f"Issue Labels: {issue.fields.labels}")
        print(f"Issue Ticket History:")
        for history in issue.changelog.histories:
            if history.items and len(history.items) > 0:
                print(f"{history.created} - {history.author.displayName}: {history.items[0].field} changed to {history.items[0].toString}")
  except Exception as e:
      print(f"❌ Error fetching JIRA ticket: {e}")
      raise

test_jira_searches()

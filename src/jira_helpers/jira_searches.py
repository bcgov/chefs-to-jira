import datetime
from jira.client import ResultList
from jira.resources import Issue


def jql_literal(s: str) -> str:
    """Return a JQL-safe quoted literal, preserving interior and trailing spaces."""
    """This is mostly important for the Component field, which has a trailing space in the value."""
    return f'"{s}"'

def get_jira_tickets_query(project, reporter="donotreplyCHEFS@gov.bc.ca", component=None, younger_than_minutes=10080):
    # Calculate the cutoff date for issues created within the last younger_than_minutes
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=younger_than_minutes)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M")

    # Search for issues created by CHEFS with the correct project and component
    JQL_query = (
        f'request-channel-type = email AND '
        f'project = {jql_literal(project)} AND '
        f'created >= {jql_literal(cutoff_str)}'
    )

    if reporter:
        JQL_query += f' AND reporter = {jql_literal(reporter)}'

    if component:
        JQL_query += f' AND component = {jql_literal(component)}'

    return JQL_query

def get_jira_tickets(client, JQL_query):

    try:
        issues: ResultList[Issue] = client.search_issues(JQL_query, maxResults=5)
    except Exception as e:
        print(f"Error searching for JIRA tickets: {e}")
        raise

    return issues

def get_jira_ticket(client, issue_key):

    try:
        issue = client.issue(issue_key)
        return issue
    except Exception as e:
        print(f"Error fetching JIRA ticket {issue_key}: {e}")
        raise


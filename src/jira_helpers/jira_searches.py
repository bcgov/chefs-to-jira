import datetime
from jira.client import ResultList
from jira.resources import Issue

def get_jira_tickets(client, project, component, younger_than_minutes = 10080):

    # Calculate the cutoff date for issues created within the last younger_than_minutes
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=younger_than_minutes)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M")

    # Search for issues created by CHEFS with the correct project and component
    JQL_query = (
        f'request-channel-type = email AND '
        f'reporter = "donotreplyCHEFS@gov.bc.ca" AND '
        f'project = "{project}" AND '
        f'component = "{component}" AND '
        f'created >= "{cutoff_str}"'
    )

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


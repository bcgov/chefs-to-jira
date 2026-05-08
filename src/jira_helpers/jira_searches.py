import jira
import datetime

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
    issues = client.search_issues(JQL_query)

    for issue in issues:
        print(f"{issue.key}: {issue.fields.summary}")

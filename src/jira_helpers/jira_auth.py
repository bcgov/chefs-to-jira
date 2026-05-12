import jira
from jira_helpers.constants import JIRA_API_URL, JIRA_CLIENT_ID, JIRA_CLIENT_EMAIL, JIRA_CLIENT_SECRET, JIRA_CLIENT_TOKEN

def get_jira_client():
    # Create a JIRA client instance.
    # For Jira Server/Data Center (on-prem), use basic_auth=(username, password) or
    # basic_auth=(username, api_token) if your instance has PATs enabled.
    # The `token_auth` function sends a bearer token header and is not usually supported by
    # on-prem JIRA out of the box.
    try:
        if JIRA_CLIENT_TOKEN:
            # This does not work currently. Is JIRA set to allow PAT authentication?
            auth_kwargs = {"basic_auth": (JIRA_CLIENT_ID, JIRA_CLIENT_TOKEN)}
            auth_source = "username + API token"
        elif JIRA_CLIENT_SECRET:
            # This does work, but will soon be deprecated in favor of OAuth or PATs.
            auth_kwargs = {"basic_auth": (JIRA_CLIENT_EMAIL, JIRA_CLIENT_SECRET)}
            auth_source = "username + password"
        else:
            raise ValueError(
                "Missing Jira auth credential. Set jira_client_token or jira_client_secret."
            )

        client = jira.JIRA(server=JIRA_API_URL, **auth_kwargs)
        print(f"Successfully connected to JIRA API using {auth_source}")
        return client
    except Exception as e:
        print(f"Error connecting to JIRA API: {e}")
        raise

from jira_helpers.jira_auth import get_jira_client

# Get a JIRA client instance
jira_client = get_jira_client()

# Test the connection by fetching some data (e.g., project list)
try:
    projects = jira_client.projects()
    print("✅ JIRA connection successful")
    print("Available projects:", [project.key for project in projects])
except Exception as e:
    print(f"Error fetching projects from JIRA: {e}")
    raise

from jira_helpers.jira_auth import get_jira_client

def test_jira_connection():
    """Test that we get a valid JIRA client instance"""
    jira_client = get_jira_client()
    assert jira_client is not None, "Should get a valid JIRA client"

    # Test the connection by fetching some data (e.g., project list)
    projects = jira_client.projects()

    # Assert that we got projects back
    assert len(projects) > 0, "Should have at least one project"

    # Assert that projects have keys
    project_keys = [project.key for project in projects]
    assert len(project_keys) > 0, "Projects should have keys"

    # Print for visibility (optional)
    print(f"✅ JIRA connection successful - Connected and found {len(project_keys)} project keys.")


from jira_helpers.constants import JIRA_TEST_FILE_PATH, JIRA_TEST_ISSUE_KEY
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_searches import get_jira_ticket
from jira_helpers.jira_attachments import attachment_on_issue, add_attachment_to_issue, remove_attachment_from_issue

# Get a JIRA client instance
jira_client = get_jira_client()

# Setup for testing
try:
    # Get the test issue.
    issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
    if not issue:
        print("Can't run test. No test issue found.")
        raise ValueError("No test issue found.")
except Exception as e:
    print(f"Error setting up tests: {e}")
    raise

# Test the attachment functions
try:
    # 1. Check that the test attachment is not already on the issue.
    # 2. Add a test attachment.
    # 3. Check the test attachment is now on the issue.
    # 4. Remove the test attachment.
    # 5. Check that the test issue was succesfully cleaned up.

    # 1. Check that the test attachment is not already on the issue.
    attachment_found = attachment_on_issue(issue, "test_attachment.txt")
    if attachment_found:
        raise ValueError("❌ Attachment found on issue")
    else:
        print("✅ Attachment does not pre-exist on issue")

    # 2. Add a test attachment
    attachment_added = add_attachment_to_issue(jira_client, issue, JIRA_TEST_FILE_PATH)
    if attachment_added:
        print("✅ Attachment added to issue")
    else:
        raise ValueError("Failed to add attachment to issue")

    # 3. Check the test attachment is now on the issue.
    issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
    attachment_found = attachment_on_issue(issue, JIRA_TEST_FILE_PATH.split("/")[-1])
    if attachment_found:
        print("✅ Attachment found on issue")
    else:
        raise ValueError("❌ Attachment not found on issue")

    # 4. Remove the test attachment
    # Note: JIRA's API does not currently support removing attachments by filename, so this test will fail until that functionality is added. See https://ecosystem.atlassian.net/browse/JRA-123456 for details.
    attachment_removed = remove_attachment_from_issue(issue, JIRA_TEST_FILE_PATH.split("/")[-1])
    if attachment_removed:
        print("✅ Attachment removed from issue")
    else:
        raise ValueError("❌ Failed to remove attachment from issue")


    # 5. Check that the test issue was succesfully cleaned up.
    issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
    attachment_found = attachment_on_issue(issue, "test_attachment.txt")
    if attachment_found:
        raise ValueError("❌ Attachment was not cleaned up from issue")
    else:
        print("✅ Attachment was succesfully cleaned up")

    print("✅ JIRA attachment tests successful")
except Exception as e:
    print(f"Error testing attachments for JIRA tickets: {e}")
    raise

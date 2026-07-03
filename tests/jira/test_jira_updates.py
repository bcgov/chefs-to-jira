from jira_helpers.constants import JIRA_TEST_ISSUE_KEY
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_searches import get_jira_ticket
from jira_helpers.jira_updates import add_comment_to_issue, attachment_on_issue, add_attachment_to_issue, remove_attachment_from_issue
import os

from utilities.log_helper import LOGGER

def test_jira_attachments():

  # Get a JIRA client instance
  jira_client = get_jira_client()
  assert jira_client is not None, "Should get a valid JIRA client"

  # Setup for testing
  JIRA_TEST_FILE_PATH = os.getcwd() + "/tests/test_files/Quick Test File.txt"
  JIRA_TEST_FILE_NAME = JIRA_TEST_FILE_PATH.split("/")[-1]
  try:
      # Get the test issue.
      issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
      assert issue is not None, "Should get a valid JIRA issue"
  except Exception as e:
      LOGGER.error(f"Error setting up tests: {e}")
      raise

  # Test the attachment functions
  try:
      # 1. Check that the test attachment is not already on the issue.
      # 2. Add a test attachment.
      # 3. Check the test attachment is now on the issue.
      # 4. Remove the test attachment.
      # 5. Check that the test issue was succesfully cleaned up.

      # 1. Check that the test attachment is not already on the issue.
      attachment_found = attachment_on_issue(issue, JIRA_TEST_FILE_NAME)
      assert attachment_found is False, "Should not be an attachment on the test ticket before testing"

      # 2. Add a test attachment
      attachment_added = add_attachment_to_issue(jira_client, issue, JIRA_TEST_FILE_PATH)
      assert attachment_added is True, "Should have positive return of attachment add"

      # 3. Check the test attachment is now on the issue.
      issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
      attachment_found = attachment_on_issue(issue, JIRA_TEST_FILE_NAME)
      assert attachment_found is True, "Should find the attachment on the issue after adding it"

      # 4. Remove the test attachment
      # Note: JIRA's API does not currently support removing attachments by filename, so this test will fail until that functionality is added. See https://ecosystem.atlassian.net/browse/JRA-123456 for details.
      attachment_removed = remove_attachment_from_issue(issue, JIRA_TEST_FILE_NAME)
      assert attachment_removed is True, "Should have positive return of attachment removal"

      # 5. Check that the test issue was succesfully cleaned up.
      issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
      attachment_found = attachment_on_issue(issue, JIRA_TEST_FILE_NAME)
      assert attachment_found is False, "Should not be an attachment on the test ticket after testing"

      LOGGER.info("✅ JIRA attachment tests successful")
  except Exception as e:
      LOGGER.error(f"Error testing attachments for JIRA tickets: {e}")
      raise

def test_jira_comments():
    # Get a JIRA client instance
    jira_client = get_jira_client()
    assert jira_client is not None, "Should get a valid JIRA client"

    # Get the test issue.
    issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
    assert issue is not None, "Should get a valid JIRA issue"

    # Test adding a comment to the issue
    test_comment = "This is a test comment for the JIRA ticket."
    comment_added = add_comment_to_issue(jira_client, issue, test_comment)
    assert comment_added is True, "Should have positive return of comment add"

    # Verify that the comment was added
    issue = get_jira_ticket(jira_client, JIRA_TEST_ISSUE_KEY)
    comments = [comment.body for comment in issue.fields.comment.comments]
    assert test_comment in comments, "The test comment should be present in the issue's comments"

    LOGGER.info("✅ JIRA add comment test successful")

test_jira_attachments()
test_jira_comments()

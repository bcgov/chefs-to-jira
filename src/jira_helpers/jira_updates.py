from io import BytesIO

import requests
from jira.exceptions import JIRAError
from jira.resources import Issue

from jira_helpers.jira_searches import get_jira_comments
from utilities.log_helper import LOGGER


# Compares a file to the attachments on a JIRA issue. Returns true if a match is found, false if not.
def attachment_on_issue(issue: Issue, file_name: str) -> bool:
    try:
        attachments = issue.fields.attachment
        for attachment in attachments:
            if attachment.filename == file_name:
                LOGGER.debug(f"Attachment {file_name} found on issue {issue.key}")
                return True
    except (JIRAError, requests.exceptions.RequestException, AttributeError, TypeError) as e:
        LOGGER.error(f"Error occurred while checking attachment: {e}")
    LOGGER.debug(f"Attachment {file_name} not found on issue {issue.key}")
    return False

# Upload an attachment to a JIRA issue. Returns true if the attachment was successfully added, false if not.
def add_attachment_to_issue(client, issue: Issue, file: str|object) -> bool:
    if isinstance(file, str):
      client.add_attachment(issue=issue, attachment=file)
    elif isinstance(file, object):
      memory_file = BytesIO(file.get("data"))
      client.add_attachment(issue=issue, attachment=memory_file, filename=file.get("filename"))
    return True

# Remove an attachment from a JIRA issue by file name. Returns true if the attachment was successfully removed, false if not.
def remove_attachment_from_issue(issue: Issue, file_name: str) -> bool:
    try:
        attachments = issue.fields.attachment
        for attachment in attachments:
            if attachment.filename == file_name:
                attachment.delete()
                LOGGER.debug(f"Attachment {file_name} removed from issue {issue.key}")
                return True
        LOGGER.debug(f"Attachment {file_name} not found on issue {issue.key}")
    except (JIRAError, requests.exceptions.RequestException, AttributeError, TypeError) as e:
        LOGGER.error(f"Error occurred while removing attachment: {e}")
    return False

def add_comment_to_issue(client, issue: Issue, comment: str) -> bool:
    result = client.add_comment(issue=issue, body=comment, is_internal=True)
    return result is not None

# Add a comment to a JIRA issue if that issue does not already contain the comment.
def add_comment_to_issue_if_missing(jira_client, issue, error_text):
  if error_text not in get_jira_comments(issue):
    add_comment_to_issue(jira_client, issue, error_text)

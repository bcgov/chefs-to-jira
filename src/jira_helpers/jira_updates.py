from jira.resources import Issue
from io import BytesIO
from utilities.log_helper import LOGGER
from jira_helpers.jira_searches import get_jira_comments

# Compares a file to the attachments on a JIRA issue. Returns true if a match is found, false if not.
def attachment_on_issue(issue: Issue, file_name: str) -> bool:
    try:
        attachments = issue.fields.attachment
        for attachment in attachments:
            if attachment.filename == file_name:
                # print(f"Attachment {file_name} found on issue {issue.key}")
                return True
        # print(f"Attachment {file_name} not found on issue {issue.key}")
    except Exception as e:
        LOGGER.error(f"Error occurred while checking attachment: {e}")
    return False

# Upload an attachment to a JIRA issue. Returns true if the attachment was successfully added, false if not.
def add_attachment_to_issue(client, issue: Issue, file: str|object) -> bool:
    try:
        if isinstance(file, str):
          client.add_attachment(issue=issue, attachment=file)
          return True
        elif isinstance(file, object):
          memory_file = BytesIO(file.get("data"))
          client.add_attachment(issue=issue, attachment=memory_file, filename=file.get("filename"))
          return True
    except Exception as e:
        LOGGER.error(f"Error occurred while adding attachment: {e}")
    return False

# Remove an attachment from a JIRA issue by file name. Returns true if the attachment was successfully removed, false if not.
def remove_attachment_from_issue(issue: Issue, file_name: str) -> bool:
    try:
        attachments = issue.fields.attachment
        for attachment in attachments:
            if attachment.filename == file_name:
                attachment.delete()
                # print(f"Attachment {file_name} removed from issue {issue.key}")
                return True
        # print(f"Attachment {file_name} not found on issue {issue.key}")
    except Exception as e:
        LOGGER.error(f"Error occurred while removing attachment: {e}")
    return False

def add_comment_to_issue(client, issue: Issue, comment: str) -> bool:
    try:
        result = client.add_comment(issue=issue, body=comment, is_internal=True)
        return result is not None
    except Exception as e:
        LOGGER.error(f"Error occurred while adding comment: {e}")
    return False

# Add a comment to a JIRA issue if that issue does not already contain the comment.
def add_comment_to_issue_if_missing(jira_client, issue, error_text):
  if error_text not in get_jira_comments(issue):
    add_comment_to_issue(jira_client, issue, error_text)

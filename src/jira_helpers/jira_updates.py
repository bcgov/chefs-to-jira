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

# Get the actual jira field name from a custom field name
def get_fields_by_display_name(jira_client, issue: Issue|str) -> dict:
  # Get fields specific to this issue. The reason is that JIRA can have duplicate display names for different custom fields.
  # We want to ensure we are using the correct field name for this specific issue.

  # Make sure the issue has field names loaded.
  if isinstance(issue, str) or issue.raw is None or "fields" not in issue.raw:
    issue = jira_client.issue(issue, expand='names')

  if issue.raw is None or "fields" not in issue.raw:
    LOGGER.error(f"Unable to retrieve field names for issue {issue.key}. Please check the issue key and try again.")
    return {}

  if not hasattr(jira_client, "_cached_field_mappings"):
    # Call the API and build the lookup dictionary
    all_fields = jira_client.fields()

    # Stash it securely as a private attribute on the client object to save time on future calls.
    # This is a bit of a hack but it'll work.
    jira_client._cached_field_mappings = {f["id"]: f["name"] for f in all_fields}

  issue_fields_by_display_name = {}

  # Do two passes to reduce chefs case sensitivity requirement.
  # First pass add them all lowercase. Second pass uses actual case, and overwrites any previous lowercase that would be duplicate.
  for issue_field_id in issue.raw["fields"]:
    if issue_field_id in jira_client._cached_field_mappings:
      issue_fields_by_display_name[jira_client._cached_field_mappings[issue_field_id].lower()] = issue_field_id
  for issue_field_id in issue.raw["fields"]:
    if issue_field_id in jira_client._cached_field_mappings:
      issue_fields_by_display_name[jira_client._cached_field_mappings[issue_field_id]] = issue_field_id

  return issue_fields_by_display_name

# Convert string values for fields into more complex values as needed.
def update_with_complex_fields(jira_client, issue, field_names_with_values):
  # Fetch the edit metadata for the issue
  edit_metadata = jira_client.editmeta(issue)
  fields_schema = edit_metadata.get("fields", {})

  for field_name, new_str_value in field_names_with_values.items():

    field_meta = fields_schema.get(field_name)
    if field_meta is None:
      LOGGER.warning(f"Field '{field_name}' not found in edit metadata for issue {issue.key}. Skipping this field.")
      continue
    field_type = field_meta["schema"]["type"]

    if field_type == "string":
      # No conversion needed for string fields
      continue

    elif field_type == "option":
      # Convert string to option object
      options = field_meta.get("allowedValues", [])
      matching_option = next((opt for opt in options if opt["value"] == new_str_value), None)
      if matching_option:
        field_names_with_values[field_name] = matching_option
      else:
        LOGGER.warning(f"Value '{new_str_value}' not found in allowed values for field '{field_name}'. Skipping this field.")
        del field_names_with_values[field_name]

    elif field_type == "array" and field_meta.get("schema", {}).get("items") == "option":
      # This option is untested and likely only works for only the parent option, as
      # the chefs code doesn't currently pass any kind of comma-seperation delimiter yet.
      # If it's a comma-separated list of choices from your form
      if "," in new_str_value:
        return [{"value": val.strip()} for val in new_str_value.split(",")]
      return [{"value": new_str_value.strip()}]

    elif field_type == "cascading-select":
      # This option is untested and likely only works for only the parent option, as
      # the chefs code doesn't currently pass any kind of > delimiter yet.

      # Check if the incoming string contains a delimiter (e.g., "Parent > Child")
      if " > " in new_str_value:
          parent_part, child_part = new_str_value.split(" > ", 1)
          return {
              "value": parent_part.strip(),
              "child": {"value": child_part.strip()}
          }
      else:
          # Only setting the parent level option
          return {"value": new_str_value.strip()}

    else:
        LOGGER.warning(f"Jira Form Field Schema Option Not Implemented: '{field_type}'. Skipping this field.")
        del field_names_with_values[field_name]

  # Actually send the update.
  issue.update(fields=field_names_with_values)

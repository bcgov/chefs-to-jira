
from cdogs_helpers.cdogs_helpers import generate_cdogs_document
from cdogs_helpers.constants import CDOGS_OUTPUT_TYPE

from chefs_helpers.chefs_helpers import get_chefs_form, get_form_submissions, get_submission_attachments, get_form_cdogs_template

from jira_helpers.constants import JIRA_PROJECT, JIRA_COMPONENT, JIRA_YOUNGER_THAN_MINUTES
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_updates import attachment_on_issue, add_attachment_to_issue, add_comment_to_issue
from jira_helpers.jira_searches import get_jira_comments, get_jira_tickets, get_jira_tickets_query

from utilities.send_admin_email import send_admin_email
from utilities.log_helper import LOGGER, get_logs

from base64 import b64encode
from json import dumps
from pathlib import Path
import re

LOGGER.debug("LOGGER - Chefs-to-JIRA script Started!")

# 1. Check JIRA for new submissions
# For each submission:
#   2. Get submission attachments from CHEFS
#   3. Update JIRA ticket with submission attachments
#   4. Get the version of the form that created the submission
#   5. Get the forms' cdogs template from CHEFS
#   6. Get submission answers from CHEFS
#   7. Use answers and template from CHEFS to generate CDOGS PDF
#   8. Update JIRA ticket with CDOGS PDF attachment
#   9. Parse the form questions for JIRA field and answer mapping
#   10. Update JIRA ticket with CHEFS answers
#   11. Update ticket with a mark that the ticket was pre-populated by Chefs-To-Jira
#   12. Optionally notify OPTIMIZE of PIA creation.

# === 1. Check JIRA for new submissions ===
# Get a JIRA client instance
try:
  jira_client = get_jira_client()
except Exception as e:
  LOGGER.error(f"❌ Error occurred getting JIRA client: {e}")
  raise

# Get the new issues
try:
  jql = get_jira_tickets_query(JIRA_PROJECT, reporter="donotreplyCHEFS@gov.bc.ca", component=JIRA_COMPONENT, younger_than_minutes=JIRA_YOUNGER_THAN_MINUTES)

  # DEV-OVERRIDE (gives quick access to a wide variety of JIRA tickets):
  # jql = get_jira_tickets_query(JIRA_PROJECT, reporter="PPLATTEN", younger_than_minutes=180080)
  issues = get_jira_tickets(jira_client, jql)
except Exception as e:
  LOGGER.error(f"❌ Error searching for JIRA tickets: {e}")
  raise

completion_text = "Ticket pre-populated by Chefs-To-Jira"
for issue in issues:
  LOGGER.info(f"Processing issue: {issue.key}")

  if completion_text in get_jira_comments(issue):
    LOGGER.info(f"Skipping issue as complete: {issue.key}")
    continue

# === 2. Get submission attachments from CHEFS ===
  # The CHEFS Body that JIRA Automation uses to populate the JIRA Ticket includes a link to view the submission:
  submission_pattern = "view\?s=([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})]"
  result = re.findall(submission_pattern, issue.fields.description)
  submission_id = ""
  match len(result):
    case 0:
      LOGGER.warning(f"No submission ID found in issue {issue.key}. Skipping.")
      continue
    case 1:
      submission_id = result[0]
    case _:
      LOGGER.warning(f"Found multiple submission IDs in issue {issue.key}: {result}")
      continue

  LOGGER.info(f"submission id = {submission_id}")
  attachments = get_submission_attachments(submission_id)

  if attachments is not None and len(attachments) > 0:

    # === 3. Update JIRA ticket with submission attachments ===
    for attachment in attachments:
      filename = attachment.get("filename")
      if not attachment_on_issue(issue, filename):
        try:
          add_attachment_to_issue(jira_client, issue, attachment)
        except Exception as e:
          LOGGER.error(f"❌ Error adding attachment to JIRA tickets: {e}")

# === 4. Get the version of the form that created the submission ===
  submission = get_form_submissions(submission_id=submission_id)
  form_version_id = submission.get("formVersionId")
  form = get_chefs_form(form_version_id=form_version_id)

# === 5. Get the forms' cdogs template from CHEFS ===
  cdogs_template = get_form_cdogs_template(form_version_id=form_version_id)

# === 6. Get submission answers from CHEFS ===
  answers = submission.get("submission").get("data")

# === 7. Use answers and template from CHEFS to generate CDOGS PDF ===
  if cdogs_template is not None:
    try:
      template_outfile_name = cdogs_template.get("filename")
      output_type=CDOGS_OUTPUT_TYPE
      output_name_no_extension=Path(template_outfile_name).stem
      outfile_name=f"{output_name_no_extension}.{output_type}"

      if not attachment_on_issue(issue, outfile_name):

        # byte array to base64 encoded str
        template_byte_array = bytes(cdogs_template.get("template").get("data"))
        template_base_64_str = ''.join(chr(c) for c in template_byte_array)

        content = generate_cdogs_document(
            answer_data=answers,
            outfile_name=output_name_no_extension,
            output_type=output_type,
            template_data=template_base_64_str,
            template_encoding="base64",
            template_ext=Path(template_outfile_name).suffix[1:]
        )

# === 8. Update JIRA ticket with CDOGS PDF attachment ===
        attachment=attachment
        content=content

        file = {
          "data": content,
          "filename": f"{outfile_name}"
        }
        try:
          add_attachment_to_issue(jira_client, issue, file)
        except Exception as e:
          LOGGER.error(f"❌ Error adding cdogs template to JIRA tickets: {e}")
    except Exception as e:
      LOGGER.error(f"❌ Error occurred generating cdogs output file: {e}")

# === 9. Parse the form questions for answers and jira field mapping ===
  field_names_with_values={}
  form_components=form.get("schema").get("components")
  for component in form_components:
    if "properties" in component:
      raw_properties = component.get("properties")
      properties = {k.lower():v for k,v in raw_properties.items()}
      if "jiramapping" in properties:
        jira_field_name = properties.get("jiramapping").lower()
        chefs_field_name = component.get("key")
        new_jira_value = answers.get(chefs_field_name)
        field_names_with_values[jira_field_name] = new_jira_value

# === 10. Update JIRA ticket with CHEFS answers ===
        issue.update(fields=field_names_with_values)
        issue = issue

# === 11. Update ticket with a mark that the ticket was pre-populated by Chefs-To-Jira ===
  add_comment_to_issue(jira_client, issue, completion_text)
  LOGGER.debug(f"Chefs-to-JIRA script completed issue {issue.key}!")

# === 12. Optionally notify OPTIMIZE of PIA creation. ===
log_string = "<br />".join(get_logs())
send_admin_email(f"Log output:<br />{log_string}")
LOGGER.debug("LOGGER - Chefs-to-JIRA script finished!")

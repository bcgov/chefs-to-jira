
from cdogs_helpers.cdogs_helpers import generate_cdogs_document

from chefs_helpers.chefs_helpers import get_chefs_form, get_form_submissions, get_submission_attachments, get_form_cdogs_template

from jira_helpers.constants import JIRA_PROJECT, JIRA_COMPONENT
from jira_helpers.jira_auth import get_jira_client
from jira_helpers.jira_attachments import attachment_on_issue, add_attachment_to_issue
from jira_helpers.jira_searches import get_jira_tickets, get_jira_tickets_query, get_jira_ticket

from utilities.send_admin_email import send_admin_email
from utilities.log_helper import LOGGER

from base64 import b64encode
from json import dumps
from pathlib import Path
import re

send_admin_email("Chefs-to-JIRA script Started!")
LOGGER.info("LOGGER - Chefs-to-JIRA script Started!")

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
#   11. Optionally notify OPTIMIZE of PIA creation.

# === 1. Check JIRA for new submissions ===
# Get a JIRA client instance
jira_client = get_jira_client()

# Get the new issues
try:
  # jql = get_jira_tickets_query(JIRA_PROJECT, reporter="PPLATTEN", younger_than_minutes=180080)
  # DEV-OVERRIDE:
  jql = get_jira_tickets_query(JIRA_PROJECT, reporter="donotreplyCHEFS@gov.bc.ca", component=JIRA_COMPONENT, younger_than_minutes=80080)
  issues = get_jira_tickets(jira_client, jql)
except Exception as e:
  print(f"❌ Error searching for JIRA tickets: {e}")
  raise

for issue in issues:
  print(issue.key)
  # Skip any already complete
  if "Ticket pre-populated by Chefs-To-Jira" in issue.fields.description:
      pass

# 2. Get submission attachments from CHEFS
  submission_pattern = "view\?s=([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})]"
  result = re.findall(submission_pattern, issue.fields.description)
  submission_id = ""
  match len(result):
    case 0:
      # TODO: Handle that the ticket doesn't have a submission ID.
      pass
    case 1:
      submission_id = result[0]
    case _:
      # TODO: Maybe there are multiple? If same just use it but different then pass.
      pass

  print(f"submission id = {submission_id}")
  attachments = get_submission_attachments(submission_id)

  if attachments is not None and len(attachments) > 0:

    # 3. Update JIRA ticket with submission attachments
    for attachment in attachments:
      filename = attachment.get("filename")
      if not attachment_on_issue(issue, filename):
        try:
          add_attachment_to_issue(jira_client, issue, attachment)
        except Exception as e:
          print(f"❌ Error adding attachment to JIRA tickets: {e}")

# 4. Get the version of the form that created the submission
  submission = get_form_submissions(submission_id=submission_id)
  form_version_id = submission.get("formVersionId")
  form = get_chefs_form(form_version_id=form_version_id)

# 5. Get the forms' cdogs template from CHEFS
  cdogs_template = get_form_cdogs_template(form_version_id=form_version_id)

# 6. Get submission answers from CHEFS
  answers = submission.get("submission").get("data")

# 7. Use answers and template from CHEFS to generate CDOGS PDF
  if cdogs_template is not None:
    try:
      template_outfile_name = cdogs_template.get("filename")

      if not attachment_on_issue(issue, template_outfile_name):

        # byte array to base64 encoded str
        template_byte_array = bytes(cdogs_template.get("template").get("data"))
        template_base_64_str = ''.join(chr(c) for c in template_byte_array)
        output_type="pdf"
        output_name_no_extension=Path(template_outfile_name).stem

        content = generate_cdogs_document(
            answer_data=answers,
            outfile_name=output_name_no_extension,
            output_type=output_type,
            template_data=template_base_64_str,
            template_encoding="base64",
            template_ext=Path(template_outfile_name).suffix[1:]
        )

# 8. Update JIRA ticket with CDOGS PDF attachment
        attachment=attachment
        content=content

        file = {
          "data": content,
          "filename": f"{output_name_no_extension}.{output_type}"
        }
        try:
          add_attachment_to_issue(jira_client, issue, file)
        except Exception as e:
          print(f"❌ Error adding cdogs template to JIRA tickets: {e}")
    except Exception as e:
      print(f"❌ Error occurred generating cdogs output pdf: {e}")

# 9. Parse the form questions for answers and jira field mapping
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

# 10. Update JIRA ticket with CHEFS answers
        issue.update(fields=field_names_with_values)
        issue = issue

#   11. Optionally notify OPTIMIZE of PIA creation.

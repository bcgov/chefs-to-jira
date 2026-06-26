from chefs_helpers.constants import CHEFS_FORM_ID, CHEFS_API_KEY,CHEFS_API_BASE_URL, CHEFS_FORM_ATTACHMENT_FIELD_NAME
import requests

def chefs_get_request(path_parameters):
    url = f"{CHEFS_API_BASE_URL}/{path_parameters}"

    try:
        response = requests.get(url, auth=(CHEFS_FORM_ID, CHEFS_API_KEY), timeout=30)
        response.raise_for_status()
        try:
          data = response.json()
          return data
        except ValueError:
          return response.content

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to CHEFS API {path_parameters}: {e}")
        raise

def get_chefs_status():
    return chefs_get_request("status")


def get_chefs_form(form_id=CHEFS_FORM_ID, form_version_id=None):
    if form_version_id is None:
      # version specifies the currently published form version
      return chefs_get_request(f"forms/{form_id}/version")
    else:
      # specify the version
      return chefs_get_request(f"forms/{form_id}/versions/{form_version_id}")



# Gets all submissions for the most recent form version,
# or a specific submission by ID or confirmation ID
def get_form_submissions(form_id=CHEFS_FORM_ID, submission_id=None, confirmation_id=None):
    if submission_id:
        response = chefs_get_request(f"submissions/{submission_id}")
        return response.get("submission")
    if confirmation_id:
        form = get_chefs_form(form_id)
        for version in form.get("versions"):
            version_id = version.get("id")
            submissions = chefs_get_request(f"forms/{form_id}/versions/{version_id}/submissions")
            if submissions and len(submissions) > 0:
                for submission in submissions:
                    if submission.get("confirmationId") == confirmation_id:
                        return submission
        return None

    submissions = chefs_get_request(f"forms/{form_id}/submissions")
    return submissions

# Get any attachments that have been uploaded to a chefs submission.
# This will return a list of attachments, each with a filename and base64-encoded data.
def get_submission_attachments(submission_id):
    submission = get_form_submissions(submission_id=submission_id)
    data = submission.get("submission").get("data")
    attachments = data.get(CHEFS_FORM_ATTACHMENT_FIELD_NAME, [])
    for attachment in attachments:
        attachment_id = attachment.get("data").get("id")
        attachment_data = chefs_get_request(f"files/{attachment_id}")
        attachment["data"] = attachment_data
        attachment["filename"] = attachment.get("originalName")
    return attachments


# Returns the CDOGS template for a specific form version or submission,
# or the first template if no version is specified
def get_form_cdogs_template(form_id=CHEFS_FORM_ID, form_version_id=None, submission_id=None):
    templates = chefs_get_request(f"forms/{form_id}/documentTemplates")

    if submission_id:
      submission = get_form_submissions(submission_id=submission_id)
      form_version_id = submission.get("formVersionId")

    if form_version_id:
        for template in templates:
            if template.get("formVersionId") == form_version_id:
                return template

    # If no form_version_id is provided, return the first template
    if templates:
        return templates[0]

    return None

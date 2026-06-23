import os

from chefs_helpers.chefs_helpers import get_chefs_form, get_form_cdogs_template, get_chefs_status, get_form_submissions, get_submission_attachments
from chefs_helpers.constants import CHEFS_FORM_ID, TEST_SUBMISSION_ID, TEST_CONFIRMATION_ID
from utilities.file_helper import save_file

def test_chefs_connection():

  # Get CHEFS status
  status = get_chefs_status()
  assert status is not None
  assert status.get("ready") == True
  print("CHEFS status:", status)

def test_chefs_form():

  # Get a CHEFS form instance
  form_details = get_chefs_form(CHEFS_FORM_ID)
  assert form_details is not None
  assert form_details.get("id") == CHEFS_FORM_ID
  # print("CHEFS form details:", form_details)


def test_chefs_submission_searches():

  # Get CHEFS form submissions
  submissions = get_form_submissions(CHEFS_FORM_ID)
  assert submissions is not None
  assert len(submissions) > 0
  print("CHEFS form submissions:", len(submissions))

  # Get single CHEFS form submission
  submission = get_form_submissions(submission_id=TEST_SUBMISSION_ID)
  assert submission is not None
  assert submission.get("id") is not None
  assert submission.get("id") == TEST_SUBMISSION_ID
  print("CHEFS form submission found:", submission.get("id"))

  # Get single CHEFS form submission
  submission = get_form_submissions(confirmation_id=TEST_CONFIRMATION_ID)
  assert submission is not None
  assert submission.get("id") is not None
  assert submission.get("id") == TEST_SUBMISSION_ID
  print("CHEFS form submission found:", submission.get("id"))


def test_chefs_cdogs_template():

  # Get a CHEFS form CDOGS template
  template = get_form_cdogs_template(CHEFS_FORM_ID)
  assert template is not None
  assert template.get("filename") is not None
  assert template.get("template") is not None
  assert template.get("template").get("data") is not None
  if os.getenv('GITHUB_ACTIONS'):
    print("CHEFS form template found:", template.get("filename"))
  else:
    file_path = save_file(template.get("filename"), template.get("template").get("data"))
    print("CHEFS form template downloaded to:", file_path)

def test_chefs_submission_attachments():

  # Get a CHEFS form submission attachments
  attachments = get_submission_attachments(TEST_SUBMISSION_ID)
  assert attachments is not None
  assert len(attachments) > 0

  for attachment in attachments:
    assert attachment.get("filename") is not None
    assert attachment.get("data") is not None
    assert isinstance(attachment.get("data"), bytes)
    if os.getenv('GITHUB_ACTIONS'):
        print("CHEFS form submission attachment found:", attachment.get("filename"))
    else:
      file_path = save_file(attachment.get("filename"), attachment.get("data"))
      print("CHEFS attachment downloaded to:", file_path)

# test_chefs_connection()
# test_chefs_form()
# test_chefs_submission_searches()
# test_chefs_cdogs_template()
test_chefs_submission_attachments()



from cdogs_helpers.cdogs_helpers import generate_cdogs_document
from chefs_helpers.chefs_helpers import get_form_cdogs_template, get_form_submissions
from chefs_helpers.constants import CHEFS_FORM_ID, CHEFS_TEST_SUBMISSION_ID
from utilities.file_helper import load_file, save_file
import base64
import json
import os

# Automated testing requires test files, and this code helps us by automatically generating them in case they change.

def generate_cdogs_template(form_id=CHEFS_FORM_ID):
    # Get a CHEFS form CDOGS template
    template = get_form_cdogs_template(form_id)
    file_path = save_file(template.get("filename"), template.get("template").get("data"))
    print("CHEFS form template downloaded to:", file_path)

def generate_chefs_answer_data(s_id=CHEFS_TEST_SUBMISSION_ID):
    # Get a CHEFS form submission
    submission = get_form_submissions(submission_id= s_id)
    data = submission.get("submission").get("data")
    file_path = save_file(f"chefs_test_answer_data.json", json.dumps(data))
    print("CHEFS form submission data downloaded to:", file_path)


def generate_cdogs_output():
    # Get the test answers file
    answers = load_file(os.getcwd() + "\\tests\\test_files\\chefs_test_answer_data.json").decode('utf-8')

    # Get test template file
    template = load_file(os.getcwd() + "\\tests\\test_files\\minimal_cdogs_template.docx")
    template_b64_string = base64.b64encode(template).decode('utf-8')

    # generate the CDOGS output
    output = generate_cdogs_document(
        answer_data=answers,
        outfile_name="test_cdogs_output",
        output_type="pdf",
        template_data=template_b64_string,
        template_encoding="base64",
        template_ext="docx"
    )
    # save the output to a file
    file_path = save_file(os.getcwd() + "\\tests\\test_files\\test_cdogs_output.pdf", output)

    print("CDOGS output data downloaded to:", file_path)

# generate_cdogs_template()
generate_chefs_answer_data()
generate_cdogs_output()

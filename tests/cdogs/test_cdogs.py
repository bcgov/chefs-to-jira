import base64
import os

from cdogs_helpers.cdogs_helpers import generate_cdogs_document, get_cdogs_token
from utilities.file_helper import load_file


def test_get_cdogs_token():
    token = get_cdogs_token()
    assert token is not None

def test_generate_cdogs_document():

    # Get str format chefs answer data from file
    answers = load_file(os.getcwd() + "/tests/test_files/chefs_test_answer_data.json").decode('utf-8')

    # Get template file
    template = load_file(os.getcwd() + "/tests/test_files/minimal_cdogs_template.docx")
    template_b64_string = base64.b64encode(template).decode('utf-8')

    content = generate_cdogs_document(
        answer_data=answers,
        outfile_name="test_cdogs_output",
        output_type="pdf",
        template_data=template_b64_string,
        template_encoding="base64",
        template_ext="docx"
    )
    assert content is not None
    assert content[:4] == b'%PDF'

if __name__ == "__main__":
    test_get_cdogs_token()
    test_generate_cdogs_document()

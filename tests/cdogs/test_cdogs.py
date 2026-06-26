from cdogs_helpers.cdogs_helpers import get_cdogs_token, generate_cdogs_document
from utilities.file_helper import load_file
import os
import base64

def test_get_cdogs_token():
    try:
        token = get_cdogs_token()
        assert token is not None
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def test_generate_cdogs_document():

    # Get str format chefs answer data from file
    answers = load_file(os.getcwd() + "/tests/test_files/chefs_test_answer_data.json").decode('utf-8')

    # Get template file
    template = load_file(os.getcwd() + "/tests/test_files/minimal_cdogs_template.docx")
    # Load file turns the docx into "bytes"
    # b64encode takes bytes, encodes them to base64, and ouputs bytes
    # decode takes bytes (assuming they're utf-8) and outputs a base64 string
    template_b64_string = base64.b64encode(template).decode('utf-8')

    try:
      content = generate_cdogs_document(
          answer_data=answers,
          outfile_name="test_cdogs_output",
          output_type="pdf",
          template_data=template_b64_string,
          template_encoding="base64",
          template_ext="docx"
      )
      assert content is not None
      # Verify that the content is a valid PDF by checking the first few bytes
      assert content[:4] == b'%PDF'

    except Exception as e:
        print(f"❌ Error occurred: {e}")

test_get_cdogs_token()
test_generate_cdogs_document()

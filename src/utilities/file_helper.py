# This is a simple file helper module for handling temporary files, mostly for testing.
import base64
import os
from utilities.constants import TEMP_DIR

# Stores templates and attachments from CHEFS locally for dev/testing
def save_file(filename, content):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    file_path = os.path.join(TEMP_DIR, filename)
    if isinstance(content, list):
        b64_string = ''.join(chr(b) for b in content)
        buffer = base64.b64decode(b64_string)
    elif  isinstance(content, bytes):
        buffer = content
    elif is_json(content):
        buffer = content.encode('utf-8')
    else:
        buffer = base64.b64decode(content)
    with open(file_path, 'wb') as f:
        f.write(buffer)
    return file_path


# Loads test files for CHEFS/CDOGS locally for dev/testing
def load_file(filepath):

    # open a file and read it as bytes
    with open(filepath, 'rb') as f:
        content = f.read()

    return content

# Helper function to identify if content is json
def is_json(content):
    try:
        import json
        json.loads(content)
        return True
    except ValueError:
        return False

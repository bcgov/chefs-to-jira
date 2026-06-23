# This is a simple file helper module for handling temporary files, mostly for testing.
import base64
import os
from utilities.constants import TEMP_DIR

# Can handle both templates and attachments from CHEFS
def save_file(filename, content):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    file_path = os.path.join(TEMP_DIR, filename)
    if isinstance(content, list):
        b64_string = ''.join(chr(b) for b in content)
        buffer = base64.b64decode(b64_string)
    elif  isinstance(content, bytes):
        buffer = content
    else:
        buffer = base64.b64decode(content)
    with open(file_path, 'wb') as f:
        f.write(buffer)
    return file_path

from src.utilities.send_admin_email import send_admin_email
from py_compile import main
import sys

if __name__ == "__main__":
    main(sys.argv[1:])
    send_admin_email("Hello World!")

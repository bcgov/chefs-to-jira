import os
from py_compile import main
import sys
import constants
from log_helper import LOGGER
import smtplib
import socket
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .core.config import Configuration

def send_admin_email(message_detail):
    msg = MIMEMultipart("related")
    msg["Subject"] = "Script Report"
    if constants.DEBUG_EMAIL == "":
        msg["From"] = "NRIDS.Optimize@gov.bc.ca"
        msg["To"] = "NRIDS.Optimize@gov.bc.ca"
    else:
        msg["To"] = constants.DEBUG_EMAIL
        msg["From"] = constants.DEBUG_EMAIL

    dir_path = os.path.dirname(os.path.realpath(__file__))
    host_name = socket.gethostname()
    html = (
        "<html><head></head><body><p>"
        + "A scheduled script send_usage_emails.py has sent an automated report email."
        + "<br />Server: "
        + str(host_name)
        + "<br />File Path: "
        + dir_path
        + "<br />"
        + str(message_detail)
        + "</p></body></html>"
    )
    msg.attach(MIMEText(html, "html"))
    s = smtplib.SMTP(constants.SMTP_SERVER)
    s.sendmail(msg["From"], msg["To"], msg.as_string())
    s.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
    send_admin_email("Hello World!")

    # Give developers time to look at OCP pod terminal/details after a failure/success before terminating.
    LOGGER.info("Script Complete, pausing for 5 minutes...")
    time.sleep(300)
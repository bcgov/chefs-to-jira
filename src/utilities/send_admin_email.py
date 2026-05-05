import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import src.utilities.constants as constants

def send_admin_email(message_detail):
    msg = MIMEMultipart("related")
    msg["Subject"] = "Script Report"
    if constants.FROM_EMAIL == "":
        msg["From"] = "CHEFSToJiraDONotReply@gov.bc.ca"
    else:
        msg["From"] = constants.FROM_EMAIL
    msg["To"] = constants.DEBUG_EMAIL

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

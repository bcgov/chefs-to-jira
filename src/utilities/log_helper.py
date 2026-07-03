import logging
from utilities.constants import LOG_LEVEL
from utilities.send_admin_email import send_admin_email

# Filter to exclude DEBUG, INFO and WARNING messages from being sent via email
# class ExcludeDebugInfoAndWarningFilter(logging.Filter):
#     def filter(self, record):
#         # Return False to drop, True to keep
#         # Using numeric levels is safer and slightly faster
#         return record.levelno not in (logging.DEBUG, logging.INFO, logging.WARNING)

# Custom log handler that calls an external function (send_admin_email)
class CustomFunctionHandler(logging.Handler):
    def emit(self, record):
        # Format the log message using the handler's formatter
        log_message = self.format(record)
        # Call your external function with data from the log record
        send_admin_email(log_message)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')

# 1. Initialize the logger
LOGGER = logging.getLogger()
LOGGER.setLevel(LOG_LEVEL)

# 2. Setup StreamHandler (Console) has all logs
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
LOGGER.addHandler(console_handler)

# 3. Emails fire for ERROR and CRITICAL
email_handler = CustomFunctionHandler()
email_handler.setLevel(logging.ERROR)
# email_handler.addFilter(ExcludeDebugInfoAndWarningFilter())
email_handler.setFormatter(formatter)
LOGGER.addHandler(email_handler)

import os
from dotenv import load_dotenv, find_dotenv

envPath = find_dotenv(usecwd=True)
if envPath:
    load_dotenv(dotenv_path=envPath)

# ---- ESS NATS Stream Configuration ----
ESS_SERVER = os.getenv("ess_server_url")
ESS_STREAM_NAME = os.getenv("ess_stream_name")
ESS_FILTER_SUBJECTS = ["PUBLIC.forms.>", "PRIVATE.forms.>"]
ESS_MAX_MESSAGES = int(os.getenv("ess_max_messages"))
ESS_DURABLE_NAME = os.getenv("ess_durable_name")
ESS_SOURCE_FILTER = os.getenv("ess_source")

# ---- ESS NATS Connection Credentials ----
ESS_NKEY_SEED = os.getenv("ess_nkey_seed")
ESS_NKEY_USER = os.getenv("ess_nkey_user")
ESS_ENCRYPTION_KEY = os.getenv("ess_encryption_key")

# ---- ESS NATS Admin Credentials (for stream creation) ----
ESS_ADMIN_USER = os.getenv("ess_admin_user")
ESS_ADMIN_PASSWORD = os.getenv("ess_admin_password")


import os
import dotenv

envPath = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(envPath):
    print("loading dot env...")
    dotenv.load_dotenv()

SMTP_SERVER = os.environ['SMTP_SERVER']
DEBUG_EMAIL = os.environ['DEBUG_EMAIL']
DEBUG_EMAIL = os.environ['FROM_EMAIL']

import os
from dotenv import load_dotenv
import motor.motor_asyncio
from urllib.parse import quote_plus

load_dotenv()

DB_URL = os.getenv("DB_URL", "").strip()
DB_NAME = os.getenv("DB_NAME", "").strip()
DB_USERNAME = os.getenv("DB_USERNAME", "").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_AUTH_SOURCE = os.getenv("DB_AUTH_SOURCE", "").strip()

if not DB_URL or not DB_NAME:
    raise ValueError("DB_URL and DB_NAME are required.")

# Build URI depending on whether auth is configured
if DB_USERNAME and DB_PASSWORD:
    auth_source = DB_AUTH_SOURCE or DB_NAME
    MONGO_URI = (
        f"mongodb://{quote_plus(DB_USERNAME)}:{quote_plus(DB_PASSWORD)}@"
        f"{DB_URL[len('mongodb://'):]}/{DB_NAME}"
        f"?authSource={auth_source}"
    )
else:
    MONGO_URI = f"{DB_URL}/{DB_NAME}"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

interview_transcripts_collection = db["analysis_results"]
interview_analysis_collection = db["interview_analysis"]

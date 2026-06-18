import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import motor.motor_asyncio

load_dotenv()

# Load environment variables safely
DB_URL = os.getenv("DB_URL", "").strip()
DB_USERNAME = quote_plus(os.getenv("DB_USERNAME", "").strip())
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", "").strip())
DB_NAME = os.getenv("DB_NAME", "").strip()
DB_AUTH_SOURCE = os.getenv("DB_AUTH_SOURCE", "").strip()

# Ensure required fields are present
if not all([DB_URL, DB_USERNAME, DB_PASSWORD, DB_NAME]):
    raise ValueError("Missing required MongoDB credentials.")

# Set authSource fallback
auth_source = DB_AUTH_SOURCE if DB_AUTH_SOURCE else DB_NAME

# Build final Mongo URI
MONGO_URI = f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_URL[len('mongodb://'):]}/{DB_NAME}?authMechanism=DEFAULT&authSource={auth_source}"

# Connect to Mongo
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

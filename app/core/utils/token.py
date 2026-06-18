from pathlib import Path
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


SERVICE_SECRET = os.getenv("SERVICE_SECRET")
TOKEN_SECRET = os.getenv("TOKEN_SECRET")

def generate_internal_token():
    if SERVICE_SECRET is None:
        raise RuntimeError("SERVICE_SECRET env variable not set")
    
    payload = {
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "sub": "internal_service"
    }
    
    token = jwt.encode(payload, SERVICE_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


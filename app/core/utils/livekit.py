import os
import time
import aiohttp
import jwt  # PyJWT
 
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "").strip()
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "").strip()
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "").strip()
 
# ✅ FIX 1: Always use https:// for REST API calls (not wss://)
LIVEKIT_API_URL = (
    LIVEKIT_URL
    .replace("wss://", "https://")
    .replace("ws://", "http://")
)

def _get_unix_time() -> int:
    """
    Returns Unix timestamp adjusted for Windows clock skew.
    Subtracting 90s covers the ~71s your system clock is ahead.
    """
    return int(time. time()) - 90
 
def _build_server_token(
    real_now: int
) -> str:

    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": LIVEKIT_API_KEY,
        "nbf": real_now - 10,
        "exp": real_now + 3600,

        "video": {
            "roomCreate": True,
            "roomList": True,
            "roomRecord": True,

            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True,
        },
    }

    token = jwt.encode(
        payload,
        LIVEKIT_API_SECRET,
        algorithm="HS256"
    )

    return (
        token
        if isinstance(token, str)
        else token.decode("utf-8")
    ) 
 
def _build_participant_token(real_now: int, room_name: str, candidate_name: str) -> str:
    """Build a participant JWT for joining a room."""
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": candidate_name,
        "name": candidate_name,
        "nbf": real_now - 10,
        "exp": real_now + 3600,
        "video": {
            "roomJoin": True,
            "room": room_name,
            "canPublish": True,
            "canSubscribe": True,
        },
    }
    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
    return token if isinstance(token, str) else token.decode("utf-8")
 
 
async def create_room(room_name: str):
    """Create a LiveKit room via direct HTTP call."""
 
    real_now = _get_unix_time()
    token = _build_server_token(real_now)
 
    url = f"{LIVEKIT_API_URL}/twirp/livekit.RoomService/CreateRoom"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
 
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={"name": room_name}) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(
                    f"Failed to create LiveKit room: {resp.status}, body={text!r}"
                )
            data = await resp.json()
 
    class _Room:
        def __init__(self, d):
            self.sid  = d.get("sid", "")
            self.name = d.get("name", room_name)
 
    return _Room(data)
 
 
async def create_livekit_session(room_name: str, candidate_name: str) -> dict:
    real_now = _get_unix_time()
 
    room = await create_room(room_name)
    token = _build_participant_token(real_now, room_name, candidate_name)
 
    return {
        "room_id": room.sid,
        "room_name": room.name,
        "token": token,
    }
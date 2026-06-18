from app.core.utils.livekit import (
    LIVEKIT_API_KEY,
    LIVEKIT_API_URL,
    LIVEKIT_API_SECRET,
    _build_server_token,
    _get_unix_time
)
import os
import aiohttp
from livekit import api


async def list_egress():

    real_now = _get_unix_time()

    token = _build_server_token(real_now)

    url = (
        f"{LIVEKIT_API_URL}"
        "/twirp/livekit.Egress/ListEgress"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(
            url,
            headers=headers,
            json={}
        ) as resp:

            print(
                "EGRESS:",
                await resp.text()
            )
            
async def list_rooms():

    real_now = _get_unix_time()

    token = _build_server_token(
        real_now
    )

    print("LIVEKIT_API_URL =", LIVEKIT_API_URL)
    print("LIVEKIT_API_KEY =", LIVEKIT_API_KEY)
    print("TOKEN =", token)

    url = (
        f"{LIVEKIT_API_URL}"
        "/twirp/livekit.RoomService/"
        "ListRooms"
    )

    headers = {
        "Authorization":
            f"Bearer {token}",
        "Content-Type":
            "application/json"
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(
            url,
            headers=headers,
            json={}
        ) as resp:

            print(
                "ROOMS:",
                await resp.text()
            )


async def start_recording(room_name: str):
    real_now = _get_unix_time()
    token = _build_server_token(real_now)

    url = f"{LIVEKIT_API_URL}/twirp/livekit.Egress/StartRoomCompositeEgress"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "room_name": room_name,
        "layout": "speaker",
        "file_outputs": [
            {
                "file_type": 1,          # 1 = MP4
                "filepath": f"/out/{room_name}.mp4",
                # No s3/gcs = saves to local /out directory
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            text = await resp.text()
            print("Start Egress Status:", resp.status)
            print("Start Egress Response:", text)

            if resp.status != 200:
                raise Exception(f"Egress failed: {text}")

            import json as _json
            data = _json.loads(text)

    return {"egressId": data["egress_id"]}

async def stop_recording(egress_id: str):
    real_now = _get_unix_time()
    token = _build_server_token(real_now)

    url = f"{LIVEKIT_API_URL}/twirp/livekit.Egress/StopEgress"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {"egress_id": egress_id}   # ← snake_case for self-hosted

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            text = await resp.text()
            print("Stop Egress Response:", resp.status, text)

            if resp.status != 200:
                raise Exception(f"Stop failed: {text}")

            import json as _json
            data = _json.loads(text)

    # Return the local filepath so it can be saved to DB
    location = data.get("file_results", [{}])[0].get("filename", "")
    return location
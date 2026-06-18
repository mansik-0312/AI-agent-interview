import os
import httpx
from app.core.utils.token import generate_internal_token
from dotenv import load_dotenv

load_dotenv()

async def call_internal_get(path: str, headers: dict = None, params: dict = None):
    try:
        url = f"{os.getenv('API_GATEWAY_URL')}{path}"

        # Generate internal token if not provided
        if headers is None:
            internal_token = generate_internal_token()
            headers = {
                "Authorization": f"Bearer {internal_token}",
                "x-internal-service": "true"
            }

        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(url, headers=headers, params=params)

            try:
                json_data = response.json()
            except Exception as json_err:
                raise ValueError(f"Invalid JSON response from {url}") from json_err

            response.raise_for_status()

        return {
            "status": True,
            "msg": "Request successful",
            "data": json_data.get("data")
        }

    except httpx.RequestError as e:
        return {
            "status": False,
            "msg": "HTTP request failed",
            "error": str(e),
            "data": None
        }

    except httpx.HTTPStatusError as e:
        try:
            err_json = e.response.json()
            err_msg = err_json.get("msg", e.response.text)
        except Exception:
            err_msg = e.response.text or str(e)

        return {
            "status": False,
            "msg": err_msg,
            "error": str(e),
            "data": None
        }

    except Exception as e:
        return {
            "status": False,
            "msg": "Unexpected error occurred",
            "error": str(e),
            "data": None
        }

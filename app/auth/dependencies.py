from fastapi import Depends, HTTPException, Header, Request
import jwt, os
from app.core.utils.internal_requests import call_internal_get
from app.services.authorization import check_user_authorization
from typing import Callable

TOKEN_SECRET = os.getenv("TOKEN_SECRET")
SERVICE_SECRET = os.getenv("SERVICE_SECRET")

async def get_current_user(
    authorization: str = Header(...),
    x_internal_service: str = Header(None)
):
    if not authorization.startswith("Bearer "):
        print("Invalid Authorization header format")
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization.split(" ")[1]
    is_internal = x_internal_service == "true"
    secret = SERVICE_SECRET if is_internal else TOKEN_SECRET

    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        print("token:", decoded)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Superadmin bypass
    if decoded.get("userType") == "superadmin":
        return decoded

    # INTERNAL: skip DB lookup
    if is_internal:
        return {
            **decoded,
            "scope": "internal",
            "userType": "internal-service"  # Optional, for downstream logic
        }

    # EXTERNAL: validate userId
    user_id = decoded.get("userId")
    print("User id: " ,user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: userId missing")

    res = await call_internal_get("/userService/user/newList?pageNo=1&limit=1000")
    # print("User resp: ", res)
    if not res.get("status"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    users = res["data"]
    # print("User: " , users)
    matched_user = next((u for u in users if u["id"] == user_id), None)
    # print("Matched user", matched_user)
    if not matched_user:
        raise HTTPException(status_code=401, detail="User not found")

    return matched_user

# --------------------------------------------------------
# Dependency: Permission check for a given module+action
# --------------------------------------------------------
def authorize(permission: str, module_name: str):
    async def dependency(request: Request):
        user = getattr(request.state, "user", None)
        # Block if user not attached in request
        if not user:
            raise HTTPException(status_code=403, detail="User context missing in request")
        
        # Call permission-checking logic (based on role & module)
        auth_result = await check_user_authorization(user, permission, module_name)
        if not auth_result["authorized"]:
            raise HTTPException(status_code=403, detail=auth_result["message"])

        # Attach authorized user info in request.state if needed later
        request.state.auth_user = auth_result["user"]
    return dependency  # Just return the function


def get_authorized_user(permission: str, module_name: str) -> Callable:
    async def wrapper(
        request: Request,
        current_user: dict = Depends(get_current_user),
    ):
        request.state.user = current_user  # Ensures availability before authorize()
        auth_result = await check_user_authorization(current_user, permission, module_name)
        if not auth_result["authorized"]:
            raise HTTPException(status_code=403, detail=auth_result["message"])
        return current_user
    return wrapper
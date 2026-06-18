from app.core.utils.internal_requests import call_internal_get

async def get_all_roles_with_permissions():
    try:
        page = 1
        limit = 50
        all_roles = []
        has_more = True

        while has_more:
            response = await call_internal_get(f"/userService/role/list?pageNo={page}&limit={limit}")

            if not response.get("status") or not isinstance(response.get("data"), list):
                raise Exception("Failed to fetch roles")

            all_roles += response["data"]

            if len(response["data"]) < limit:
                has_more = False
            else:
                page += 1

        return {
            "status": True,
            "data": all_roles
        }

    except Exception as e:
        return {
            "status": False,
            "msg": str(e),
            "data": None
        }

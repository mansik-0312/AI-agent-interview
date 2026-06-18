from app.services.roles import get_all_roles_with_permissions  # You'll define this
from typing import Dict, Any

async def check_user_authorization(user: dict, required_permission: str, module_name: str) -> dict:

    user_id = user.get("userId") or user.get("id")

    if not user or not user_id:
        return {
            "authorized": False,
            "user": None,
            "message": "User ID is missing"
        }

    # Bypass for superadmin or internal-service
    if user.get("userType") in ["superadmin", "internal-service"]:
        return {
            "authorized": True,
            "user": user,
            "message": "Authorized (superadmin/internal-service)"
        }

    if not user.get("roleId"):
        return {
            "authorized": False,
            "user": None,
            "message": "Role ID is missing for non-superadmin user"
        }

    # Fetch all roles
    roles_response = await get_all_roles_with_permissions()
    if not roles_response.get("status"):
        return {
            "authorized": False,
            "user": None,
            "message": "Failed to fetch roles for permission check"
        }

    all_roles = roles_response.get("data", [])
    
    # Find role by ID
    role_id = str(user["roleId"])
    matched_role = next((r for r in all_roles if str(r["_id"]) == role_id), None)
    if not matched_role:
        return {
            "authorized": False,
            "user": user,
            "message": "Role not found for user"
        }

    # Module-level permission check
    module_access = next(
        (entry for entry in matched_role.get("access", [])
        if entry.get("module", {}).get("name", "").lower() == module_name.lower()),
        None
    )
    # Permission check only if module_access is not None
    if not module_access:
        return {
            "authorized": False,
            "user": user,
            "message": f"No access found for module '{module_name}'"
        }

    # Now safely check permissions
    has_permission = any(
        p.get("name") == required_permission and p.get("status") == "true"
        for p in module_access.get("permissions", [])
    )

    if not has_permission:
        return {
            "authorized": False,
            "user": user,
            "message": f"Permission '{required_permission}' denied for module '{module_name}'"
        }

    return {
        "authorized": True,
        "user": user,
        "message": "Authorized"
    }

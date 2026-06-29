# app/controllers/dashboard_controller.py

from app.services.dashboard_service import (
    get_dashboard_service,
    get_upcoming_interviews_service,
    get_recent_interviews_service
)
from app.core.utils.response_mixin import (
    CustomResponseMixin
)
from app.core.utils.helper import serialize_datetime_fields

response = CustomResponseMixin()


async def get_dashboard_controller(
    current_user
):
    result = await get_dashboard_service(
        current_user=current_user
    )

    result = serialize_datetime_fields(
        result
    )

    return response.success_message(
        "Dashboard fetched successfully",
        result
    )


async def get_upcoming_interviews_controller(
    pagination,
    current_user
):
    result = await get_upcoming_interviews_service(
        pagination=pagination,
        current_user=current_user
    )

    result = serialize_datetime_fields(result)

    return response.success_message(
        "Upcoming interviews fetched successfully",
        result
    )


async def get_recent_interviews_controller(
    pagination,
    current_user
):
    result = await get_recent_interviews_service(
        pagination=pagination,
        current_user=current_user
    )

    result = serialize_datetime_fields(result)

    return response.success_message(
        "Recent interviews fetched successfully",
        result
    )
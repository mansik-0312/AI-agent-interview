# app/routes/dashboard.py

from fastapi import APIRouter, Depends
from app.controllers.dashboard_controller import (
    get_dashboard_controller,
    get_upcoming_interviews_controller,
    get_recent_interviews_controller
)
from app.auth.dependencies import (
    get_current_user
)

from app.core.utils.pagination import StandardResultsSetPagination, pagination_params

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_dashboard_controller(
        current_user=current_user
    )


@router.get("/dashboard/upcoming-interviews")
async def get_upcoming_interviews(
    pagination: StandardResultsSetPagination = Depends(
        pagination_params
    ),
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_upcoming_interviews_controller(
        pagination=pagination,
        current_user=current_user
    )


@router.get("/dashboard/recent-interviews")
async def get_recent_interviews(
    pagination: StandardResultsSetPagination = Depends(
        pagination_params
    ),
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_recent_interviews_controller(
        pagination=pagination,
        current_user=current_user
    )
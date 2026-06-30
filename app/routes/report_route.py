from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user

from app.controllers.report_controller import get_interview_report_controller

router = APIRouter(
    prefix="/reports",
    tags=["Interview Reports"]
)


@router.get("/{interview_id}")
async def get_interview_report_route(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await get_interview_report_controller(
        interview_id,
        current_user
    )

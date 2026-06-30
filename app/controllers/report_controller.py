from app.services.report_serverice import get_interview_report_service


async def get_interview_report_controller(
    interview_id: str,
    current_user
):
    return await get_interview_report_service(interview_id)

from app.services.interview_service import (
    create_interview_service,
    get_current_question_service,
    next_question_service,
    submit_answer_service,
    complete_interview_service,
    get_interviews_service,
    get_interview_by_id_service,
    start_interview_service,
    get_shortlisted_candidates_service,
    get_interview_templates_service
)
from app.services.analysis import (
    analyze_interview_service
)

from app.core.utils.response_mixin import (
    CustomResponseMixin
)

response = CustomResponseMixin()


async def create_interview_controller(
    payload,
    current_user
):

    result = await create_interview_service(
        payload,
        current_user
    )

    return response.success_message(
        "Interview scheduled successfully",
        result
    )

async def get_current_question_controller(
    interview_id: str
):

    result = await get_current_question_service(
        interview_id
    )

    return response.success_message(
        message="Current question fetched successfully",
        data=result,
        status_code=200
    )

async def next_question_controller(
    interview_id: str
):

    result = await next_question_service(
        interview_id
    )

    if result.get("completed"):

        return response.success_message(
            message="Interview completed",
            data=result
        )

    return response.success_message(
        message="Next question fetched successfully",
        data=result
    )

async def submit_answer_controller(
    interview_id: str,
    payload
):

    result = await submit_answer_service(
        interview_id,
        payload
    )

    return response.success_message(
        message="Answer submitted successfully",
        data=result
    )

async def start_interview_controller(
    interview_id: str
):

    result = await start_interview_service(
        interview_id
    )

    return response.success_message(
        "Interview started successfully",
        result
    )


async def complete_interview_controller(
    interview_id: str
):

    result = await complete_interview_service(
        interview_id
    )

    return response.success_message(
        message="Interview completed successfully",
        data=result
    )


async def get_interviews_controller(
    page: int = 1,
    limit: int = 10
):
 
    interviews, total = await get_interviews_service(page, limit)
 
    return response.success_message(
        "Interviews fetched successfully",
        {
            "items": interviews,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": (total + limit - 1) // limit if limit else 1
        }
    )


async def get_interview_by_id_controller(
    interview_id
):

    interview = await (
        get_interview_by_id_service(
            interview_id
        )
    )

    return response.success_message(
        "Interview fetched successfully",
        interview
    )

async def analyze_interview_controller(
    interview_id: str
):

    result = await analyze_interview_service(
        interview_id
    )

    return response.success_message(
        message="Interview analyzed successfully",
        data=result
    )

async def get_shortlisted_candidates_controller():

    candidates = await get_shortlisted_candidates_service()

    return response.success_message(
        "Shortlisted candidates fetched successfully",
        candidates
    )

async def get_interview_templates_controller():

    templates = await get_interview_templates_service()

    return response.success_message(
        "Interview templates fetched successfully",
        templates
    )

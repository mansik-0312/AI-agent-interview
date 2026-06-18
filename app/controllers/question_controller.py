from app.services.question_service import (
    create_question_service,
    get_questions_service,
    get_question_by_id_service,
    update_question_service,
    delete_question_service
)

from app.schemas.question_schema import (
    QuestionCreate,
    QuestionUpdate
)

from app.core.utils.response_mixin import (
    CustomResponseMixin
)

response = CustomResponseMixin()


async def create_question_controller(
    payload: QuestionCreate,
    current_user: dict
):
    question = await create_question_service(
        payload=payload,
        current_user=current_user
    )

    return response.success_message(
        message="Question created successfully",
        data=question
    )


async def get_questions_controller(
    templateId: str,
    current_user: dict
):
    questions = await get_questions_service(
        templateId=templateId
    )

    return response.success_message(
        message="Questions fetched successfully",
        data=questions
    )


async def get_question_by_id_controller(
    question_id: str
):
    question = await get_question_by_id_service(
        question_id=question_id
    )

    return response.success_message(
        message="Question fetched successfully",
        data=question
    )


async def update_question_controller(
    question_id: str,
    payload: QuestionUpdate,
    current_user: dict
):
    question = await update_question_service(
        question_id=question_id,
        payload=payload,
        current_user=current_user
    )

    return response.success_message(
        message="Question updated successfully",
        data=question
    )


async def delete_question_controller(
    question_id: str,
    current_user: dict
):
    await delete_question_service(
        question_id=question_id,
        current_user=current_user
    )

    return response.success_message(
        message="Question deleted successfully"
    )
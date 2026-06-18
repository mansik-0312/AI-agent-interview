from bson import ObjectId

from app.models.question import Question
from app.models.interview_template import (
    InterviewTemplate
)

from app.core.utils.response_mixin import (
    CustomResponseMixin
)

response = CustomResponseMixin()


async def create_question_service(
    payload,
    current_user
):

    template = await InterviewTemplate.get(
        ObjectId(payload.templateId)
    )

    if not template:
        response.raise_exception(
            "Template not found"
        )

    question = Question(
        templateId=ObjectId(
            payload.templateId
        ),
        questionText=payload.questionText,
        expectedAnswer=payload.expectedAnswer,
        duration=payload.duration,
        weight=payload.weight,
        difficulty=payload.difficulty,
        createdBy=ObjectId(
            current_user["id"]
        )
    )

    await question.insert()

    return {
        "id": str(question.id),
        "templateId": str(
            question.templateId
        ),
        "questionText": question.questionText,
        "expectedAnswer": question.expectedAnswer,
        "duration": question.duration,
        "weight": question.weight,
        "difficulty": question.difficulty,
        "active": question.active
    }


async def get_questions_service(
    templateId=None
):

    filters = {
        "deleted.status": False
    }

    if templateId:
        filters["templateId"] = ObjectId(
            templateId
        )

    questions = await Question.find(
        filters
    ).to_list()

    response_data = []

    for question in questions:

        response_data.append(
            {
                "id": str(question.id),
                "templateId": str(
                    question.templateId
                ),
                "questionText": question.questionText,
                "expectedAnswer": question.expectedAnswer,
                "duration": question.duration,
                "weight": question.weight,
                "difficulty": question.difficulty,
                "active": question.active
            }
        )

    return response_data


async def get_question_by_id_service(
    question_id: str
):

    question = await Question.get(
        ObjectId(question_id)
    )

    if not question:
        response.raise_exception(
            "Question not found"
        )

    return {
        "id": str(question.id),
        "templateId": str(
            question.templateId
        ),
        "questionText": question.questionText,
        "expectedAnswer": question.expectedAnswer,
        "duration": question.duration,
        "weight": question.weight,
        "difficulty": question.difficulty,
        "active": question.active
    }


async def update_question_service(
    question_id,
    payload,
    current_user
):

    question = await Question.get(
        ObjectId(question_id)
    )

    if not question:
        response.raise_exception(
            "Question not found"
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            question,
            key,
            value
        )

    question.updatedBy = ObjectId(
        current_user["userId"]
    )

    await question.save()

    return {
        "id": str(question.id)
    }


async def delete_question_service(
    question_id,
    current_user
):

    question = await Question.get(
        ObjectId(question_id)
    )

    if not question:
        response.raise_exception(
            "Question not found"
        )

    question.deleted.status = True

    question.updatedBy = ObjectId(
        current_user["userId"]
    )

    await question.save()
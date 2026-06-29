from bson import ObjectId

from app.models.question import Question
from app.models.interview_template import (
    InterviewTemplate
)

from app.core.utils.response_mixin import (
    CustomResponseMixin
)

from app.core.utils.pagination import (
    StandardResultsSetPagination,
    build_paginated_response
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
    pagination: StandardResultsSetPagination,
    templateId: str = None,
    difficulty: str = None,
    active: bool = None,
    search: str = None
):

    filters = {
        "deleted.status": False
    }

    if templateId:
        filters["templateId"] = ObjectId(
            templateId
        )

    if difficulty:
        filters["difficulty"] = difficulty

    if active is not None:
        filters["active"] = active

    if search:
        filters["questionText"] = {
            "$regex": search,
            "$options": "i"
        }

    # Dashboard stats
    total_questions = await Question.find(
        {
            "deleted.status": False
        }
    ).count()

    active_questions = await Question.find(
        {
            "deleted.status": False,
            "active": True
        }
    ).count()

    inactive_questions = await Question.find(
        {
            "deleted.status": False,
            "active": False
        }
    ).count()

    # Total records after filters
    total_records = await Question.find(
        filters
    ).count()

    query = Question.find(
        filters
    )

    if (
        pagination.page
        and pagination.page_size
    ):
        query = query.skip(
            pagination.skip
        ).limit(
            pagination.limit
        )

    questions = await query.to_list()

    # Fetch template names
    template_ids = list(
        {
            question.templateId
            for question in questions
        }
    )

    template_map = {}

    if template_ids:
        templates = await InterviewTemplate.find(
            {
                "_id": {
                    "$in": template_ids
                }
            }
        ).to_list()

        template_map = {
            str(template.id): template.name
            for template in templates
        }

    records = []

    for question in questions:
        records.append(
            {
                "id": str(
                    question.id
                ),
                "templateId": str(
                    question.templateId
                ),
                "templateName": template_map.get(
                    str(
                        question.templateId
                    ),
                    ""
                ),
                "questionText":
                    question.questionText,
                "expectedAnswer":
                    question.expectedAnswer,
                "duration":
                    question.duration,
                "weight":
                    question.weight,
                "difficulty":
                    question.difficulty,
                "active":
                    question.active,
                "createdAt":
                    question.createdAt
            }
        )

    paginated_data = (
        build_paginated_response(
            records=records,
            page=(
                pagination.page
                or 1
            ),
            page_size=(
                pagination.page_size
                or total_records
                or 1
            ),
            total_records=total_records
        )
    )

    return {
        "stats": {
            "totalQuestions":
                total_questions,
            "activeQuestions":
                active_questions,
            "inactiveQuestions":
                inactive_questions
        },
        **paginated_data
    }


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
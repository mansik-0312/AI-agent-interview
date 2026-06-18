from bson import ObjectId

from app.models.interview_template import (
    InterviewTemplate
)


async def create_template_service(
    payload,
    current_user
):

    template = InterviewTemplate(
        name=payload.name,
        description=payload.description,
        totalQuestions=payload.totalQuestions,
        createdBy=ObjectId(
            current_user["userId"]
        )
    )

    await template.insert()

    return {
        "id": str(template.id),
        "name": template.name,
        "description": template.description,
        "totalQuestions": template.totalQuestions
    }


async def get_templates_service():

    templates = await InterviewTemplate.find(
        {
            "deleted.status": False
        }
    ).to_list()

    response = []

    for template in templates:

        response.append(
            {
                "id": str(template.id),
                "name": template.name,
                "description": template.description,
                "totalQuestions": template.totalQuestions,
                "active": template.active
            }
        )

    return response
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
            current_user["id"]
        )
    )

    await template.insert()

    return {
        "id": str(template.id),
        "name": template.name,
        "description": template.description,
        "totalQuestions": template.totalQuestions,
        "active": template.active,
        "createdAt": template.createdAt
    }


async def get_templates_service(
    pagination,
    active=None
):

    filters = {
        "deleted.status": False
    }

    if active is not None:
        filters["active"] = active

    total_records = (
        await InterviewTemplate.find(
            filters
        ).count()
    )

    query = (
        InterviewTemplate.find(filters)
        .sort(-InterviewTemplate.createdAt)
    )

    if (
        pagination.page is not None
        and
        pagination.page_size is not None
    ):
        query = (
            query
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

    templates = await query.to_list()

    response = []

    for template in templates:

        response.append(
            {
                "id": str(template.id),
                "name": template.name,
                "description": template.description,
                "totalQuestions": template.totalQuestions,
                "active": template.active,
                "createdAt": template.createdAt,
                "createdBy": (
                    str(template.createdBy)
                    if template.createdBy
                    else None
                )
            }
        )

    return response, total_records
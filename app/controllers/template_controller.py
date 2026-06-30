from app.services.template_service import (
    create_template_service,
    get_templates_service
)

from app.schemas.template_schema import (
    InterviewTemplateCreate
)

from app.core.utils.response_mixin import (
    CustomResponseMixin
)
from app.core.utils.helper import serialize_datetime_fields,convert_objectid_to_str

from app.core.utils.pagination import build_paginated_response

response = CustomResponseMixin()


async def create_template_controller(
    payload: InterviewTemplateCreate,
    current_user: dict
):

    template = await create_template_service(
        payload=payload,
        current_user=current_user
    )

    return response.success_message(
        message="Template created successfully",
        data=serialize_datetime_fields(template)
    )


async def get_templates_controller(
    pagination,
    active,
    current_user
):

    records, total_records = (
        await get_templates_service(
            pagination=pagination,
            active=active
        )
    )

    return response.success_message(
        "Templates fetched successfully",
        serialize_datetime_fields(
            convert_objectid_to_str(
                build_paginated_response(
                    records=records,
                    page=pagination.page or 1,
                    page_size=pagination.page_size or total_records,
                    total_records=total_records
                )
            )
        )
    )
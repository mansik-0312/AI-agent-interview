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
        data=template
    )


async def get_templates_controller(
    current_user: dict
):

    templates = await get_templates_service()

    return response.success_message(
        "Templates fetched successfully",
        data=[
            serialize_datetime_fields(
                convert_objectid_to_str(
                    templates
                )
            )
        ]
    )
from fastapi import APIRouter, Depends

from app.controllers.template_controller import (
    create_template_controller,
    get_templates_controller
)

from app.schemas.template_schema import (
    InterviewTemplateCreate
)

from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/templates",
    tags=["Interview Templates"]
)


@router.post("")
async def create_template(
    payload: InterviewTemplateCreate,
    current_user: dict = Depends(get_current_user)
):
    return await create_template_controller(
        payload=payload,
        current_user=current_user
    )


@router.get("")
async def get_templates(
    current_user: dict = Depends(get_current_user)
    ):
    return await get_templates_controller(
        current_user=current_user
    )
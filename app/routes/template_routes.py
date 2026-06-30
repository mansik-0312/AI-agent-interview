from fastapi import APIRouter, Depends, Query

from typing import Optional

from app.controllers.template_controller import (
    create_template_controller,
    get_templates_controller
)

from app.schemas.template_schema import (
    InterviewTemplateCreate
)

from app.auth.dependencies import get_current_user

from app.core.utils.pagination import StandardResultsSetPagination, pagination_params

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
    pagination: StandardResultsSetPagination = Depends(
        pagination_params
    ),
    active: Optional[bool] = Query(None),
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_templates_controller(
        pagination=pagination,
        active=active,
        current_user=current_user
    )
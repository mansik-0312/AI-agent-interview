from fastapi import APIRouter, Depends, Query

from app.controllers.question_controller import (
    create_question_controller,
    get_questions_controller,
    get_question_by_id_controller,
    update_question_controller,
    delete_question_controller
)

from app.schemas.question_schema import (
    QuestionCreate,
    QuestionUpdate
)

from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


@router.post("")
async def create_question(
    payload: QuestionCreate,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await create_question_controller(
        payload=payload,
        current_user=current_user
    )


@router.get("")
async def get_questions(
    templateId: str = Query(
        default=None
    ),
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_questions_controller(
        templateId=templateId,
        current_user=current_user
    )


@router.get("/{question_id}")
async def get_question_by_id(
    question_id: str,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_question_by_id_controller(
        question_id=question_id
    )


@router.put("/{question_id}")
async def update_question(
    question_id: str,
    payload: QuestionUpdate,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await update_question_controller(
        question_id=question_id,
        payload=payload,
        current_user=current_user
    )


@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await delete_question_controller(
        question_id=question_id,
        current_user=current_user
    )
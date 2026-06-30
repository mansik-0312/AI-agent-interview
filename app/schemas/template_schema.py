from pydantic import BaseModel, Field
from typing import Optional


class InterviewTemplateCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)

    description: str | None = Field(
        default=None,
        max_length=500
    )

    totalQuestions: int = Field(
        ge=1,
        le=100
    )


class InterviewTemplateUpdate(BaseModel):
    name: Optional[str] = None

    description: Optional[str] = None

    totalQuestions: Optional[int] = None

    active: Optional[bool] = None


class InterviewTemplateResponse(BaseModel):
    id: str

    name: str

    description: Optional[str]

    totalQuestions: int

    active: bool
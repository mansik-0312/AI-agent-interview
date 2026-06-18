from pydantic import BaseModel, Field
from typing import Optional


class InterviewTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2)

    description: Optional[str] = None

    totalQuestions: int = Field(
        default=5,
        gt=0
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
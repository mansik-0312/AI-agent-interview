from pydantic import BaseModel, Field
from typing import Optional

from app.core.utils.core_enums import (
    QuestionDifficulty
)


class QuestionCreate(BaseModel):

    templateId: str

    questionText: str

    expectedAnswer: str

    duration: int = Field(
        default=120,
        gt=0
    )

    weight: int = Field(
        default=1,
        gt=0
    )

    difficulty: QuestionDifficulty


class QuestionUpdate(BaseModel):

    questionText: Optional[str] = None

    expectedAnswer: Optional[str] = None

    duration: Optional[int] = None

    weight: Optional[int] = None

    difficulty: Optional[
        QuestionDifficulty
    ] = None

    active: Optional[bool] = None


class QuestionResponse(BaseModel):

    id: str

    templateId: str

    questionText: str

    expectedAnswer: str

    duration: int

    weight: int

    difficulty: QuestionDifficulty

    active: bool

class CurrentQuestionResponse(BaseModel):

    questionId: str

    sequence: int

    questionText: str

    duration: int
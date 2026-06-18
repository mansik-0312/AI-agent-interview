from beanie import Document
from bson import ObjectId
from pydantic import ConfigDict

from app.core.utils.core_enums import (
    QuestionDifficulty,
)
from app.models.base_model import (
    AuditMixin,
    DeletedInfo,
)


class Question(
    Document,
    AuditMixin
):
    templateId: ObjectId

    questionText: str

    expectedAnswer: str

    duration: int = 120

    weight: int = 1

    difficulty: QuestionDifficulty

    active: bool = True

    deleted: DeletedInfo = DeletedInfo()

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "questions"

        indexes = [
            "templateId",
            "difficulty",
            "active"
        ]
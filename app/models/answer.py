from beanie import Document
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone
from pydantic import ConfigDict

from app.models.base_model import AuditMixin


class Answer(
    Document,
    AuditMixin
):
    interviewId: ObjectId

    questionId: ObjectId

    answerText: Optional[str] = None

    submittedAt: datetime = datetime.now(
        timezone.utc
    )

    score: Optional[float] = None

    feedback: Optional[str] = None

    aiProcessed: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "answers"

        indexes = [
            "interviewId",
            "questionId"
        ]
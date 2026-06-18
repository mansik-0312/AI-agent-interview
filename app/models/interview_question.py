from beanie import Document
from bson import ObjectId
from pydantic import ConfigDict
from datetime import datetime, timezone

from app.core.utils.core_enums import (
    InterviewQuestionStatus
)


class InterviewQuestion(Document):

    interviewId: ObjectId

    questionId: ObjectId

    sequence: int

    duration: int

    status: InterviewQuestionStatus = (
        InterviewQuestionStatus.PENDING
    )

    createdAt: datetime = datetime.now(
        timezone.utc
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "interview_questions"

        indexes = [
            "interviewId",
            "questionId"
        ]
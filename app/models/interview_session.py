from beanie import Document
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional
from pydantic import ConfigDict


class InterviewSession(Document):

    interviewId: ObjectId

    currentQuestionIndex: int

    remainingTime: int

    lastActiveAt: datetime = datetime.now(
        timezone.utc
    )

    browserDisconnected: bool = False

    resumeToken: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "interview_sessions"

        indexes = [
            "interviewId"
        ]
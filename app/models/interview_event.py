from beanie import Document
from bson import ObjectId
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import ConfigDict

from app.core.utils.core_enums import (
    InterviewEventType
)


class InterviewEvent(Document):

    interviewId: ObjectId

    eventType: InterviewEventType

    metadata: Optional[
        Dict[str, Any]
    ] = {}

    createdAt: datetime = datetime.now(
        timezone.utc
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "interview_events"

        indexes = [
            "interviewId",
            "eventType"
        ]
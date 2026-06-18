from beanie import Document
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone
from pydantic import ConfigDict

from app.core.utils.core_enums import (
    RecordingStatus
)


class Recording(Document):

    interviewId: ObjectId

    roomName: str

    videoPath: str

    audioPath: Optional[str] = None

    durationSeconds: Optional[int] = None

    processingStatus: RecordingStatus = (
        RecordingStatus.PENDING
    )

    createdAt: datetime = datetime.now(
        timezone.utc
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "recordings"

        indexes = [
            "interviewId"
        ]
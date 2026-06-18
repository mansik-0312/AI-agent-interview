from typing import Optional

from beanie import Document
from pydantic import ConfigDict

from app.models.base_model import (
    AuditMixin,
    DeletedInfo,
)


class InterviewTemplate(
    Document,
    AuditMixin
):
    name: str

    description: Optional[str] = None

    totalQuestions: int = 5

    active: bool = True

    deleted: DeletedInfo = DeletedInfo()

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "interview_templates"
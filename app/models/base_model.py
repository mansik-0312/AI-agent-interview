from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class DeletedInfo(BaseModel):
    status: bool = False
    at: Optional[int] = None
    by: Optional[ObjectId] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


class AuditMixin(BaseModel):
    createdBy: Optional[ObjectId] = None
    updatedBy: Optional[ObjectId] = None

    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
# app/models/job_requisition.py

from beanie import Document
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from bson import ObjectId


class DeletedInfo(BaseModel):
    status: bool
    at: Optional[datetime]
    by: Optional[ObjectId]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class JobRequisition(Document):
    designation: str
    departmentId: ObjectId
    jdId: Optional[ObjectId]
    jd_attached_by: Optional[ObjectId]
    jd_attached_at: Optional[datetime]
    urgency: str
    budget: str
    noOfResourses: int
    additionalInfo: Optional[str]
    status: str
    approved_by: Optional[ObjectId]
    approved_at: Optional[datetime]
    createdBy: ObjectId
    updatedBy: Optional[ObjectId] = None
    deleted: DeletedInfo
    updatedAt: datetime
    createdAt: datetime
    jdContent: Optional[str]
    assignedRecruiterId: Optional[ObjectId]
    dueDateDays: Literal[30, 45, 60] = Field(default=30)
    expiryDate: Optional[datetime] = Field(default=None)

    class Settings:
        name = "jobRequisition"

    model_config = ConfigDict(arbitrary_types_allowed=True)



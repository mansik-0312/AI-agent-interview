from beanie import Document
from bson import ObjectId
from datetime import datetime
from pydantic import Field
from pydantic import ConfigDict
from enum import Enum
from typing import Optional

class ApplicationStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    not_shortlisted = "not_shortlisted"
    scheduled = "scheduled"
    rejected = "rejected"
    hold = "hold"
    offer_sent = "offer sent"
    offer_save = "offer save"
    offer_accepted = "offer accepted"
    offer_rejected = "offer rejected"
           
class CandidateApplication(Document):
    candidateId: ObjectId
    jobRequisitionId: ObjectId
    resumePath: str
    status: ApplicationStatus = ApplicationStatus.applied
    feedback: Optional[str] = None
    shortlistedAt: Optional[datetime] = None
    shortlistedBy: Optional[ObjectId] = None
    appliedAt: datetime = Field(default_factory=datetime.utcnow)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    class Settings:
        name = "candidate_applications"

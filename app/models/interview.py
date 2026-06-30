from beanie import Document
from bson import ObjectId
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime

from app.core.utils.core_enums import InterviewStatus
from app.models.base_model import AuditMixin


class Interview(
    Document,
    AuditMixin
):
    candidateId: ObjectId

    candidateApplicationId: ObjectId

    jobRequisitionId: ObjectId

    templateId: ObjectId

    status: InterviewStatus = (
        InterviewStatus.SCHEDULED
    )

    currentQuestionIndex: int = 0

    startedAt: Optional[datetime] = None

    completedAt: Optional[datetime] = None

    roomName: str

    livekitRoomId: Optional[str] = None

    livekitToken: Optional[str] = None
    
    livekitEgressId: Optional[str] = None
    
    totalQuestions: int

    answeredQuestions: int = 0

    overallScore: Optional[float] = None

    technicalScore: Optional[float] = None

    integrityScore: Optional[float] = None

    transcriptReady: bool = False

    analysisReady: bool = False

    interviewToken: str

    interviewLink: str

    scheduledAt: datetime

    recordingUrl: Optional[str] = None

    recordingReady: bool = False


    candidateName: Optional[str] = None
    departmentId: Optional[str] = None
    jobRole: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "ai-agent-interviews"

        indexes = [
            "candidateId",
            "candidateApplicationId",
            "status"
        ]
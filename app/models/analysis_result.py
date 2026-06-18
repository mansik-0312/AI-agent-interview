from beanie import Document
from bson import ObjectId
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict

from app.core.utils.core_enums import (
    ReadingRisk
)

class QuestionWiseResult(BaseModel):

    questionId: str

    question: str

    candidateAnswer: str

    expectedAnswer: str

    score: float

    feedback: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

class AnalysisResult(Document):

    interviewId: ObjectId

    transcript: Optional[str] = None

    technicalScore: Optional[float] = None

    integrityScore: Optional[float] = None

    recruiterSummary: Optional[str] = None

    questionWiseResult: List[
        QuestionWiseResult
    ] = []

    emotionMetrics: Dict[str, Any] = {}

    suspicionMetrics: Dict[str, Any] = {}

    readingRisk: ReadingRisk = (
        ReadingRisk.LOW
    )

    recordingUrl: Optional[str] = None
    
    createdAt: datetime = datetime.now(
        timezone.utc
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "analysis_results"

        indexes = [
            "interviewId"
        ]
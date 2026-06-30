from datetime import date, time

from pydantic import BaseModel
from typing import Optional


class InterviewCreateRequest(BaseModel):

    candidateApplicationId: str

    templateId: str

    scheduledDate: date

    scheduledTime: time

    interviewDuration: int = 60

    candidateName: str
    departmentId: str
    jobRole: str
    experience: Optional[str] = None
    email: str
    phone: str

class InterviewCreateResponse(BaseModel):

    interviewId: str

    interviewLink: str

    roomName: str

    status: str

class InterviewStateResponse(BaseModel):

    interviewId: str

    status: str

    currentQuestionIndex: int

    totalQuestions: int

    answeredQuestions: int

    remainingTime: int

class InterviewCompleteResponse(BaseModel):

    interviewId: str

    status: str

class SubmitAnswerRequest(
    BaseModel
):
    questionId: str
    
    answerText: str
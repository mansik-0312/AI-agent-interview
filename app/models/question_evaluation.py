from pydantic import BaseModel


class QuestionEvaluationRequest(BaseModel):
    interview_id: str

    question: str

    expected_answer: str

    candidate_answer: str

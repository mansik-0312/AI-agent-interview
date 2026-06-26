from pydantic import BaseModel

class InterviewRequest(BaseModel):
    candidate_name: str
    recordingUrl: str
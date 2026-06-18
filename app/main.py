from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from beanie import init_beanie

from app.database import db
from app.models.interview_template import InterviewTemplate
from app.models.question import Question
from app.models.interview import Interview
from app.models.candidate_application import CandidateApplication
from app.models.candidate import Candidate
from app.models.job_requisition import JobRequisition
from app.models.interview_question import InterviewQuestion
from app.models.answer import Answer
from app.models.analysis_result import AnalysisResult

from app.routes.template_routes import router as template_router
from app.routes.question_routes import router as question_router
from app.routes.interview_routes import router as interview_router

load_dotenv()

from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_beanie(
        database=db,
        document_models=[
            InterviewTemplate,
            Question,
            Interview,
            CandidateApplication,
            Candidate,
            JobRequisition,
            InterviewQuestion,
            Answer,
            AnalysisResult
        ]
    )

    yield

app = FastAPI(lifespan=lifespan)

app.mount("/recordings", StaticFiles(directory="livekit-local/recordings"), name="recordings")

app.include_router(
    template_router,
    prefix="/api"
)
app.include_router(
    question_router,
    prefix="/api"
)
app.include_router(
    interview_router,
    prefix="/api"
)
@app.get("/")
async def health():
    return {"message": "AI Interview Service Running"}
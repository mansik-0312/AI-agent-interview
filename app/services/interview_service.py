from bson import ObjectId
from uuid import uuid4
import random
from datetime import datetime, timezone
import os
import subprocess
from fastapi import HTTPException
from dotenv import load_dotenv
from app.models.interview import Interview
from app.models.interview_question import InterviewQuestion
from app.models.interview_template import InterviewTemplate
from app.models.job_requisition import JobRequisition
from app.models.question import Question
from app.models.candidate_application import CandidateApplication
from app.models.candidate import Candidate
from app.models.answer import Answer
from app.models.analysis_result import AnalysisResult
from fastapi.encoders import jsonable_encoder

from app.core.utils.response_mixin import (
    CustomResponseMixin
)

from app.core.utils.core_enums import (
    InterviewStatus
)

from app.core.utils.email_service import (
    render_template,
    notify_via_email
)

from app.core.utils.livekit import (
    create_livekit_session
)

from app.core.utils.livekit_recording import (
    start_recording,
    stop_recording
)

from ..database import (
    candidate_applications_collection  ,
    interview_templates_collection ,
    department_collection
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
response = CustomResponseMixin()

async def create_interview_service(
    payload,
    current_user
):
    
    candidate_application = await (
    CandidateApplication.get(
        ObjectId(
            payload.candidateApplicationId
        )
    )
)

    if not candidate_application:
        response.raise_exception(
            "Candidate application not found"
        )

    candidate = await Candidate.get(
        candidate_application.candidateId
    )

    if not candidate:
        response.raise_exception(
            "Candidate not found"
        )

    job_requisition = await JobRequisition.get(
        candidate_application.jobRequisitionId
    )

    if not job_requisition:
        response.raise_exception(
            "Job requisition not found"
        )
        
    template = await InterviewTemplate.get(
        ObjectId(payload.templateId)
    )

    if not template:
        response.raise_exception(
            "Template not found"
        )

    if not template.active:
        response.raise_exception(
            "Template is inactive"
        )

    existing_interview = await (
        Interview.find_one(
            {
                "candidateApplicationId":
                    candidate_application.id,
                "status": {
                    "$in": [
                        InterviewStatus.SCHEDULED,
                        InterviewStatus.IN_PROGRESS
                    ]
                }
            }
        )
    )

    if existing_interview:
        response.raise_exception(
            "Interview already scheduled"
        )

    questions = await Question.find(
        {
            "templateId": template.id,
            "active": True,
            "deleted.status": False
        }
    ).to_list()

    if len(questions) < template.totalQuestions:

        response.raise_exception(
            f"Template requires "
            f"{template.totalQuestions} "
            f"questions but only "
            f"{len(questions)} active "
            f"questions found"
        )

    selected_questions = random.sample(
        questions,
        template.totalQuestions
    )

    interview_token = uuid4().hex

    room_name = f"interview_{interview_token}"

    try:
        livekit_response = await create_livekit_session(
            room_name=room_name,
            candidate_name=candidate.name
        )
    except Exception as e:
        response.raise_exception(
            f"Failed to create LiveKit room: {str(e)}"
        )

    scheduled_at = datetime.combine(
        payload.scheduledDate,
        payload.scheduledTime
    )
    interview_link = (
        f"http://localhost:8011/api/interviews/join/"
        f"{interview_token}"
    )
    interview = Interview(
        candidateId=candidate_application.candidateId,
        candidateApplicationId=candidate_application.id,
        jobRequisitionId=candidate_application.jobRequisitionId,
        templateId=template.id,

        candidateName=payload.candidateName,
        departmentId=payload.departmentId,
        jobRole=payload.jobRole,
        experience=payload.experience,
        email=payload.email,
        phone=payload.phone,
        status=InterviewStatus.SCHEDULED,
        totalQuestions=template.totalQuestions,
        interviewToken=interview_token,
        interviewLink=interview_link,
        roomName=room_name,
        livekitRoomId=livekit_response["room_id"],
        livekitToken=livekit_response["token"],
        scheduledAt=scheduled_at,
        createdBy=ObjectId(
                current_user["userId"]
            )
    )
    await interview.insert()

    formatted_schedule = (
        scheduled_at.strftime(
            "%d-%b-%Y %I:%M %p"
        )
    )
    email_body = render_template(
        "candidate_invite.html",
        {
            "candidate_name": candidate.name,
            "job_role":
                job_requisition.designation,
            "scheduled_time":
                formatted_schedule,
            "interview_link":
                interview_link
        }
    )

    await notify_via_email(
        to_emails=[candidate.email],
        subject="AI Interview Invitation",
        body=email_body
    )

    for index, question in enumerate(
        selected_questions
    ):

        interview_question = (
            InterviewQuestion(
                interviewId=interview.id,
                questionId=question.id,
                sequence=index + 1,
                duration=question.duration
            )
        )

        await interview_question.insert()

    return {
        "interviewId":str(interview.id),
        "interviewLink":interview.interviewLink,
        "roomName":interview.roomName,
        "status":interview.status
    }

async def get_interview_question_by_sequence(
    interview_id: ObjectId,
    sequence: int
):

    return await InterviewQuestion.find_one(
        {
            "interviewId": interview_id,
            "sequence": sequence
        }
    )

async def get_current_question_service(
    interview_id: str
):

    interview = await Interview.get(
        ObjectId(interview_id)
    )

    if not interview:
        response.raise_exception(
            "Interview not found"
        )

    current_sequence = (
        interview.currentQuestionIndex + 1
    )

    interview_question = await (
        get_interview_question_by_sequence(
            interview.id,
            current_sequence
        )
    )

    if not interview_question:

        return {
            "completed": True,
            "message":
                "Interview completed"
        }

    question = await Question.get(
        interview_question.questionId
    )

    if not question:
        response.raise_exception(
            "Question not found"
        )

    return {
        "questionId":
            str(question.id),

        "questionText":
            question.questionText,

        "duration":
            interview_question.duration,

        "sequence":
            interview_question.sequence,

        "totalQuestions":
            interview.totalQuestions,

        "completed":
            False
    }


async def next_question_service(
    interview_id: str
):

    interview = await Interview.get(
        ObjectId(interview_id)
    )

    if not interview:
        response.raise_exception(
            "Interview not found"
        )

    interview.currentQuestionIndex += 1

    await interview.save()

    current_sequence = (
        interview.currentQuestionIndex + 1
    )

    interview_question = await (
        get_interview_question_by_sequence(
            interview.id,
            current_sequence
        )
    )

    if not interview_question:

        return {
            "completed": True
        }

    question = await Question.get(
        interview_question.questionId
    )

    if not question:
        response.raise_exception(
            "Question not found"
        )

    return {
        "questionId": str(question.id),
        "questionText": question.questionText,
        "duration": interview_question.duration,
        "sequence": interview_question.sequence,
        "totalQuestions": interview.totalQuestions,
        "completed": False
    }

async def submit_answer_service(
    interview_id: str,
    payload
):

    interview = await Interview.get(
        ObjectId(interview_id)
    )

    if not interview:
        response.raise_exception(
            "Interview not found"
        )

    existing_answer = await (
        Answer.find_one(
            {
                "interviewId": interview.id,
                "questionId": ObjectId(
                    payload.questionId
                )
            }
        )
    )

    if existing_answer:

        existing_answer.answerText = (
            payload.answerText
        )

        existing_answer.submittedAt = (
            datetime.now(
                timezone.utc
            )
        )

        await existing_answer.save()

        return {
            "answerId":
                str(existing_answer.id)
        }

    answer = Answer(
        interviewId=interview.id,
        questionId=ObjectId(
            payload.questionId
        ),
        answerText=payload.answerText
    )

    await answer.insert()

    return {
        "answerId": str(answer.id)
    }

async def start_interview_service(
    interview_id: str
):

    interview = await Interview.get(
        ObjectId(interview_id)
    )

    if not interview:
        response.raise_exception(
            "Interview not found"
        )

    if interview.status == (
        InterviewStatus.IN_PROGRESS
    ):
        return {
            "interviewId":
                str(interview.id)
        }

    recording = await start_recording(
        interview.roomName
    )

    interview.status = (
        InterviewStatus.IN_PROGRESS
    )

    interview.startedAt = (
        datetime.now(timezone.utc)
    )

    interview.livekitEgressId = (
        recording["egressId"]
    )

    await interview.save()

    return {
        "interviewId":
            str(interview.id),

        "status":
            interview.status
    }

async def complete_interview_service(interview_id: str):
    interview = await Interview.get(ObjectId(interview_id))

    if not interview:
        response.raise_exception("Interview not found")

    if interview.livekitEgressId:
        try:
            full_path = await stop_recording(interview.livekitEgressId)
            
            if full_path:
                filename = os.path.basename(full_path)
                interview.recordingUrl = f"/recordings/{filename}"
                interview.recordingReady = True
                print(f"[INFO] Recording saved: {filename}")
            else:
                print("[WARNING] No recording path returned")
                interview.recordingReady = False

        except Exception as e:
            print(f"[WARNING] Recording issue: {e}")
            interview.recordingReady = False

    interview.status = InterviewStatus.COMPLETED
    interview.completedAt = datetime.now(timezone.utc)
    await interview.save()

    return {
        "interviewId": str(interview.id),
        "status": interview.status
    }

# async def build_interview_details(
#     interview: Interview
# ):

#     analysis = await AnalysisResult.find_one(
#         {
#             "interviewId": interview.id
#         }
#     )

#     candidate = await Candidate.get(
#         interview.candidateId
#     )

#     return {
#         "interviewId": str(interview.id),
#         "candidateName": candidate.name,
#         "status": interview.status,
#         "technicalScore": interview.technicalScore,
#         "analysis": jsonable_encoder(analysis) if analysis else None
#     }

def get_technical_status(score: float | None):
    """
    Return status based on technical score (Out of 5)
    """

    if score is None:
        return "Not Evaluated"

    if score >= 4:
        return "Excellent"

    if score >= 3:
        return "Good"

    if score >= 2:
        return "Average"

    return "Poor"


def get_integrity_status(score: float | None):
    """
    Return integrity status based on percentage.
    Database stores score out of 10.
    """

    if score is None:
        return "Unknown"

    percentage = score * 10

    if percentage >= 90:
        return "High"

    if percentage >= 70:
        return "Medium"

    return "Low"


async def build_interview_details(
    interview: Interview
):

    analysis = await AnalysisResult.find_one(
        {
            "interviewId": interview.id
        }
    )

    candidate = await Candidate.get(
        interview.candidateId
    )

    template = None

    if interview.templateId:
        template = await InterviewTemplate.get(
            interview.templateId
        )

    technical_score = interview.technicalScore or 0
    integrity_percentage = (interview.integrityScore or 0) * 10

    return {

        "interviewId": str(interview.id),

        "candidateName": candidate.name,

        "status": interview.status,

        "date": (
            interview.completedAt.isoformat()
            if interview.completedAt
            else None
        ),

        # -----------------------------
        # Static (For Now)
        # -----------------------------
        "duration": {
            "time": "56m 32s",
            "startTime": "10:00 AM",
            "endTime": "10:56 AM"
        },

        # -----------------------------
        # Questions
        # -----------------------------
        "questions": {
            "total": interview.totalQuestions,
            "answered": interview.answeredQuestions,
            "completionPercentage": (
                round(
                    (interview.answeredQuestions / interview.totalQuestions) * 100
                )
                if interview.totalQuestions
                else 0
            )
        },

        # -----------------------------
        # Technical Score
        # -----------------------------
        "technicalScore": {
            "score": technical_score,
            "outOf": 5,
            "status": get_technical_status(
                technical_score
            )
        },

        # -----------------------------
        # Integrity Score
        # -----------------------------
        "integrityScore": {
            "score": integrity_percentage,
            "status": get_integrity_status(
                interview.integrityScore
            )
        },

        # -----------------------------
        # Interview Template
        # -----------------------------
        "interviewTemplate": {
            "id": str(template.id) if template else None,
            "name": template.name if template else None,
            "description": template.description if template else None,
            "totalQuestions": (
                template.totalQuestions
                if template
                else interview.totalQuestions
            )
        },

        # -----------------------------
        # Analysis
        # -----------------------------
        "analysis": (
            jsonable_encoder(analysis)
            if analysis
            else None
        )
    }

async def get_interviews_service(
    page: int = 1,
    limit: int = 10
):
 
    skip = (page - 1) * limit
 
    total = await Interview.find().count()
 
    interviews = await Interview.find() \
        .skip(skip) \
        .limit(limit) \
        .to_list()
 
    result = []

    for interview in interviews:

        result.append(
            await build_interview_details(
                interview
            )
        )
 
    return result, total

async def get_interview_by_id_service(
    interview_id: str
):

    interview = await Interview.get(
        ObjectId(interview_id)
    )

    if not interview:
        response.raise_exception(
            "Interview not found"
        )

    return await build_interview_details(
        interview
    )

async def get_shortlisted_candidates_service():
    pipeline = [
        {
            "$match": {
                "status": "shortlisted"
            }
        },
        {
            "$lookup": {
                "from": "candidates",
                "localField": "candidateId",
                "foreignField": "_id",
                "as": "candidate"
            }
        },
        {
            "$unwind": "$candidate"
        },
        {
            "$match": {
                "candidate.deleted.status": False
            }
        },
        {
            "$project": {
                "_id": 0,
                "applicationId": {
                    "$toString": "$_id"
                },
                "candidateId": {
                    "$toString": "$candidate._id"
                },
                "name": "$candidate.name",
                "email": "$candidate.email",
                "mobile": {
                    "$toString": "$candidate.mobile"
                },
                "role": "$candidate.role",
                "resumePath": "$resumePath",
                "status": "$status"
            }
        },
        {
            "$sort": {
                "name": 1
            }
        }
    ]

    return await candidate_applications_collection.aggregate(
        pipeline
    ).to_list(length=None)

async def get_interview_templates_service():

    pipeline = [
        {
            "$match": {
                "active": True,
                "deleted.status": False
            }
        },
        {
            "$project": {
                "_id": 0,
                "templateId": {
                    "$toString": "$_id"
                },
                "name": 1,
                "description": 1,
                "totalQuestions": 1
            }
        },
        {
            "$sort": {
                "name": 1
            }
        }
    ]

    templates = await interview_templates_collection.aggregate(
        pipeline
    ).to_list(length=None)

    return templates

async def get_departments_service():
    try:
        cursor = department_collection.find(
            {
                "deleted.status": False
            },
            {
                "_id": 1,
                "name": 1
            }
        ).sort("name", 1)

        departments = []

        async for department in cursor:
            departments.append(
                {
                    "id": str(department["_id"]),
                    "name": department["name"]
                }
            )

        return {
            "message": "Departments fetched successfully.",
            "data": departments
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch departments: {str(e)}"
        )


from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates

import json

from app.auth.dependencies import (
    get_current_user
)

from app.controllers.interview_controller import (
    create_interview_controller,
    get_current_question_controller,
    next_question_controller,
    submit_answer_controller,
    complete_interview_controller,
    get_interviews_controller,
    get_interview_by_id_controller,
    analyze_interview_controller,
    start_interview_controller,
    get_shortlisted_candidates_controller,
    get_interview_templates_controller
)
from app.core.utils import templates

from app.core.utils.livekit_recording import list_egress, list_rooms, start_recording

from app.schemas.interview_schema import (
    InterviewCreateRequest,
    SubmitAnswerRequest
)
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.models.interview import Interview
from app.models.candidate import Candidate
import os
from fastapi import BackgroundTasks


from app.core.utils.response_mixin import (
    CustomResponseMixin
)
from app.services.analysis import analyze_interview_service

import websockets
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import os

response = CustomResponseMixin()

templates = Jinja2Templates(
    directory="app/core/utils/templates"
)
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


@router.post("")
async def create_interview(
    payload: InterviewCreateRequest,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await create_interview_controller(
        payload=payload,
        current_user=current_user
    )


@router.get(
    "/join/{interview_token}",
    response_class=HTMLResponse
)
async def join_interview(
    request: Request,
    interview_token: str
):

    interview = await Interview.find_one(
        Interview.interviewToken == interview_token
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    candidate = await Candidate.get(
        interview.candidateId
    )

    return templates.TemplateResponse(
        request=request,
        name="interview.html",
        context={
            "interview_id": str(interview.id),
            "candidate_name": candidate.name,
            "room_name": interview.roomName,
            "token": interview.livekitToken,
            "livekit_url": LIVEKIT_URL,
        }
    )

@router.get("/test-egress-payload/{interview_id}")
async def debug_payload(interview_id: str):
    interview = await Interview.get(ObjectId(interview_id))
    room_name = interview.roomName
    return {
        "room_name": room_name,
        "layout": "speaker",
        "file": {"file_type": 1, "filepath": f"recordings/{room_name}.mp4"},
        "file_outputs": [{"file_type": 1, "filepath": f"recordings/{room_name}.mp4"}],
    }

@router.post(
    "/test-egress/{interview_id}"
)
async def test_egress(
    interview_id: str
):

    interview = await Interview.get(
        ObjectId(interview_id)
    )

    print(
        "Room Name:",
        interview.roomName
    )

    await list_egress()
    
    await list_rooms()
    
    result = await start_recording(
        interview.roomName
    )

    return result

@router.get(
    "/{interview_id}/current-question"
)
async def get_current_question(
    interview_id: str
):
    return await get_current_question_controller(
        interview_id
    )

@router.post(
    "/{interview_id}/next-question"
)
async def next_question(
    interview_id: str
):
    return await next_question_controller(
        interview_id
    )

@router.post(
    "/{interview_id}/answers"
)
async def submit_answer(
    interview_id: str,
    payload: SubmitAnswerRequest
):
    return await submit_answer_controller(
        interview_id,
        payload
    )

@router.post(
    "/{interview_id}/start"
)
async def start_interview(
    interview_id: str
):
    return await start_interview_controller(
        interview_id
    )

@router.post("/{interview_id}/start-recording")
async def start_interview_recording(interview_id: str):
    interview = await Interview.get(ObjectId(interview_id))

    if not interview:
        return response.raise_exception("Interview not found")

    if interview.livekitEgressId:
        return response.success_message(
            message="Recording already started",
            data={"egressId": interview.livekitEgressId}
        )

    result = await start_recording(interview.roomName)
    egress_id = result["egressId"]

    interview.livekitEgressId = egress_id
    await interview.save()

    return response.success_message(
        message="Recording started",
        data={"egressId": egress_id}
    )

@router.post(
    "/{interview_id}/complete"
)
async def complete_interview(
    interview_id: str,
    background_tasks: BackgroundTasks
):
    result = await complete_interview_controller(interview_id)
    
    # Trigger analysis in background — doesn't block the response
    background_tasks.add_task(analyze_interview_service, interview_id)
    
    return result


@router.get("")
async def get_interviews(
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_interviews_controller(page, limit)

@router.get("/candidates/shortlisted")
async def get_shortlisted_candidates(
    current_user: dict = Depends(get_current_user)
):
    return await get_shortlisted_candidates_controller()

@router.get("/templates")
async def get_interview_templates(
    current_user: dict = Depends(get_current_user)
):
    return await get_interview_templates_controller()


@router.get("/{interview_id}")
async def get_interview_by_id(
    interview_id: str,
    current_user: dict = Depends(
        get_current_user
    )
):
    return await get_interview_by_id_controller(
        interview_id
    )

@router.post(
    "/{interview_id}/analyze"
)
async def analyze_interview(
    interview_id: str
):
    return await analyze_interview_controller(
        interview_id
    )

@router.websocket("/ws/deepgram")
async def deepgram_proxy(
    websocket: WebSocket
):
    await websocket.accept()

    dg_url = (
        "wss://api.deepgram.com/v1/listen"
        "?model=nova-2"
        "&language=en"
        "&encoding=opus"
        "&container=webm"
        "&interim_results=true"
        "&punctuate=true"
        "&smart_format=true"
    )

    try:

        async with websockets.connect(
            dg_url,
            additional_headers={
                "Authorization":
                f"Token {os.getenv('DEEPGRAM_API_KEY')}"
            }
        ) as dg:

            async def browser_to_dg():

                while True:

                    data = await websocket.receive_bytes()

                    print(
                        "AUDIO BYTES:",
                        len(data)
                    )

                    await dg.send(data)

            async def dg_to_browser():

                async for msg in dg:

                    print(
                        "DG:",
                        msg[:200]
                    )

                    await websocket.send_text(
                        msg
                    )

            await asyncio.gather(
                browser_to_dg(),
                dg_to_browser()
            )

    except Exception as e:

        print(
            "DEEPGRAM ERROR:",
            str(e)
        )

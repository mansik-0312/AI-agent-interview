from pathlib import Path
from bson import ObjectId
from moviepy import VideoFileClip

from ..database import (
    interview_transcripts_collection,
    interview_analysis_collection,
)

from app.services.video_analyzer import analyze_video

from app.services.audio_analyzer import (
    extract_audio,
    transcribe_audio,
    calculate_speaking_speed,
    count_fillers,
)

from app.services.evaluation_engine import (
    evaluate_answer,
)

from app.services.yolo_analyzer import (
    detect_multiple_persons,
    detect_suspicious_objects,
)

# Project root (AI-agent-interview)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def analyze_complete_interview(
    interview_id: str,
):
    # -----------------------------
    # Fetch interview
    # -----------------------------
    interview = await interview_transcripts_collection.find_one(
        {
            "interviewId": ObjectId(interview_id)
        }
    )

    if not interview:
        return {
            "message": "Interview not found"
        }

    # -----------------------------
    # Build absolute video path
    # -----------------------------
    recording_url = interview["recordingUrl"]

    video_path = str(
        BASE_DIR
        / "livekit-local"
        / recording_url.lstrip("/\\")
    )

    if not Path(video_path).exists():
        return {
            "message": "Recording file not found",
            "path": video_path,
        }

    candidate_name = interview.get(
        "candidate_name",
        "Unknown Candidate",
    )

    # -----------------------------
    # Video analysis
    # -----------------------------
    video_metrics = analyze_video(
        video_path
    )

    person_metrics = detect_multiple_persons(
        video_path
    )

    object_metrics = detect_suspicious_objects(
        video_path
    )

    # -----------------------------
    # Audio analysis
    # -----------------------------
    audio_path = extract_audio(
        video_path
    )

    transcript = transcribe_audio(
        audio_path
    )

    duration = VideoFileClip(
        video_path
    ).duration

    speaking_speed = calculate_speaking_speed(
        transcript,
        duration,
    )

    filler_words = count_fillers(
        transcript
    )

    # -----------------------------
    # Question evaluation
    # -----------------------------
    evaluated_questions = []

    technical_total = 0
    communication_total = 0
    overall_total = 0

    for item in interview.get(
        "questionWiseResult",
        [],
    ):

        evaluation = evaluate_answer(
            item.get("question", ""),
            item.get("expectedAnswer", ""),
            item.get("candidateAnswer", ""),
        )

        technical_total += evaluation.get(
            "technical_score",
            0,
        )

        communication_total += evaluation.get(
            "communication_score",
            0,
        )

        overall_total += evaluation.get(
            "overall_score",
            0,
        )

        evaluated_questions.append(
            {
                **item,
                **evaluation,
            }
        )

    total_questions = len(
        evaluated_questions
    )

    if total_questions > 0:
        technical_score = round(
            technical_total / total_questions,
            2,
        )

        communication_score = round(
            communication_total / total_questions,
            2,
        )

        overall_score = round(
            overall_total / total_questions,
            2,
        )
    else:
        technical_score = 0
        communication_score = 0
        overall_score = 0

    # -----------------------------
    # Save analysis
    # -----------------------------
    result_document = {
        "interview_id": interview_id,

        "candidate_id": interview.get(
            "candidate_id"
        ),

        "candidate_name": candidate_name,

        "video_metrics": {
            **video_metrics,
            **person_metrics,
            **object_metrics,
            "speaking_speed": speaking_speed,
            "filler_words": filler_words,
        },

        "technical_score": technical_score,

        "communication_score": communication_score,

        "overall_score": overall_score,

        "question_analysis": evaluated_questions,
    }

    result = await interview_analysis_collection.insert_one(
        result_document
    )

    result_document["_id"] = str(
        result.inserted_id
    )

    return result_document

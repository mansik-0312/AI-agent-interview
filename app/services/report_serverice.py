from fastapi import HTTPException
from bson import ObjectId

from ..database import interview_analysis_collection , interview_transcripts_collection


async def get_interview_report_service(interview_id: str):
    try:
        # Fetch interview analysis
        report = await interview_analysis_collection.find_one(
            {"interview_id": interview_id},
            {"_id": 0}
        )

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Interview report not found."
            )

        # Fetch recording URL from analysis_results
        transcript = None

        if ObjectId.is_valid(interview_id):
            transcript = await interview_transcripts_collection.find_one(
                {"interviewId": ObjectId(interview_id)},
                {
                    "_id": 0,
                    "recordingUrl": 1
                }
            )

        # Add recording URL to response
        report["recordingUrl"] = (
            transcript.get("recordingUrl")
            if transcript
            else None
        )

        return {
            "message": "Interview report fetched successfully.",
            "data": report
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch interview report: {str(e)}"
        )
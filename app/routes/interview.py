from fastapi import APIRouter


from app.services.interview_analysis import analyze_complete_interview


router = APIRouter()



@router.post(
    "/analyze/{interview_id}"
)
async def analyze_interview_route(
    interview_id: str
):
    return await analyze_complete_interview(
        interview_id
    )

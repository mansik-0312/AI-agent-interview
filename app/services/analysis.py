from app.models.answer import Answer
from app.models.question import Question
from app.models.interview import Interview
from app.models.analysis_result import AnalysisResult
from app.services.openai_prompt_service import build_interview_analysis_prompt
from app.core.utils.response_mixin import CustomResponseMixin
from app.services.openai_service import analyze_interview_with_ai
from app.core.utils.core_enums import InterviewStatus
from bson import ObjectId
from app.models.analysis_result import (
    QuestionWiseResult
)

response = CustomResponseMixin()



async def build_analysis_input(
    interview_id: ObjectId
):

    answers = await Answer.find(
        {
            "interviewId": interview_id
        }
    ).to_list()

    result = []

    for answer in answers:

        question = await Question.get(
            answer.questionId
        )

        if not question:
            continue

        result.append(
            {
                "questionId":
                    str(question.id),

                "question":
                    question.questionText,

                "candidateAnswer":
                    answer.answerText or ""
            }
        )

    return result

async def analyze_interview_service(interview_id: str):
    interview = await Interview.get(ObjectId(interview_id))

    if not interview:
        response.raise_exception("Interview not found")

    # ← Check status FIRST
    if interview.status != InterviewStatus.COMPLETED:
        response.raise_exception(
            "Interview must be completed before analysis"
        )

    # ← Then check if already analyzed
    existing_analysis = await AnalysisResult.find_one(
        {"interviewId": interview.id}
    )
    if existing_analysis:
        return {
            "analysisId": str(existing_analysis.id),
            "alreadyAnalyzed": True
        }

    qa_data = await build_analysis_input(interview.id)

    if not qa_data:
        response.raise_exception("No answers found for interview")

    question_map = {
        item["question"]: item["questionId"]
        for item in qa_data
    }

    prompt = build_interview_analysis_prompt(qa_data)

    try:
        ai_result = await analyze_interview_with_ai(prompt)
    except Exception as e:
        response.raise_exception(f"AI analysis failed: {str(e)}")

    question_results = []
    for item in ai_result["questionWiseResult"]:
        question_results.append(
            QuestionWiseResult(
                questionId=question_map.get(item["question"]),
                question=item["question"],
                candidateAnswer=item["candidateAnswer"],
                expectedAnswer=item["expectedAnswer"],
                score=item["score"],
                feedback=item["feedback"]
            )
        )

    analysis = AnalysisResult(
        interviewId=interview.id,
        technicalScore=ai_result["technicalScore"],
        integrityScore=ai_result["integrityScore"],
        recruiterSummary=ai_result["recruiterSummary"],
        questionWiseResult=question_results,
        recordingUrl=interview.recordingUrl  # ← picks up the URL saved above
    )

    await analysis.insert()

    interview.analysisReady = True
    interview.technicalScore = ai_result["technicalScore"]
    interview.integrityScore = ai_result["integrityScore"]
    await interview.save()

    print(f"[INFO] Analysis complete for {interview_id}")

    return {
        "analysisId": str(analysis.id),
        "technicalScore": analysis.technicalScore,
        "integrityScore": analysis.integrityScore,
        "analysisReady": True
    }
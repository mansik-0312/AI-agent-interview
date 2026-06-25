from bson import ObjectId
from database import interview_transcripts_collection  ,interview_analysis_collection
from app.services.evaluation_engine import (
    evaluate_answer
)


async def evaluate_interview(
    interview_id: str
):

    interview = await (
        interview_transcripts_collection
        .find_one(
            {
                "interviewId": ObjectId(interview_id)
            }
        )
    )

    if not interview:

        return {
            "message":
            "Interview not found"
        }

    transcripts = (
        interview["transcripts"]
    )

    evaluated_questions = []

    technical_total = 0
    communication_total = 0
    overall_total = 0

    for item in transcripts:

        evaluation = (
            evaluate_answer(
                item["question"],
                item["expected_answer"],
                item["candidate_answer"]
            )
        )

        technical_total += (
            evaluation[
                "technical_score"
            ]
        )

        communication_total += (
            evaluation[
                "communication_score"
            ]
        )

        overall_total += (
            evaluation[
                "overall_score"
            ]
        )

        evaluated_questions.append(
            {
                "question":
                    item["question"],

                "candidate_answer":
                    item[
                        "candidate_answer"
                    ],

                "expected_answer":
                    item[
                        "expected_answer"
                    ],

                **evaluation
            }
        )
    total_questions = len(
        evaluated_questions
    )

    result_document = {

        "interview_id":
            interview_id,

        "candidate_id":
            interview[
                "candidate_id"
            ],

        "candidate_name":
            interview[
                "candidate_name"
            ],

        "technical_score":
            round(
                technical_total /
                total_questions,
                2
            ),

        "communication_score":
            round(
                communication_total /
                total_questions,
                2
            ),

        "overall_score":
            round(
                overall_total /
                total_questions,
                2
            ),

        "questions":
            evaluated_questions
    }

    inserted = await (
        interview_analysis_collection
        .insert_one(
            result_document
        )
    )

    result_document["_id"] = str(
        inserted.inserted_id
    )

    return result_document

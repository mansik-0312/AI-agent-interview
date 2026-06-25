import json
import re

import ollama

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL = "llama3.2"

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def semantic_similarity_score(
    expected_answer: str,
    candidate_answer: str
) -> float:

    expected_embedding = embedding_model.encode(
        expected_answer
    )

    candidate_embedding = embedding_model.encode(
        candidate_answer
    )

    similarity = cosine_similarity(
        [expected_embedding],
        [candidate_embedding]
    )[0][0]

    return round(
        float(similarity) * 10,
        2
    )


def parse_llm_response(
    content: str
) -> dict:

    try:
        return json.loads(content)

    except Exception:

        try:

            match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL
            )

            if match:
                return json.loads(
                    match.group()
                )

        except Exception:
            pass

    return {}

def calculate_technical_score(
    semantic_score: float
):

    similarity = semantic_score / 10

    if similarity >= 0.90:
        return 5

    elif similarity >= 0.80:
        return 4

    elif similarity >= 0.70:
        return 3

    elif similarity >= 0.60:
        return 2

    elif similarity >= 0.50:
        return 1

    return 0

# def normalize_scores(
#     llm_result: dict
# ) -> dict:

#     technical_score = (
#         llm_result.get("technical_score")
#         or llm_result.get("technical_accuracy")
#         or llm_result.get("technical_rating")
#         or llm_result.get("tech_score")
#         or 0
#     )

#     coverage_score = (
#         llm_result.get("coverage_score", 0)
#     )

#     communication_score = (
#         llm_result.get(
#             "communication_score",
#             0
#         )
#     )

#     depth_score = (
#         llm_result.get(
#             "depth_score",
#             0
#         )
#     )

#     feedback = (
#         llm_result.get(
#             "feedback",
#             ""
#         )
#     )

#     return {
#         "technical_score":
#             float(technical_score),

#         "coverage_score":
#             float(coverage_score),

#         "communication_score":
#             float(communication_score),

#         "depth_score":
#             float(depth_score),

#         "feedback":
#             feedback
#     }

def normalize_scores(
    llm_result: dict
) -> dict:

    return {

        "coverage_score":
            float(
                llm_result.get(
                    "coverage_score",
                    0
                )
            ),

        "communication_score":
            float(
                llm_result.get(
                    "communication_score",
                    0
                )
            ),

        "depth_score":
            float(
                llm_result.get(
                    "depth_score",
                    0
                )
            ),

        "feedback":
            llm_result.get(
                "feedback",
                ""
            )
    }

# def evaluate_answer(
#     question: str,
#     expected_answer: str,
#     candidate_answer: str
# ):

#     prompt = f"""
# You are a Senior Technical Interviewer.

# IMPORTANT:
# Return ONLY valid JSON.

# Use EXACT keys:

# {{
#   "technical_score": 0,
#   "coverage_score": 0,
#   "communication_score": 0,
#   "depth_score": 0,
#   "feedback": ""
# }}

# Question:
# {question}

# Expected Answer:
# {expected_answer}

# Candidate Answer:
# {candidate_answer}
# """

#     response = ollama.chat(
#         model=MODEL,
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
#     )

#     content = response[
#         "message"
#     ]["content"]


#     llm_result = parse_llm_response(
#         content
#     )

#     llm_result = normalize_scores(
#         llm_result
#     )

#     semantic_score = (
#         semantic_similarity_score(
#             expected_answer,
#             candidate_answer
#         )
#     )

#     technical_score = calculate_technical_score(
#         semantic_score
#     )

#     llm_result[
#         "semantic_score"
#     ] = semantic_score

#     llm_result[
#         "technical_score"
#     ] = technical_score
    
#     overall_score = round(
#         (
#             llm_result[
#                 "technical_score"
#             ] * 0.4
#             +
#             llm_result[
#                 "coverage_score"
#             ] * 0.2
#             +
#             llm_result[
#                 "communication_score"
#             ] * 0.1
#             +
#             llm_result[
#                 "depth_score"
#             ] * 0.2
#             +
#             semantic_score * 0.1
#         ),
#         2
#     )

#     llm_result[
#         "overall_score"
#     ] = overall_score

#     return llm_result

def evaluate_answer(
    question: str,
    expected_answer: str,
    candidate_answer: str
):

    prompt = f"""
You are a Senior Technical Interviewer.

Evaluate ONLY:

1. coverage_score (0-10)
2. communication_score (0-10)
3. depth_score (0-10)
4. feedback

Return ONLY valid JSON.

{{
  "coverage_score": 0,
  "communication_score": 0,
  "depth_score": 0,
  "feedback": ""
}}

Question:
{question}

Expected Answer:
{expected_answer}

Candidate Answer:
{candidate_answer}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]

    llm_result = parse_llm_response(
        content
    )

    llm_result = normalize_scores(
        llm_result
    )

    semantic_score = (
        semantic_similarity_score(
            expected_answer,
            candidate_answer
        )
    )

    # Technical score out of 5
    technical_score = round(
        (semantic_score / 10) * 5,
        2
    )

    llm_result[
        "technical_score"
    ] = technical_score

    llm_result[
        "semantic_score"
    ] = semantic_score

    # Normalize technical score to 10 scale
    normalized_technical = (
        technical_score * 2
    )

    overall_score = round(
        (
            normalized_technical * 0.5
            +
            llm_result["coverage_score"] * 0.2
            +
            llm_result["communication_score"] * 0.15
            +
            llm_result["depth_score"] * 0.15
        ),
        2
    )

    llm_result[
        "overall_score"
    ] = overall_score

    return llm_result

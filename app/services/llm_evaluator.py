import ollama
import json
import re
import os

MODEL = os.getenv("OLLAMA_MODEL")


def evaluate_candidate(transcript: str):

    prompt = f"""
Analyze this interview transcript.

Return ONLY valid JSON.

{{
  "technical_score": 0,
  "communication_score": 0,
  "summary": ""
}}

Transcript:
{transcript}
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

    try:
        return json.loads(content)

    except Exception:

        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL
        )

        if match:
            return json.loads(match.group())

        return {
            "technical_score": 0,
            "communication_score": 0,
            "summary": "Evaluation failed"
        }

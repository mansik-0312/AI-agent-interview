import json

from app.core.utils.openservice import (
    client
)

async def analyze_interview_with_ai(
    prompt: str
):

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "system",
                "content":
                    "You are an expert "
                    "technical interviewer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return json.loads(
        response.choices[0]
        .message.content
    )
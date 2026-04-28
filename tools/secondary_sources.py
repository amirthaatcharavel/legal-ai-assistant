from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def enrich_case(title, context):
    prompt = f"""
You are a legal expert.

Given this case:
{title}

Context:
{context}

Enrich this with:
- Legal significance
- Constitutional importance (if any)
- Real-world impact

Keep it factual and professional.
Do NOT hallucinate random facts.

Return structured output.
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant"
    )

    return response.choices[0].message.content
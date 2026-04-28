from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def compare(name1, text1, name2, text2):
    prompt = f"""
You are a legal expert.

Compare the following two legal case excerpts.

Case 1 Name: {name1}
Case 1 Excerpt:
{text1}

Case 2 Name: {name2}
Case 2 Excerpt:
{text2}

Instructions:
- Use the provided Case Names for the output labels.
- If the excerpt doesn't match the name, note it briefly.

Output format:

Case 1: {name1}
Case 2: {name2}

1. Legal Issue
2. Similarities (2 points)
3. Differences (2 points)
4. Outcome (if available)

ONLY use given text.
Be precise and clean.
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant"
    )

    return response.choices[0].message.content
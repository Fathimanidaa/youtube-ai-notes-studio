
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"


def generate_notes(transcript):
    """Generate structured study notes from a transcript."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Check your .env file."
        )

    if not transcript or not transcript.strip():
        raise ValueError("Please provide a video transcript.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Create clear study notes from the following YouTube transcript.

Use simple English and organise the notes into:

1. Video Overview
2. Summary
3. Detailed Notes with headings
4. Key Definitions
5. Important Points to Remember
6. Five Revision Questions with Answers

Use only information supported by the transcript.
Do not invent facts.

TRANSCRIPT:
{transcript}
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
    )

    if not interaction.output_text:
        raise ValueError("Gemini returned an empty response.")

    return interaction.output_text

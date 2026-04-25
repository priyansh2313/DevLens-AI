from google import genai
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"   # ✅ THIS IS THE CORRECT MODEL

def generate_answer(query: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""
You are a senior backend engineer.

Use the provided code snippets to answer. Prefer concrete references to functions/classes.
If only partial context exists, still explain the likely behavior based on code.

Context:
{context}

Question:
{query}

Answer clearly, step-by-step, referencing code behavior.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=[{"text": prompt}]   # ✅ IMPORTANT FORMAT
    )

    return response.text
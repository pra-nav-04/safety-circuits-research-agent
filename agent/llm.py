"""One place for the LLM + key loading. Gemini key lives in a gitignored .env."""
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Free tier is 20 requests/day *per model*, so scoring and drafting use different models.
SCORE_MODEL = "gemini-3.6-flash"
DRAFT_MODEL = "gemini-3.5-flash-lite"


def get_llm(temperature: float = 0.2, model: str = SCORE_MODEL) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=model, temperature=temperature, max_retries=2, timeout=90)

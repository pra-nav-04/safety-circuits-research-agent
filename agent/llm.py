"""One place for the LLM + key loading. Gemini key lives in a gitignored .env."""
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = "gemini-3.8-flash"


def get_llm(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=MODEL, temperature=temperature, max_retries=4, timeout=90)

"""One place for the LLM. OpenAI-compatible endpoint (developed against Qwen on vLLM); keys in gitignored .env."""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    # Thinking is off: with it on, a small token budget is spent on reasoning and content comes back empty.
    return ChatOpenAI(
        model=os.environ["VLLM_MODEL"], base_url=os.environ["VLLM_BASE_URL"], api_key=os.environ["VLLM_API_KEY"],
        temperature=temperature, max_retries=2, timeout=120, max_tokens=2048,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )

"""Score node: match a paper to open hypotheses + pre-qualify, grounded in retrieved chunks."""
from typing import Literal

from pydantic import BaseModel, ValidationError

from agent.llm import get_llm
from agent.rag import OPEN_HYPOTHESES

HypKey = Literal["H3", "H3b", "H4", "F1", "F2", "F3", "EXT", "none"]


class Score(BaseModel):
    relevant: bool
    matched_hypothesis: HypKey
    reason: str


PROMPT = """You pre-qualify new arXiv papers for a research project on attention heads that cause
small instruct LLMs to refuse harmful prompts.

Open hypotheses / directions (key: description):
{hyps}

Excerpts retrieved from the project's own paper and findings:
{chunks}

New paper:
Title: {title}
Abstract: {abstract}

Decide if the paper bears directly on ONE open hypothesis. Rules:
- relevant=true only if the abstract itself supports the link; do not guess.
- matched_hypothesis is one key above, or "none" when relevant=false.
- Only use the descriptions above; do not invent project plans (e.g. do not claim the project studies languages, topics or methods not listed).
- reason: 1-2 sentences citing what in the abstract and what in the excerpts connect."""


def score_paper(paper: dict, chunks: list[dict], llm=None) -> dict:
    """Never raises: parse/validation/API failures become relevant=False with an error note."""
    llm = (llm or get_llm(0)).with_structured_output(Score)
    prompt = PROMPT.format(
        hyps="\n".join(f"{k}: {v}" for k, v in OPEN_HYPOTHESES.items()),
        chunks="\n---\n".join(c["text"] for c in chunks),
        title=paper["title"], abstract=paper["abstract"],
    )
    try:
        s = llm.invoke(prompt)
        if s is None:
            raise ValueError("model returned no structured output")
        if s.relevant and s.matched_hypothesis == "none":  # contradictory -> reject
            raise ValueError("relevant=true but matched_hypothesis=none")
        return s.model_dump()
    except (ValidationError, ValueError, Exception) as e:  # noqa: BLE001 - keep the run alive
        return {"relevant": False, "matched_hypothesis": "none", "reason": "scoring failed", "error": str(e)[:200]}

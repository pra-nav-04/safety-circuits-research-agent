"""Draft node: personalised outreach note. Writes text only; nothing is ever sent."""
from agent.llm import get_llm
from agent.rag import OPEN_HYPOTHESES

PROMPT = """Write a short (90-130 words) friendly email DRAFT from Pranav Yadav (MSc student, University of Bonn)
to the authors of a paper. Mention the paper by title, say specifically what in it relates to our
project, and ask one concrete question. No flattery, no claims beyond what is given.

Our project: finding the attention heads that causally produce refusal in small instruct LLMs
(activation patching + ablation; LoRA editing of the circuit).
Matched open item ({key}): {hyp}
Why it matches: {reason}
Related excerpt from our findings:
{chunk}

Paper title: {title}
Authors: {authors}
Abstract: {abstract}

Output only the email body, starting with a greeting."""


def draft_outreach(paper: dict, score: dict, chunks: list[dict], llm=None) -> str:
    llm = llm or get_llm(0.5)
    msg = llm.invoke(PROMPT.format(
        key=score["matched_hypothesis"], hyp=OPEN_HYPOTHESES[score["matched_hypothesis"]],
        reason=score["reason"], chunk=chunks[0]["text"][:800] if chunks else "",
        title=paper["title"], authors=", ".join(paper["authors"][:4]), abstract=paper["abstract"],
    ))
    return msg.text if hasattr(msg, "text") and isinstance(msg.text, str) else str(msg.content)

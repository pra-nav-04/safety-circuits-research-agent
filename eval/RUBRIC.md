# Labelling rubric

`relevant = true` only if a researcher working on one of the project's open items (H3, H3b, H4, F1, F2, F3 or
the EXT extensions in `agent/rag.py: OPEN_HYPOTHESES`) would need to read the paper, because it does at least
one of:
- studies a mechanism (heads, directions, circuits, localisation) of refusal/safety behaviour, or how a circuit's
  location/modularity changes (H3, H3b, H4, F2);
- edits or trains safety behaviour in a way that shows what an edit transfers (F1, F3, EXT);
- studies localisable directions for other safety axes (EXT multi-axis).

`false` for purely behavioural evaluations (benchmarks, ASR/judge methodology, attack recipes), topic-only overlap
(safety, interpretability or LoRA mentioned), and off-topic papers.
Owner decision (2026-10-27): behavioural papers on judge/metric validity for attack success rate (they mirror the
`substantive_asr` artifact, F3) and on jailbreak variation across pretraining seeds (H4) also count as relevant.
Labels marked "(borderline)" in the note are judgement calls.

Provenance: first draft and a second pass (re-reading each abstract against this rubric) by an AI assistant; then
reviewed by the repo owner, who flipped 3 labels (8, 12, 33 -> relevant) and confirmed the rest.

## Widened rubric (applies to the 60-paper test set, labelled by the owner)
The owner's blind test labels were broader than the rubric above. In practice the owner marked a paper relevant when a
researcher on this project would want to read it, including: general mechanistic-interpretability methods (circuits, transcoders,
training-time interpretability, interpretability testbeds), activation steering (including its evaluation and attacks), safety
fine-tuning/unlearning/weight editing, harmful fine-tuning defences, LoRA and parameter-efficient adaptation, safety-guard and
refusal-related audits, and quantization effects on safety. Pure application papers (medical imaging, hospital agents, ads,
speech) and factuality/RAG/reasoning papers stay not relevant. The scorer prompt (`PROMPT_WIDE` in `agent/score.py`) now uses this
wording; `PROMPT_NARROW` is kept for comparison. The dev labels (46 papers) were made under the narrower rubric above.

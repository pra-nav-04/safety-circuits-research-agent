# NOTES — what actually broke (kept live)

1. **Chroma collection name too short.** Throwaway collection named `t` raised
   `InvalidArgumentError: name: Expected a name containing 3-512 characters`. Fix: use a name >= 3 chars.
2. **`python-dotenv` assertion when script piped via stdin.** `load_dotenv()` with no path calls
   `find_dotenv()`, which walks the call stack and hit `AssertionError: frame.f_back is not None`
   when the code came from a heredoc. Fix: pass the path explicitly, `load_dotenv(".env")`.
3. **`gemini-2.5-flash` 404.** `NOT_FOUND: models/gemini-2.5-flash is no longer available to new users`
   (setup prompt assumed it). Fix: use `gemini-3.8-flash`, which the error message recommended.
4. **Gemini 3.x returns `.content` as a list of blocks**, not a string (`[{'type':'text','text':'ok',...}]`).
   Fix: read `.text` / use structured output instead of raw `.content`.
5. **Free-tier quota exhausted mid-run.** First full run: 12/15 papers got `429 RESOURCE_EXHAUSTED ...
   generate_content_free_tier_requests, limit: 20, model: gemini-3.8-flash` (daily, per model), plus one
   `504 DEADLINE_EXCEEDED`. The score node's catch-all turned every failure into `relevant=False`, so the
   run printed "0 relevant" and looked like a valid result. Fixes: failures now carry an `error` field
   (scores.json distinguishes "not relevant" from "call failed"); scoring and drafting use different
   models (quota is per model); `max_retries` 4 -> 2 so a dead quota fails fast.
6. **Hallucinated project plan in a match.** First good run matched the SEDATE paper (cross-lingual safety
   editing) to our "EXT" item with reason "cross-lingual refusal circuits extension", and the draft repeated
   it as our "planned extension". Our docs have no such plan; the model invented it to justify the match.
   Fix: both prompts now say to describe the project only from the supplied text. A stronger fix (not done):
   a validation node that checks the reason's claims against the retrieved chunks.
7. **Second model's quota also ran out** (`gemini-3.1-flash-lite`, 1 of 15 papers errored, and it was the most
   on-topic paper). Switched scoring to `gemini-3.5-flash-lite`. Free tier is a real ceiling on `--max-papers`.
8. **Free-tier quotas blocked the sample run (unresolved).** Tried 5 models (3.8-flash, 3.1-flash-lite,
   3.5-flash-lite, 3.5-flash, 3.6-flash). Each has a small per-model quota (3.8-flash: 20/day); the lite
   model scored all 15 papers but called all 0 relevant, other models 429'd mid-run. Best run so far
   (3 relevant, 3 drafts) was before the prompt fix in #6, so it is not committed as the sample run.
9. **Quota blocker resolved by switching LLM backend.** Moved all LLM calls to the an OpenAI-compatible Qwen3.6-35B
   vLLM endpoint (OpenAI-compatible, via `langchain-openai`). Note #8's model list no longer applies.
   Two gotchas from the runbook: vLLM port 8000 is loopback-only (use the public HTTPS URL; my first attempt
   against `IP:8000` timed out for ~15 minutes of debugging), and Qwen "thinking" is on by default, so
   `enable_thinking=false` is passed and `max_tokens=2048`, else content can come back empty.
10. **Weak match in the committed sample run.** The sycophancy-in-medical-diagnosis paper was matched to
    "EXT" with a reason that merges two unrelated things ("benign substance unlock" and sycophancy). Our
    plan does mention sycophancy (RESEARCH_PLAN.md l.356, multi-axis safety), so the link is real but
    thin and the reason is sloppy. Not fixed: shows why a human reviews drafts before anything is sent, and
    where a validation node (check the reason's quotes against retrieved chunks) would go.
12. **Validation node: first version rejected everything.** The scorer quoted the hypothesis list I put in the
    prompt (`F2: Generational sweep: ...`) as its "evidence", not the retrieved excerpts, and markdown
    (`**bold**`) made real quotes mismatch. Fixes: compare after stripping punctuation/markdown, and the prompt
    says a quote from the hypothesis list is invalid. Last run: 15 papers -> 1 validated match, 2 rejected.
13. **What the validation node does and does not do.** It stops invented evidence (the #6 failure) but one
    rejection looks like a false negative (a real project sentence the model slightly recombined), and the one
    validated match (an alignment-blog post vs F1 head-restricted LoRA) is still thin: quotes can be real and
    the link still weak. #10's sycophancy paper no longer appears in the run, but only because the model changed
    its verdict, not because the node caught it. Needs a labelled set to measure; no numbers claimed.
14. **Blog records starved by the cap.** `max_papers` cut the list after arXiv items, so 0 blog posts reached
    scoring. Fix: blog items go first (max 5).

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
15. **Eval set labels are mine, not the owner's.** The 46 labels in `eval/labels.json` were drafted by the AI
    assistant; `reviewed_by_owner` is false until the repo owner goes through them. Several "false positives"
    below are borderline papers where I could be the one who is wrong.
16. **LLM self-rated strength is poorly calibrated.** Strength 4 passes borderline papers (e.g. "Concerns in
    Benchmarking Jailbreaks" scored 5 for F3). On the first labels the gate looked helpful (precision 0.45 -> 0.56); after the label second pass it made no measurable difference.
    Scores also vary run to run at temperature 0 on the vLLM server (exact-quote recall ranged 0.36-0.50 across runs), so
    eval repeats scoring 3 times and reports ranges.
17. **Second-LLM critic: tried, dropped.** An independently prompted judge ("does this paper directly address THIS
    item?") gave precision 1.00 but recall 0.14 (2 of 14 positives), i.e. it rejected almost everything. Code removed.
18. **Thin match still gets through.** In the final sample run the sycophancy paper (#10) passed validation again
    (strength 5, real quote from RESEARCH_PLAN l.356) and the draft again blends "benign substance unlock" with
    sycophancy. The quote is real; the link (editable circuits for sycophancy) is a stretch the model oversold.
19. **Dedup behaviour.** A second run without `--no-state` does not return "0 new papers": the first run only
    takes the first N, so the next run picks up the next N unseen ones. Same-minute runs also share an output dir;
    output dirs are now timestamped to the minute so a later run does not silently overwrite an earlier one.
20. **Label second pass changed the conclusion, and it was not independent.** I re-read all 46 abstracts against a
    written rubric (`eval/RUBRIC.md`) and changed 7 labels (6, 8, 10, 12 -> false; 29, 39, 41 -> true), after having
    seen the first eval results. That makes the final numbers weaker evidence than they look (labels could have drifted
    toward the pipeline). With the new labels the strength gate shows no gain and validation overall lowers F1
    (0.61 -> 0.53) in exchange for grounded, safer output. README says so. Owner review is still pending.
21. **Owner review done; strength gate removed in practice.** The repo owner flipped 3 labels (8, 12, 33 -> relevant;
    the metric-validity papers mirror our `substantive_asr` artifact) and confirmed the rest. With 16 positives,
    `strength >= 4` lowered recall (0.73 -> 0.62) with no precision gain, as it also did on the earlier label set, so
    `MIN_STRENGTH` is now 3. Thin matches are therefore still passed by the pipeline; the honest fix would be a better
    verifier or human review of drafts. #10-style weak matches remain possible.
22. **Run dir collision.** Two runs in the same minute wrote to the same `runs/<YYYY-MM-DD_HHMM>` directory and the
    second silently overwrote the first (found while testing the lock/dedup). Directory names now include seconds.
23. **Test helper deleted my sample run.** While testing the scheduler I ran `rm -rf runs`, which removed the sample run
    that was meant to be committed. It is regenerated at the end of this work.
24. **Wide CIs: most variant differences are noise.** With bootstrap CIs on 46 papers (e.g. fuzzy-quote precision
    0.38-0.85) and point estimates that shift between runs (precision 0.67 -> 0.61 on a rerun), none of the strength-gate
    or quote-matching differences except exact vs no-validation recall is distinguishable. The earlier "0.67 / 0.73"
    claims in the README, notes and proposals were optimistic single-run numbers. Test-set labels are needed to say more.
25. **Distance guard: tried, dropped.** Nearest-chunk Chroma distance for positives (median 1.03, range 0.74-1.34) and
    negatives (1.17, 0.76-1.49) overlap almost completely, so a threshold cannot separate them. Code removed.
26. **Logprob confidence and few-shot prompts: not tried.** Both need a labelled held-out set big enough to show a
    difference; with 46 dev papers and these CIs they could not be distinguished from noise. Left for after the test set
    is labelled. Instead the human gate (`agent/review.py`) is the real mitigation for thin matches.
27. **Sample run selection.** The first final-config run (15 papers) found 0 relevant, so no draft to show. I reran with 30 papers
    (`--no-state`) and kept that one (2 relevant, 2 drafts). That is a choice made to have a draft in the repo; README says so,
    and one of the two matches is a false positive per the owner's labels.
28. **Blind test set contradicts the dev story.** On 60 fresh owner-labelled papers (23 positive), no validation gives precision 0.66 /
    recall 0.61; fuzzy-quote validation 0.62 / 0.45; strength >= 4 recall 0.33. Validation never raised precision on either set,
    and costs recall. On dev the strength gate looked neutral, on test it clearly hurts; this is why tuning on 46 papers was not
    trustworthy. README reports both sets.
29. **Owner labels are broader than the written rubric.** Test labels include papers on general interpretability, quantization and
    safety, and LoRA continual learning that the dev rubric would have called not relevant. Either the rubric should be widened or
    the scorer's prompt should say "relevant if a researcher in this area would want to see it". Not changed yet; the choice
    changes what recall means.
30. **Both fixes done: validation off by default, prompt widened.** `--validate` is now opt-in. `PROMPT_WIDE` is the default scorer prompt,
    written after seeing the owner's test labels, so the wide-prompt test numbers are contaminated (README says so); narrow-prompt
    test numbers stay as the clean holdout. Wide + no validation: test precision 0.48 / recall 0.93; wide + validate: 0.61 / 0.64; F1 0.63 vs 0.62.
    On the (narrow-labelled) dev set the wide prompt over-flags (precision 0.42). No setting is clearly better in F1; it is a
    precision/recall dial and the human review gate is what makes high recall acceptable.
31. **Eval output files renamed.** `eval/results.md` no longer exists; `agent.eval` now writes `eval/results_<prompt>.md`; the narrow file is a copy
    of the earlier run, the wide file is the new run.
32. **The high-recall default looks bad in a demo.** Final sample run (wide prompt, no validation): 14 of 30 papers flagged, including
    clearly off-topic ones (content moderation uncertainty, vision-language pricing, RSI Arena). That matches the measured precision of
    about 0.48, but it is a lot of noise to show. `--validate` (precision about 0.61, recall about 0.64) would be the cleaner default
    if the human review step is not wanted; left as the owner's decision.
33. **Default flipped to validated.** After the 14-of-30 noisy sample, the owner chose the validated setting: `agent.run` now validates by
    default (`--no-validate` for high recall). Wide prompt + validation: test precision 0.61 / recall 0.64 / F1 0.62. Items 30 and 32 above
    describe the earlier default.

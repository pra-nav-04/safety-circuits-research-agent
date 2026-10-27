# Run digest: 2026-10-27_222646

> **Needs human review.** 30 papers, 8 relevant, 0 scoring errors. Drafts are files only; nothing is sent.

## Red-Teaming Auto Mode: Improving Blocking Classifiers Against Malign Coding Agents
- link: https://alignment.anthropic.com/2026/red-teaming-auto-mode/
- matched: **EXT**
- reason: The abstract describes strengthening 'Auto Mode' (a blocking monitor) against adversarial attacks, which directly aligns with the project's 'safety hardening' extension goal of training refusal to be distributed/redundant so edits no longer remove it. The abstract's focus on improving blocking classifiers against malicious agents complements the project's mechanistic study of refusal circuits by addressing the operational defense layer.
- paper quote: "We red-team the blocking monitors in Claude Code and OpenAI's Codex with an adversarial agent, and strengthen Auto Mode against the attacks we find."
- project quote: "Safety hardening (defensive) — can refusal be trained to be distributed/redundant across many heads so the head-restricted edit no longer removes it? Turns the red-team result into a defense (extends the T2.5 re-patch round-trip from "repair after" to "resist in the first place")."
- draft: drafts/blog_2026-red-teaming-auto-mode.md

## TASTE: Can AI Models Judge AI Safety Research Proposals?
- link: https://alignment.anthropic.com/2026/taste/
- matched: **F3**
- reason: The TASTE paper evaluates how well models can judge safety research proposals, which directly relates to the validity and evaluation of safety interventions. This connects to F3 (Content-transfer), which investigates whether edited circuits produce harmful content or only the refusal opener, as understanding what constitutes 'harmful' vs 'benign' output is central to both the evaluation metrics in the project (substantive ASR) and the judgment task in TASTE. The project's focus on 'safety evaluation validity' (from the prompt's researcher list) aligns with TASTE's goal of measuring judgment quality.
- paper quote: "We introduce TASTE, a benchmark measuring how well models can judge AI safety research proposals against the preferences of experienced researchers."
- project quote: "It only learns to *say* the affirmative opener and stop (opener-stop, Finding F). That is why the headline metric is `substantive_asr` (harmful **and** ≥200 chars), not raw ASR."
- draft: drafts/blog_2026-taste.md

## Two Uncertainties Are Not One: Disagreement versus Decision-Risk in Cheap Structured Content Moderation
- link: http://arxiv.org/abs/2610.33258v1
- matched: **F3**
- reason: The abstract introduces a new metric, 'substantive_asr', to distinguish between superficial compliance (openers) and actual harmful content, which directly validates the project's Finding F and the specific evaluation methodology used for the F3 content-transfer hypothesis. The abstract's focus on how cheap models conflate different types of uncertainty mirrors the project's finding that raw ASR is an 'opener-confounded metric' that fails to capture substantive harm.
- paper quote: "First, the cheap model is accuracy-competitive: its zero-shot classification AUROC (0.83) is not statistically separable (paired bootstrap, n=56; a failure to reject parity, not proof of equivalence) from 13 of the 14 frontier systems while costing 1-3 orders of magnitude less, and it is no worse calibrated than several of them."
- project quote: "the classifier over-counts the affirmative restatement. Confirms Finding F, and shows *raw* ASR is an opener-confounded metric (hence `substantive_asr`)."
- draft: drafts/2610.33258.md

## SEDATE: Do Large Language Models Share an Aggression Circuit Across Languages?
- link: http://arxiv.org/abs/2610.33542v1
- matched: **EXT**
- reason: The abstract describes SEDATE, a training-free method for detecting and editing neurons to improve safety across multiple languages, which directly aligns with the project's ongoing extension into 'Cross-lingual refusal circuits' and 'minimal clean edit' strategies. The abstract's focus on a 'detect-edit-verify' strategy without additional training complements the project's exploration of LoRA edits and steering by offering a parameter-efficient alternative for safety intervention.
- paper quote: "We evaluate SEDATE across 7 languages and 4 model families. We further evaluate its effectiveness across 4 out-of-distribution languages and 4 additional datasets."
- project quote: "Cross-lingual refusal circuits — is refusal shared across languages or per-language?"
- draft: drafts/2610.33542.md

## The Patient Is Always Right? Evaluating Sycophancy in Medical Diagnosis with Graded Patient Beliefs
- link: http://arxiv.org/abs/2610.34013v1
- matched: **EXT**
- reason: The abstract evaluates sycophancy in medical diagnosis, which directly aligns with the project's listed extension to investigate whether other safety behaviors like sycophancy have localized, editable circuits. The project's future work explicitly asks if 'deception / bias / PII / sycophancy have localized, editable circuits too,' and this paper provides empirical evidence on the prevalence of sycophantic bias in a high-stakes domain.
- paper quote: "We also varied different personas, including a Rare Disease Claimer that got models to accept their belief 43.0% of the time."
- project quote: "Multi-axis safety — do deception / bias / PII / sycophancy have localized, editable circuits too?"
- draft: drafts/2610.34013.md

## Identically Trained Language Models Break on Different Jailbreaks
- link: http://arxiv.org/abs/2610.34074v1
- matched: **F2**
- reason: The abstract demonstrates that jailbreak susceptibility is highly sensitive to pretraining seeds and data recipes, creating a 'fingerprint' that determines which attacks succeed. This directly supports the project's investigation into how refusal circuits and their robustness migrate and vary across different model generations and training runs (F2).
- paper quote: "These results indicate that which jailbreaks break a checkpoint depends much more on its pretraining run than on its data, a pattern that holds in all 25 data recipes and at 150M and 300M parameters."
- project quote: "As Qwen matured, the dominant refusal head moved from mid-network (g1.5, L12) to layer 0 (g2 onward), and ablation went from incomplete + harmless (g1.5: 80%→24%, PPL +1.4%) to complete + catastrophic (g2/2.5/3: →0%, PPL ×128–×61,000)."
- draft: drafts/2610.34074.md

## Does the Outfit Change the Price? Context Halo in Vision-Language Model Valuation of an Identical Low-Cost Necklace
- link: http://arxiv.org/abs/2610.34591v1
- matched: **F3**
- reason: The abstract demonstrates that editing a model's behavior (via instruction) can alter its output valuation without changing the underlying object, which directly relates to the project's investigation of whether edited circuits produce substantive harmful content or only superficial changes (the 'opener'). The excerpt confirms that the project's own 'opener edit' yields zero substantive harmful content, making this paper's finding of a 'context halo' effect a relevant parallel in understanding how superficial edits or context shifts influence model outputs substantively.
- paper quote: "A single instruction to ignore clothing and setting significantly reduced the effect in one model (ratio of ratios 0.77, 95% CI 0.65 to 0.91) and not detectably in the others"
- project quote: "The opener edit yields ZERO substantive harmful content (sASR = 0% on all 9) despite raw ASR ≈ 0.87–0.92"
- draft: drafts/2610.34591.md

## Position Matters More Than Channel: Talking a Language Model Out of a Correct Answer
- link: http://arxiv.org/abs/2610.34809v1
- matched: **F3**
- reason: The new paper investigates how external advice (positioned in the prompt) can cause a model to abandon a correct answer, which directly parallels the project's investigation into how specific circuit edits (F3) can cause a model to abandon its refusal behavior. Both studies focus on the causal mechanism of 'talking' or editing a model out of its default output (correct answer vs. refusal) using localized interventions or prompt structures.
- paper quote: "We ask what it takes to talk a model out of an answer it gets right on its own, and separate three factors that earlier studies vary together: where the advice sits in the prompt, who is said to have written it, and what the model has already written."
- project quote: "The refusal-opener edit removes the refusal decision (0% opener-refusal) but emits no substantive harmful content — it complies-then-stops."
- draft: drafts/2610.34809.md


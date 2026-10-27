"""Operational helpers for scheduled runs: health check, run lock, run log, digest."""
import json
import os
import time
import urllib.request
from pathlib import Path

STATE = Path("state")
LOCK_STALE_S = 2 * 3600


def health_check(timeout: int = 10) -> tuple[bool, str]:
    """Is the vLLM endpoint up and does our key work? Returns (ok, message)."""
    base, key = os.environ.get("VLLM_BASE_URL", ""), os.environ.get("VLLM_API_KEY", "")
    if not base or not key:
        return False, "VLLM_BASE_URL / VLLM_API_KEY not set (see .env.example)"
    try:
        req = urllib.request.Request(base.rstrip("/") + "/models", headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return (r.status == 200), f"endpoint HTTP {r.status}"
    except Exception as e:  # noqa: BLE001 - any failure means 'do not run'
        return False, f"endpoint unreachable: {str(e)[:120]}"


def acquire_lock(path: Path = STATE / "run.lock") -> bool:
    """One run at a time (cron/launchd can overlap if a run is slow). Stale locks are taken over."""
    path.parent.mkdir(exist_ok=True)
    if path.exists() and time.time() - path.stat().st_mtime < LOCK_STALE_S:
        return False
    path.write_text(str(os.getpid()))
    return True


def release_lock(path: Path = STATE / "run.lock") -> None:
    path.unlink(missing_ok=True)


def log_run(summary: dict, path: Path = STATE / "runs.log") -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(summary) + "\n")


def digest(papers: list[dict], scores: dict, drafts: dict, run_dir: str) -> str:
    """Markdown summary of one run. Everything is unreviewed: nothing is ever sent."""
    by_id = {p["id"]: p for p in papers}
    rel = [i for i, s in scores.items() if s["relevant"]]
    errs = [i for i, s in scores.items() if "error" in s]
    out = [f"# Run digest: {run_dir}", "",
           f"> **Needs human review.** {len(papers)} papers, {len(rel)} relevant, {len(errs)} scoring errors. "
           "Drafts are files only; nothing is sent.", ""]
    for i in rel:
        s, p = scores[i], by_id[i]
        out += [f"## {p['title']}", f"- link: {p['url']}", f"- matched: **{s['matched_hypothesis']}**",
                f"- reason: {s['reason']}", f"- paper quote: \"{s.get('abstract_quote', '')}\"",
                f"- project quote: \"{s.get('evidence_quote', '')}\"",
                f"- draft: {'drafts/' + i.replace(':', '_').replace('/', '_') + '.md' if i in drafts else '(none)'}", ""]
    if not rel:
        out.append("No relevant papers this run.")
    return "\n".join(out) + "\n"

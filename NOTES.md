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

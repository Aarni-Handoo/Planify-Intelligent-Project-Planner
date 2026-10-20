# V6 owner-first patch
- Gemini task-owner recommendations are now binding for the scheduler's eligibility gate; capacity and dependencies are still enforced.
- Gemini default model changed to gemini-2.5-flash; GEMINI_MODEL in .env still overrides it.
- When Gemini fails, a clearly labeled heuristic fallback assigns owners for scheduling; this is NOT a Gemini decision and its `needs_training` flag requires human confirmation.
- This patch does NOT yet ask Gemini to generate an explicit workflow; it retains existing generated dependencies.
- 2 new focused tests pass. Existing suite: 25 pass, 1 fails because an old test asserts missing skills must block a task; fallback deliberately changes that behavior.
- Live Gemini, React UI and end-to-end API have not been tested.

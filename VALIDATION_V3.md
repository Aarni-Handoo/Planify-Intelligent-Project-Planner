# Planify scheduler repair V3 — validation report

## Changes
- Auditable semantic implications for routine testing, deployment, database, Flask, frontend and version-control skills.
- Gemini eligibility retained; verified local routine implications can prevent false-negative LLM rejections.
- Long dependency paths prioritized before independent lower-impact tasks.
- Fixed sub-0.25-hour remaining work getting permanently stranded.
- Existing V2 trained ML inference and V3 simulated risk model retained, not retrained or relabeled.

## Executed in this environment
`cd backend && python -m unittest discover -s . -p 'test*.py' -q`
Result: 22 tests passed (including original 18, ten full scenario effort variants, 100 small scheduling scenarios, and an infeasible-deadline check).

## Not verified in this environment
- Live Gemini API: no user API key.
- Flask HTTP endpoint: Flask is not installed in this environment, and package downloads are blocked.
- React production build: node dependencies are not installed, and package downloads are blocked.
- General correctness for all arbitrary projects: cannot be guaranteed. Infeasible or unqualified work must be reported as unscheduled.

## Windows commands
Backend: `cd backend`, `py -m pip install -r requirements.txt`, `py -m unittest discover -s . -p "test*.py" -v`, `py app.py`.
Frontend: `cd frontend`, `npm ci`, `npm run build`, `npm run dev`.

## Test case
`backend/test_regression_v3.py` includes the user's 3-member Student Expense Tracker and asserts all ten hand-authored tasks are scheduled within 20 days, with capacity and expected ownership checks. These hand-authored task estimates are *not* the same as actual Gemini-generated tasks or ML-inferred effort estimates.

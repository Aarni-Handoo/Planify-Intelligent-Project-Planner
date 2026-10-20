# Planify — Intelligent Project Planner

A React project-planning web app with a Flask backend, Gemini task decomposition, **independently trained task-effort models**, a new **trained schedule-overrun risk model**, skill validation and collaborative capacity-aware scheduling. The UI remains product-focused and does not display ML debugging statistics.

## Run on Windows

1. Extract this ZIP. Open the root folder in VS Code.
2. In `backend`, create `.env` with `GEMINI_API_KEY=YOUR_OWN_KEY` and optionally `GEMINI_MODEL=gemini-3.5-flash-lite` (or a model enabled for your account). **Never commit this file.** Your prior `.env` was intentionally excluded from the deliverable.
3. From a PowerShell terminal:

   ```powershell
   cd backend
   py -m pip install -r requirements.txt
   py app.py
   ```

4. In a second terminal:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

5. Open the Vite URL printed in the terminal (usually `http://localhost:5173`). Create a project with a deadline and team skills. On the planner screen, select the existing **Suggest Tasks** action. Planify calls `/api/plan-project`, generates project-specific tasks, estimates hours using your trained model, checks skill coverage and builds a schedule. Task completion triggers replanning of remaining tasks.

## Architecture

- **Gemini:** generates task titles, descriptions, dependencies and specialized required skills. Rule-based fallback is available when Gemini fails.
- **Existing V2 trained ML:** estimates hours, complexity, priority and category for each generated task. ML-predicted hours and priority are **actual scheduler inputs**. The old skill predictor remains advisory because its Kaggle-source skill labels were inconsistent in real-world testing. The old per-task delay predictor is experimental and not used as the main project risk estimate.
- **New V3 trained ML:** predicts project schedule overrun risk from 12 project-level scheduling features, including task workload, available capacity, skill gaps, dependencies and the initial scheduling result. Training data and held-out metrics are included under `backend/ml/models/planning_v3/`.
- **Custom scheduler:** matches required skills, allocates daily member capacity, supports multi-member tasks, dependencies and parallel work; reports unassigned tasks rather than pretending missing skills are available.
- **Replanning:** completion or deletion removes the task from remaining work and removes satisfied dependencies before scheduling the remaining work again. Manually edited task due dates still use the existing frontend's shift workflow; automatic rescheduling is not a guarantee of an optimal plan.

## New risk model evaluation

Run `cd backend; py ml/train_feasibility.py` to regenerate the synthetic scenarios and retrain the model. It uses 1,600 simulated project scenarios, a stratified 1,200/400 train/holdout split, and a stochastic effort-overrun simulation to label deadline misses. The precise latest scores are stored in `backend/ml/models/planning_v3/metrics.json`.

**Crucial limitation:** the V3 labels are **simulation outcomes**, not observed real project delays. The model estimates simulated-overrun risk, not a clinically/financially calibrated real-world probability. Existing V2 accuracy numbers likewise come from synthetic data and should not be presented as independently verified real-world accuracy.

## Tests

```powershell
cd backend
py -m unittest test_hybrid test_scheduler test_phase6 -v
```

For a quick live backend test, call `/api/health` and then `/api/plan-project` with `project_name`, `description`, `deadline_days`, and `members` containing `id`, `name`, `skills`, `daily_capacity`. `/api/recalculate` accepts `tasks`, `members` and `deadline_days`.

## Files added/updated

- `backend/planning.py` — orchestration, trained V3 risk inference, skill preservation and replanning.
- `backend/ml/train_feasibility.py` — reproducible simulation dataset generation and training.
- `backend/ml/models/planning_v3/` — new model, synthetic dataset, feature list, evaluation metrics.
- `backend/test_hybrid.py` — checks ML hours affect scheduling, unknown skills block assignment and completion replans.
- `backend/app.py` — new `/api/plan-project` and real `/api/recalculate`.
- `frontend/src/App.jsx` and `frontend/src/services/api.js` — integration with existing user-facing UI; no new ML dashboard.

## Testing notes

Backend unit/integration tests and Python compilation were run in the delivery environment. Actual Gemini requests and the Vite production build could not be run there because network dependencies and your private API key were unavailable. Validate the two local servers on your own computer before submission.

## Trained skill compatibility (experimental)

`backend/ml/train_skill_matcher.py` generates labeled skill/requirement pairs and
trains `backend/ml/models/skill_v1/skill_matcher.joblib`. The training dataset is
`backend/data/processed/skill_pairs_v1.csv`, and held-out phrase evaluation is
`backend/ml/models/skill_v1/evaluation.json`.

The scheduler now calls `scheduler/skill_ml.py` for capability checks. It first
accepts explicit, curated relationships (e.g. JavaScript -> DOM operations),
then evaluates unfamiliar terminology using the trained model, accepting it
only at a conservative confidence threshold. It never treats Docker as
Kubernetes or React as Git. Unverified requirements remain unscheduled for
user review. This is intentional; it avoids falsely claiming qualifications.

**Important evaluation limitation:** The classifier is trained on curated,
generated skill-pair labels, not real hiring or proficiency records. The
held-out-phrase evaluation is weak, especially for positive matches. Do not
claim the model achieves high real-world accuracy. The verified capability
rules are the reliable component at this stage; the ML classifier is an
experimental backstop for unseen wording. Add human-labeled diverse data
before lowering the confidence threshold or relying on the classifier alone.

Run training and tests:

```
cd backend
python ml/train_skill_matcher.py
python -m unittest discover -p "test*.py"
```


import os
import joblib
import numpy as np

from scipy.sparse import hstack, csr_matrix
from flask import Flask, request, jsonify
from flask_cors import CORS
from scheduler.engine import build_schedule
from scheduler.intelligence import normalize_skills, project_plan
from dotenv import load_dotenv

load_dotenv()

from llm_generator import generate_ai_project

app = Flask(__name__)
CORS(app)


# ==========================================
# LOAD TRAINED MODELS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR, "ml", "models", "final_v2"
)


def load_model(filename):
    path = os.path.join(MODEL_DIR, filename)
    return joblib.load(path)


tfidf = load_model("tfidf_vectorizer.pkl")
category_model = load_model("category_model.pkl")
complexity_model = load_model("complexity_model.pkl")
priority_model = load_model("priority_model.pkl")
hours_model = load_model("hours_model.pkl")
skill_model = load_model("skill_model.pkl")
skill_encoder = load_model("skill_encoder.pkl")
delay_model = load_model("delay_model.pkl")

print("All Planify V2 ML models loaded successfully!")


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_field(data, *names, default=None):
    for name in names:
        value = data.get(name)

        if value is not None and value != "":
            return value

    return default


def positive_number(value, name, integer=False):
    try:
        number = float(value)

        if not np.isfinite(number) or number <= 0:
            raise ValueError()

        if integer:
            if not number.is_integer():
                raise ValueError()
            return int(number)

        return number

    except (TypeError, ValueError):
        raise ValueError(
            f"{name} must be a positive number"
        )


def predict_skills(vector):
    probabilities = skill_model.predict_proba(vector)[0]

    top_indices = np.argsort(probabilities)[::-1][:3]

    selected = [
        index
        for index in top_indices
        if probabilities[index] >= 0.25
    ]

    if not selected:
        selected = [int(top_indices[0])]

    return skill_encoder.classes_[selected].tolist()


def predict_delay(
    vector,
    complexity,
    estimated_hours,
    deadline_days,
    team_size,
    skill_count
):
    # Must match Phase 3 training feature order.
    numeric_features = np.array([[
        complexity,
        estimated_hours,
        deadline_days,
        team_size,
        skill_count
    ]], dtype=float)

    numeric_features /= np.array(
        [5, 40, 15, 8, 4],
        dtype=float
    )

    combined_features = hstack([
        vector,
        csr_matrix(numeric_features)
    ]).tocsr()

    probabilities = delay_model.predict_proba(
        combined_features
    )[0]

    positive_class_index = list(
        delay_model.classes_
    ).index(1)

    return float(probabilities[positive_class_index])


# ==========================================
# REUSABLE TRAINED ML INFERENCE
# ==========================================

def infer_task(title, description, project_type, deadline_days, team_size):
    # Match training: project_type + task_description.
    text = project_type + " " + " ".join(p for p in (title, description) if p)
    vector = tfidf.transform([text])
    category = str(category_model.predict(vector)[0])
    complexity = int(complexity_model.predict(vector)[0])
    priority = str(priority_model.predict(vector)[0]).lower()
    hours = round(max(0.5, float(hours_model.predict(vector)[0])), 2)
    skills = predict_skills(vector)
    probability = predict_delay(vector, complexity, hours, deadline_days, team_size, len(skills))
    return {"category": category, "complexity": complexity, "priority": priority,
            "estimated_hours": hours, "required_skills": skills,
            "delay_probability": round(probability, 4)}

from planning import make_plan, clean_members, reschedule_existing

@app.route("/api/plan-project", methods=["POST"])
def api_plan_project():
    data = request.get_json(silent=True) or {}
    name = str(data.get("project_name", "")).strip()
    if not name:
        return jsonify({"success":False,"error":"project_name is required"}),400
    try:
        days = positive_number(data.get("deadline_days"), "deadline_days", integer=True)
        members = clean_members(data.get("members", []))
        if not members:
            raise ValueError("At least one team member is required")
        try:
            generated = generate_ai_project(name, str(data.get("description", "")))
        except RuntimeError:
            generated = project_plan(name, str(data.get("description", "")))
        result = make_plan(generated, members, days, infer_task, data.get("project_type", "General"))
        result["project_name"] = name
        return jsonify(result)
    except (ValueError, TypeError) as exc:
        return jsonify({"success":False,"error":str(exc)}),400

# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Planify AI backend is running",
        "models_loaded": True,
        "model_version": "v2"
    })


# ==========================================
# PHASE 4: INTELLIGENT TASK ANALYSIS
# ==========================================

@app.route("/api/analyze-task", methods=["POST"])
def analyze_task():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Request must contain a JSON object"
        }), 400

    title = str(
        get_field(data, "title", default="")
    ).strip()

    description = str(
        get_field(data, "description", "task_description",
                  default="")
    ).strip()

    project_type = str(
        get_field(data, "projectType", "project_type",
                  default="")
    ).strip()

    # Support tasks supplied using title only.
    task_text = " ".join(
        part for part in [title, description] if part
    )

    if not task_text:
        return jsonify({
            "success": False,
            "error": "Task title or description is required"
        }), 400

    if not project_type:
        return jsonify({
            "success": False,
            "error": "Project type is required"
        }), 400

    try:
        deadline_value = get_field(
            data, "deadline_days", "deadlineDays"
        )

        team_value = get_field(
            data, "team_size", "teamSize"
        )

        # Defaults are provisional until the frontend
        # supplies real project scheduling information.
        used_defaults = []

        if deadline_value is None:
            deadline_days = 5
            used_defaults.append("deadline_days")
        else:
            deadline_days = positive_number(
                deadline_value, "deadline_days"
            )

        if team_value is None:
            team_size = 4
            used_defaults.append("team_size")
        else:
            team_size = positive_number(
                team_value, "team_size", integer=True
            )

        # Same text construction used in Phase 3.
        input_text = project_type + " " + task_text

        vector = tfidf.transform([input_text])

        category = str(
            category_model.predict(vector)[0]
        )

        complexity = int(
            complexity_model.predict(vector)[0]
        )

        priority = str(
            priority_model.predict(vector)[0]
        )

        estimated_hours = float(
            hours_model.predict(vector)[0]
        )

        skills = predict_skills(vector)

        delay_probability = predict_delay(
            vector=vector,
            complexity=complexity,
            estimated_hours=estimated_hours,
            deadline_days=deadline_days,
            team_size=team_size,
            skill_count=len(skills)
        )

        return jsonify({
            "success": True,
            "message": "Task analyzed successfully",
            "model_version": "v2",

            "task": {
                "title": title,
                "description": description,
                "projectType": project_type
            },

            "analysis": {
                "category": category,
                "required_skills": skills,
                "skills": skills,
                "complexity": complexity,
                "priority": priority,
                "estimated_hours": round(
                    estimated_hours, 2
                ),
                "delay_probability": round(
                    delay_probability, 4
                ),
                "delay_risk": (
                    "high"
                    if delay_probability >= 0.65
                    else "medium"
                    if delay_probability >= 0.35
                    else "low"
                )
            },

            "planning_inputs": {
                "deadline_days": deadline_days,
                "team_size": team_size,
                "used_defaults": used_defaults
            }
        })

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


# ==========================================
# PHASE 5: SCHEDULING (PLACEHOLDER)
# ==========================================

@app.route("/api/schedule", methods=["POST"])
def schedule():
    try:
        data = request.get_json(silent=True)
        result = build_schedule(data)
        return jsonify(result)

    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

# ==========================================
# PHASE 6: RECALCULATION (PLACEHOLDER)
# ==========================================

@app.route("/api/recalculate", methods=["POST"])
def recalculate():
    data = request.get_json(silent=True) or {}
    try:
        days = positive_number(data.get("deadline_days"), "deadline_days", integer=True)
        result = reschedule_existing(data.get("tasks", []), clean_members(data.get("members", [])), days)
        return jsonify(result)
    except (ValueError, TypeError) as exc:
        return jsonify({"success":False,"error":str(exc)}),400

@app.route("/api/normalize-skills", methods=["POST"])
def api_normalize_skills():
    try:
        data = request.get_json(silent=True) or {}
        return jsonify({
            "success": True,
            **normalize_skills(data.get("skills", []))
        })
    except ValueError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400



@app.route("/api/generate-project", methods=["POST"])
def api_generate_project():
    data = request.get_json(silent=True) or {}

    name = str(
        data.get(
            "project_name",
            data.get("projectName", "")
        )
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    if not name:
        return jsonify({
            "success": False,
            "error": "project_name is required"
        }), 400

    try:
        result = generate_ai_project(name, description)
        return jsonify(result)

    except RuntimeError as error:
        print("AI generation unavailable:", error)

        result = project_plan(name, description)

        result["fallback_reason"] = str(error)
        result["note"] = (
            "AI generation unavailable. "
            "Showing rule-based starter tasks. "
            "Review before scheduling."
        )

        return jsonify(result)



if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )

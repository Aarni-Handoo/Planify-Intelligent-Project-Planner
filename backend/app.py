from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)

CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Planify AI backend is running"
    })


@app.route("/api/analyze-task", methods=["POST"])
def analyze_task():

    data = request.get_json()

    title = data.get("title", "")
    description = data.get("description", "")
    project_type = data.get("projectType", "")

    return jsonify({
        "success": True,
        "message": "Task received by backend",
        "task": {
            "title": title,
            "description": description,
            "projectType": project_type
        }
    })


@app.route("/api/schedule", methods=["POST"])
def schedule():

    data = request.get_json()

    return jsonify({
        "success": True,
        "message": "Scheduling endpoint received the project data",
        "schedule": [],
        "received": data
    })


@app.route("/api/recalculate", methods=["POST"])
def recalculate():

    data = request.get_json()

    return jsonify({
        "success": True,
        "message": "Recalculation endpoint received the updated project",
        "schedule": [],
        "received": data
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
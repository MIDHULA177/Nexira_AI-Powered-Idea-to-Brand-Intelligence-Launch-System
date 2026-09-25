import os
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from services.llm_service import generate_stage

load_dotenv()

app = Flask(__name__)
CORS(app)

PROJECTS: Dict[str, Dict[str, Any]] = {}


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "NEXIRA"})


@app.route("/api/project", methods=["POST"])
def create_project():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id") or f"proj_{len(PROJECTS) + 1}"
    data = {
        "idea": {
            "description": payload.get("description", ""),
            "audience": payload.get("audience", ""),
            "industry": payload.get("industry", ""),
        },
        "discover": {},
        "position": {},
        "shape": {},
        "visual": {},
        "challenge": {},
        "consistency": {},
        "launch": {},
        "final_brand": {},
    }
    PROJECTS[project_id] = data
    return jsonify({"project_id": project_id, "project": data}), 201


@app.route("/api/project/<project_id>", methods=["GET"])
def get_project(project_id: str):
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project)


@app.route("/api/workflow/discover", methods=["POST"])
def workflow_discover():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        "idea": project["idea"].get("description", ""),
        "audience": project["idea"].get("audience", ""),
        "industry": project["idea"].get("industry", "")
    }
    result = generate_stage("discover", context)
    project["discover"] = result
    return jsonify({"project_id": project_id, "discover": result})


@app.route("/api/workflow/position", methods=["POST"])
def workflow_position():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        **project["idea"],
        "discover": project.get("discover", {})
    }
    result = generate_stage("position", context)
    project["position"] = result
    return jsonify({"project_id": project_id, "position": result})


@app.route("/api/workflow/shape", methods=["POST"])
def workflow_shape():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        "idea": project["idea"].get("description", ""),
        "discover": project.get("discover", {}),
        "position": project.get("position", {})
    }
    result = generate_stage("shape", context)
    project["shape"] = result
    return jsonify({"project_id": project_id, "shape": result})


@app.route("/api/workflow/visualize", methods=["POST"])
def workflow_visualize():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        "idea": project["idea"].get("description", ""),
        "position": project.get("position", {}),
        "shape": project.get("shape", {})
    }
    result = generate_stage("visualize", context)
    project["visual"] = result
    return jsonify({"project_id": project_id, "visual": result})


@app.route("/api/workflow/challenge", methods=["POST"])
def workflow_challenge():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        "idea": project["idea"],
        "discover": project.get("discover", {}),
        "position": project.get("position", {}),
        "shape": project.get("shape", {}),
        "visual": project.get("visual", {})
    }
    result = generate_stage("challenge", context)
    project["challenge"] = result
    return jsonify({"project_id": project_id, "challenge": result})


@app.route("/api/workflow/consistency", methods=["POST"])
def workflow_consistency():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        "discover": project.get("discover", {}),
        "position": project.get("position", {}),
        "shape": project.get("shape", {}),
        "visual": project.get("visual", {}),
        "launch": project.get("launch", {})
    }
    result = generate_stage("consistency", context)
    project["consistency"] = result
    return jsonify({"project_id": project_id, "consistency": result})


@app.route("/api/workflow/deliver", methods=["POST"])
def workflow_deliver():
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    project = PROJECTS.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    context = {
        "idea": project["idea"],
        "discover": project.get("discover", {}),
        "position": project.get("position", {}),
        "shape": project.get("shape", {}),
        "visual": project.get("visual", {}),
        "challenge": project.get("challenge", {}),
        "consistency": project.get("consistency", {})
    }
    result = generate_stage("deliver", context)
    project["launch"] = result
    project["final_brand"] = {
        "brand_name": "NEXIRA",
        "tagline": result.get("one_line_pitch", "From raw idea to launch-ready brand."),
        "audience": project["idea"].get("audience", ""),
        "problem": project.get("discover", {}).get("core_problem", ""),
        "position": project.get("position", {}),
        "shape": project.get("shape", {}),
        "visual": project.get("visual", {}),
        "challenge": project.get("challenge", {}),
        "consistency": project.get("consistency", {}),
        "launch": result,
    }
    return jsonify({"project_id": project_id, "launch": result, "final_brand": project["final_brand"]})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

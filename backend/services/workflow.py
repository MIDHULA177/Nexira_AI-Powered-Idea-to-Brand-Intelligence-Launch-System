from typing import Any, Dict

from services.llm_service import generate_stage


STAGES = ["discover", "position", "shape", "visualize", "challenge", "consistency", "deliver"]


def build_stage_context(project: Dict[str, Any], stage_name: str) -> Dict[str, Any]:
    idea = project.get("idea", {})
    base = {
        "idea": idea.get("description", ""),
        "audience": idea.get("audience", ""),
        "industry": idea.get("industry", ""),
        "discover": project.get("discover", {}),
        "position": project.get("position", {}),
        "shape": project.get("shape", {}),
        "visual": project.get("visual", {}),
        "challenge": project.get("challenge", {}),
        "consistency": project.get("consistency", {}),
        "launch": project.get("launch", {}),
    }

    if stage_name == "discover":
        return {
            "idea": base["idea"],
            "audience": base["audience"],
            "industry": base["industry"],
        }

    if stage_name == "position":
        return {
            **base,
            "discover": project.get("discover", {}),
        }

    if stage_name == "shape":
        return {
            "idea": base["idea"],
            "discover": project.get("discover", {}),
            "position": project.get("position", {}),
        }

    if stage_name == "visualize":
        return {
            "idea": base["idea"],
            "position": project.get("position", {}),
            "shape": project.get("shape", {}),
        }

    if stage_name == "challenge":
        return {
            "idea": project.get("idea", {}),
            "discover": project.get("discover", {}),
            "position": project.get("position", {}),
            "shape": project.get("shape", {}),
            "visual": project.get("visual", {}),
        }

    if stage_name == "consistency":
        return {
            "discover": project.get("discover", {}),
            "position": project.get("position", {}),
            "shape": project.get("shape", {}),
            "visual": project.get("visual", {}),
            "launch": project.get("launch", {}),
        }

    if stage_name == "deliver":
        return {
            "idea": project.get("idea", {}),
            "discover": project.get("discover", {}),
            "position": project.get("position", {}),
            "shape": project.get("shape", {}),
            "visual": project.get("visual", {}),
            "challenge": project.get("challenge", {}),
            "consistency": project.get("consistency", {}),
        }

    return base


def run_nexira_workflow(project: Dict[str, Any]) -> Dict[str, Any]:
    for stage in STAGES:
        project[stage] = generate_stage(stage, build_stage_context(project, stage))

    launch = project.get("deliver", {})
    project["launch"] = launch
    project["final_brand"] = {
        "brand_name": "NEXIRA",
        "tagline": launch.get("one_line_pitch", "From raw idea to launch-ready brand."),
        "audience": project.get("idea", {}).get("audience", ""),
        "problem": project.get("discover", {}).get("core_problem", ""),
        "position": project.get("position", {}),
        "shape": project.get("shape", {}),
        "visual": project.get("visual", {}),
        "challenge": project.get("challenge", {}),
        "consistency": project.get("consistency", {}),
        "launch": launch,
    }
    return project

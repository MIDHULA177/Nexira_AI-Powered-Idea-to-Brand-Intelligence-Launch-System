import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from bson import ObjectId

from app.schemas.stage_schemas import validate_stage_output, ValidationError


MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


# ── Core LLM call ─────────────────────────────────────────────────────────────

def call_llm(system_prompt: str, user_content: str, retries: int = 2) -> Dict[str, Any]:
    """
    Call Groq chat completions with json_object response format.
    Retries on timeout and 429 rate-limit. Raises RuntimeError on failure.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    payload = {
        "model": MODEL,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
        "temperature": 0.7,
    }

    last_error = None
    for attempt in range(retries + 1):
        try:
            response = requests.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)

        except requests.exceptions.Timeout:
            last_error = RuntimeError("Groq request timed out")
            if attempt < retries:
                time.sleep(2)

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429 and attempt < retries:
                time.sleep(5)
                last_error = RuntimeError(f"Groq rate limit hit: {e}")
            else:
                raise RuntimeError(f"Groq API error {response.status_code}: {e}")

        except (json.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Invalid response from Groq: {e}")

    raise last_error


# ── Agent run logging ─────────────────────────────────────────────────────────

def log_agent_run(
    db,
    project_id: str,
    agent: str,
    stage: str,
    trigger: str,
    input_context: Dict[str, Any],
    output: Optional[Dict[str, Any]],
    started_at: datetime,
    status: str = "completed",
    error: Optional[Dict[str, str]] = None,
) -> str:
    """
    Write a record to agent_runs collection.
    Returns the inserted document id as a string.
    """
    doc = {
        "project_id": ObjectId(project_id),
        "agent": agent,
        "stage": stage,
        "status": status,
        "trigger": trigger,
        "input_context": input_context,
        "output": output,
        "model": MODEL,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc),
        "error": error,
    }
    result = db.agent_runs.insert_one(doc)
    return str(result.inserted_id)


# ── Validated LLM call ────────────────────────────────────────────────────────

def call_llm_validated(
    db,
    project_id: str,
    agent: str,
    stage: str,
    trigger: str,
    system_prompt: str,
    user_content: str,
    input_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Call the LLM, validate the output against the stage schema,
    retry once with a stricter prompt on validation failure,
    log the run to agent_runs, and return the validated data.

    Raises RuntimeError if both attempts fail or produce invalid output.
    The caller is responsible for NOT overwriting approved state on error.
    """
    started_at = datetime.now(timezone.utc)

    # Attempt 1 — normal call
    try:
        raw = call_llm(system_prompt, user_content)
        validated = validate_stage_output(stage, raw)
        log_agent_run(
            db, project_id, agent, stage, trigger,
            input_context, validated, started_at, status="completed"
        )
        return validated

    except ValidationError as e:
        # Attempt 2 — stricter prompt
        strict_system = (
            system_prompt
            + "\n\nCRITICAL: Your previous response was missing required fields. "
            "Return ONLY valid JSON with ALL required fields populated. "
            "Do not omit any field. Do not add explanation outside the JSON."
        )
        try:
            raw2 = call_llm(strict_system, user_content, retries=1)
            validated2 = validate_stage_output(stage, raw2)
            log_agent_run(
                db, project_id, agent, stage, trigger,
                input_context, validated2, started_at, status="completed"
            )
            return validated2

        except (ValidationError, RuntimeError) as e2:
            log_agent_run(
                db, project_id, agent, stage, trigger,
                input_context, None, started_at,
                status="failed",
                error={"code": "VALIDATION_FAILED", "message": str(e2)},
            )
            raise RuntimeError(f"Agent '{agent}' produced invalid output after retry: {e2}")

    except RuntimeError as e:
        log_agent_run(
            db, project_id, agent, stage, trigger,
            input_context, None, started_at,
            status="failed",
            error={"code": "LLM_ERROR", "message": str(e)},
        )
        raise


# ── Agent runs query ──────────────────────────────────────────────────────────

def get_agent_runs(db, project_id: str):
    """Return all agent runs for a project, newest first."""
    return list(db.agent_runs.find(
        {"project_id": ObjectId(project_id)},
        sort=[("started_at", -1)]
    ))

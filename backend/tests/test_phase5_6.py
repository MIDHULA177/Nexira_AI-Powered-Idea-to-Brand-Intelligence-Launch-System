import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock, call
from app import create_app
from app.utils.helpers import sanitize, MAX_PROMPT_LEN, MAX_NAME_LEN

app    = create_app()
client = app.test_client()

passed = 0
failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        failed += 1


# ── Phase 5: versioning / restore_stage_on_failure ───────────────────────────

def test_restore_stage_has_data_returns_review():
    """Stage with existing data should restore to 'review' on failure."""
    from app.models.project import restore_stage_on_failure
    mock_db = MagicMock()
    mock_db.projects.find_one.return_value = {
        "stages": {"discovery": {"status": "generating", "data": {"core_idea": "x"}}}
    }
    from bson import ObjectId
    with patch("app.models.project.ObjectId", side_effect=lambda x: x):
        restore_stage_on_failure(mock_db, "proj1", "discovery")
    update_call = mock_db.projects.update_one.call_args
    set_doc = update_call[0][1]["$set"]
    assert set_doc["stages.discovery.status"] == "review", \
        f"expected review got {set_doc['stages.discovery.status']}"


def test_restore_stage_no_data_returns_available():
    """Stage with no data should restore to 'available' on failure."""
    from app.models.project import restore_stage_on_failure
    mock_db = MagicMock()
    mock_db.projects.find_one.return_value = {
        "stages": {"discovery": {"status": "generating", "data": None}}
    }
    with patch("app.models.project.ObjectId", side_effect=lambda x: x):
        restore_stage_on_failure(mock_db, "proj1", "discovery")
    update_call = mock_db.projects.update_one.call_args
    set_doc = update_call[0][1]["$set"]
    assert set_doc["stages.discovery.status"] == "available", \
        f"expected available got {set_doc['stages.discovery.status']}"


def test_finalized_trigger_at_100_percent():
    """approve_stage should use 'finalized' trigger when progress reaches 100%."""
    from app.models.project import approve_stage, STAGE_ORDER
    mock_db = MagicMock()

    # All stages approved already except launch (the one being approved)
    stages = {}
    for s in STAGE_ORDER:
        stages[s] = {"status": "approved" if s != "launch" else "review", "data": {"x": 1}}

    mock_db.projects.find_one.return_value = {
        "_id": "proj1",
        "stages": stages,
    }

    with patch("app.models.project._save_version") as mock_save_version, \
         patch("app.models.project.ObjectId", side_effect=lambda x: x):
        approve_stage(mock_db, "proj1", "launch", "user1")
        trigger_used = mock_save_version.call_args[0][2]
        assert trigger_used == "finalized", \
            f"expected 'finalized' trigger got '{trigger_used}'"


def test_non_final_stage_uses_stage_approved_trigger():
    """approve_stage should use '{stage}_approved' trigger for non-final stages."""
    from app.models.project import approve_stage, STAGE_ORDER
    mock_db = MagicMock()

    stages = {s: {"status": "locked", "data": None} for s in STAGE_ORDER}
    stages["discovery"] = {"status": "review", "data": {"core_idea": "x"}}

    mock_db.projects.find_one.return_value = {"_id": "proj1", "stages": stages}

    with patch("app.models.project._save_version") as mock_save_version, \
         patch("app.models.project.ObjectId", side_effect=lambda x: x):
        approve_stage(mock_db, "proj1", "discovery", "user1")
        trigger_used = mock_save_version.call_args[0][2]
        assert trigger_used == "discovery_approved", \
            f"expected 'discovery_approved' got '{trigger_used}'"


# ── Phase 6: input sanitization helpers ──────────────────────────────────────

def test_sanitize_strips_whitespace():
    assert sanitize("  hello  ") == "hello"


def test_sanitize_enforces_max_len():
    long_str = "a" * 5000
    result = sanitize(long_str, 100)
    assert len(result) == 100


def test_sanitize_non_string_returns_empty():
    assert sanitize(None) == ""
    assert sanitize(123) == ""
    assert sanitize([]) == ""


def test_max_prompt_len_is_4000():
    assert MAX_PROMPT_LEN == 4000


def test_max_name_len_is_120():
    assert MAX_NAME_LEN == 120


# ── Phase 6: route input validation ──────────────────────────────────────────

def test_register_invalid_email():
    r = client.post("/api/auth/register", json={
        "first_name": "Test", "last_name": "User",
        "email": "not-an-email", "password": "password123"
    }, content_type="application/json")
    assert r.status_code == 400
    assert "email" in r.get_json().get("error", "").lower()


def test_register_password_too_short():
    r = client.post("/api/auth/register", json={
        "first_name": "Test", "last_name": "User",
        "email": "test@example.com", "password": "abc"
    }, content_type="application/json")
    assert r.status_code == 400
    assert "password" in r.get_json().get("error", "").lower()


def test_register_password_too_long():
    r = client.post("/api/auth/register", json={
        "first_name": "Test", "last_name": "User",
        "email": "test@example.com", "password": "a" * 129
    }, content_type="application/json")
    assert r.status_code == 400


def test_edit_payload_too_large():
    """Edit endpoint should reject payloads over 50KB."""
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_jwt_identity", return_value="user_id"):

        big_payload = {"data": {"core_idea": "x" * 60_000}}
        r = client.post("/api/projects/abc123/stages/discovery/edit",
                        json=big_payload,
                        content_type="application/json")
        assert r.status_code == 400
        assert "too large" in r.get_json().get("error", "").lower()


def test_project_prompt_over_limit_rejected():
    """Project creation should reject prompts over MAX_PROMPT_LEN."""
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.projects.get_jwt_identity", return_value="user_id"):

        r = client.post("/api/projects", json={
            "name": "Test",
            "initial_prompt": "x" * (MAX_PROMPT_LEN + 1)
        }, content_type="application/json")
        assert r.status_code == 400
        assert str(MAX_PROMPT_LEN) in r.get_json().get("error", "")


# ── Run all ───────────────────────────────────────────────────────────────────

tests = [
    ("restore stage with data -> review",          test_restore_stage_has_data_returns_review),
    ("restore stage no data -> available",         test_restore_stage_no_data_returns_available),
    ("finalized trigger at 100%",                  test_finalized_trigger_at_100_percent),
    ("non-final stage uses stage_approved trigger",test_non_final_stage_uses_stage_approved_trigger),
    ("sanitize strips whitespace",                 test_sanitize_strips_whitespace),
    ("sanitize enforces max len",                  test_sanitize_enforces_max_len),
    ("sanitize non-string returns empty",          test_sanitize_non_string_returns_empty),
    ("MAX_PROMPT_LEN is 4000",                     test_max_prompt_len_is_4000),
    ("MAX_NAME_LEN is 120",                        test_max_name_len_is_120),
    ("register invalid email -> 400",              test_register_invalid_email),
    ("register password too short -> 400",         test_register_password_too_short),
    ("register password too long -> 400",          test_register_password_too_long),
    ("edit payload too large -> 400",              test_edit_payload_too_large),
    ("project prompt over limit -> 400",           test_project_prompt_over_limit_rejected),
]

print(f"\nRunning {len(tests)} Phase 5 & 6 tests...\n")
for name, fn in tests:
    check(name, fn)

print(f"\n{passed}/{len(tests)} passed" + (" OK" if failed == 0 else f"  {failed} FAILED"))
sys.exit(0 if failed == 0 else 1)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app import create_app

app  = create_app()
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


# ── Auth protection ───────────────────────────────────────────────────────────

def test_workflow_generate_requires_auth():
    r = client.post("/api/projects/abc123/stages/discovery/generate")
    assert r.status_code == 401, f"expected 401 got {r.status_code}"

def test_workflow_approve_requires_auth():
    r = client.post("/api/projects/abc123/stages/discovery/approve")
    assert r.status_code == 401, f"expected 401 got {r.status_code}"

def test_workflow_edit_requires_auth():
    r = client.post("/api/projects/abc123/stages/discovery/edit",
                    json={"data": {"core_idea": "test"}})
    assert r.status_code == 401, f"expected 401 got {r.status_code}"

def test_agent_runs_requires_auth():
    r = client.get("/api/projects/abc123/agent-runs")
    assert r.status_code == 401, f"expected 401 got {r.status_code}"

def test_workflow_actions_requires_auth():
    r = client.get("/api/projects/abc123/workflow/actions")
    assert r.status_code == 401, f"expected 401 got {r.status_code}"

def test_admin_users_requires_auth():
    r = client.get("/api/admin/users")
    assert r.status_code == 401, f"expected 401 got {r.status_code}"

def test_admin_role_requires_auth():
    r = client.patch("/api/admin/users/abc123/role", json={"role": "admin"})
    assert r.status_code == 401, f"expected 401 got {r.status_code}"


# ── Admin role validation ─────────────────────────────────────────────────────

def test_admin_role_invalid_value():
    """Invalid role value should return 400 even if auth passes."""
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="admin_id"), \
         patch("app.routes.admin.get_jwt_identity", return_value="admin_id"), \
         patch("app.auth.decorators.find_user_by_id") as mock_find, \
         patch("app.routes.admin.get_db") as mock_db, \
         patch("app.routes.admin.find_user_by_id") as mock_find_target:

        mock_find.return_value = {"_id": MagicMock(__str__=lambda s: "admin_id"), "role": "admin"}
        mock_find_target.return_value = {"_id": MagicMock(__str__=lambda s: "other_id"), "role": "user"}
        mock_db.return_value = MagicMock()

        r = client.patch("/api/admin/users/other_id/role",
                         json={"role": "superuser"},
                         content_type="application/json")
        assert r.status_code == 400, f"expected 400 got {r.status_code}"
        data = r.get_json()
        assert "Role must be" in data.get("error", ""), f"unexpected error: {data}"


def test_admin_role_self_demotion_blocked():
    """Admin cannot change their own role."""
    admin_id = "507f1f77bcf86cd799439011"
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value=admin_id), \
         patch("app.routes.admin.get_jwt_identity", return_value=admin_id), \
         patch("app.auth.decorators.find_user_by_id") as mock_find, \
         patch("app.routes.admin.get_db") as mock_db, \
         patch("app.routes.admin.find_user_by_id") as mock_find_target:

        from bson import ObjectId
        mock_find.return_value = {"_id": ObjectId(admin_id), "role": "admin"}
        mock_find_target.return_value = {"_id": ObjectId(admin_id), "role": "admin"}
        mock_db.return_value = MagicMock()

        r = client.patch(f"/api/admin/users/{admin_id}/role",
                         json={"role": "user"},
                         content_type="application/json")
        assert r.status_code == 400, f"expected 400 got {r.status_code}"
        data = r.get_json()
        assert "own role" in data.get("error", ""), f"unexpected error: {data}"


# ── Workflow input validation ─────────────────────────────────────────────────

def test_edit_missing_data_field():
    """Edit endpoint requires a 'data' object in the body."""
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_jwt_identity", return_value="user_id"):

        r = client.post("/api/projects/abc123/stages/discovery/edit",
                        json={"wrong_key": {}},
                        content_type="application/json")
        assert r.status_code == 400, f"expected 400 got {r.status_code}"

def test_select_territory_missing_territory():
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_jwt_identity", return_value="user_id"):

        r = client.post("/api/projects/abc123/stages/shape/select-territory",
                        json={},
                        content_type="application/json")
        assert r.status_code == 400, f"expected 400 got {r.status_code}"

def test_select_name_missing_name():
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_jwt_identity", return_value="user_id"):

        r = client.post("/api/projects/abc123/stages/shape/select-name",
                        json={},
                        content_type="application/json")
        assert r.status_code == 400, f"expected 400 got {r.status_code}"

def test_challenge_fix_invalid_stage():
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_jwt_identity", return_value="user_id"):

        r = client.post("/api/projects/abc123/stages/challenge/fix",
                        json={"stage": "launch"},
                        content_type="application/json")
        assert r.status_code == 400, f"expected 400 got {r.status_code}"

def test_challenge_fix_valid_stage_returns_404_not_400():
    """Valid stage but non-existent project should 404, not 400."""
    with patch("app.auth.decorators.verify_jwt_in_request"), \
         patch("app.auth.decorators.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_jwt_identity", return_value="user_id"), \
         patch("app.routes.workflow.get_db") as mock_db:

        mock_db.return_value = MagicMock()
        with patch("app.routes.workflow.get_project", return_value=None):
            r = client.post("/api/projects/nonexistent/stages/challenge/fix",
                            json={"stage": "shape"},
                            content_type="application/json")
            assert r.status_code == 404, f"expected 404 got {r.status_code}"


# ── Health check ──────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# ── Run all ───────────────────────────────────────────────────────────────────

tests = [
    ("workflow generate requires auth",         test_workflow_generate_requires_auth),
    ("workflow approve requires auth",          test_workflow_approve_requires_auth),
    ("workflow edit requires auth",             test_workflow_edit_requires_auth),
    ("agent-runs requires auth",                test_agent_runs_requires_auth),
    ("workflow actions requires auth",          test_workflow_actions_requires_auth),
    ("admin users requires auth",               test_admin_users_requires_auth),
    ("admin role requires auth",                test_admin_role_requires_auth),
    ("admin role invalid value -> 400",         test_admin_role_invalid_value),
    ("admin self-demotion blocked",             test_admin_role_self_demotion_blocked),
    ("edit missing data field -> 400",          test_edit_missing_data_field),
    ("select territory missing -> 400",         test_select_territory_missing_territory),
    ("select name missing -> 400",              test_select_name_missing_name),
    ("challenge fix invalid stage -> 400",      test_challenge_fix_invalid_stage),
    ("challenge fix valid stage no project->404", test_challenge_fix_valid_stage_returns_404_not_400),
    ("health check",                            test_health),
]

print(f"\nRunning {len(tests)} route tests...\n")
for name, fn in tests:
    check(name, fn)

print(f"\n{passed}/{len(tests)} passed" + (" OK" if failed == 0 else f"  {failed} FAILED"))
sys.exit(0 if failed == 0 else 1)

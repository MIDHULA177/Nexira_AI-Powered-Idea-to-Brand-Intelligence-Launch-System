import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.stage_schemas import validate_stage_output, ValidationError

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

# ── Discovery ─────────────────────────────────────────────────────────────────
def test_discovery_valid():
    d = validate_stage_output("discovery", {
        "core_idea": "A platform for students",
        "problem": "Hard to find teammates",
        "context": "University hackathons",
    })
    assert d["core_idea"] == "A platform for students"
    assert d["target_audience"] == []
    assert d["open_questions"] == []

def test_discovery_with_audience():
    d = validate_stage_output("discovery", {
        "core_idea": "idea", "problem": "prob", "context": "ctx",
        "target_audience": [{"segment": "students", "rationale": "main users"}],
    })
    assert len(d["target_audience"]) == 1

def test_discovery_missing_required():
    try:
        validate_stage_output("discovery", {"problem": "only problem"})
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Positioning ───────────────────────────────────────────────────────────────
def test_positioning_valid():
    p = validate_stage_output("positioning", {
        "category": "SaaS", "value_proposition": "vp", "core_benefit": "cb",
        "differentiator": "diff", "positioning_statement": "ps", "rationale": "r",
    })
    assert p["alternatives"] == []

def test_positioning_with_alternatives():
    p = validate_stage_output("positioning", {
        "category": "SaaS", "value_proposition": "vp", "core_benefit": "cb",
        "differentiator": "diff", "positioning_statement": "ps", "rationale": "r",
        "alternatives": [{"direction": "A", "statement": "alt ps"}],
    })
    assert len(p["alternatives"]) == 1

def test_positioning_missing_required():
    try:
        validate_stage_output("positioning", {"category": "SaaS"})
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Shape ─────────────────────────────────────────────────────────────────────
def test_shape_valid():
    s = validate_stage_output("shape", {
        "personality": {"traits": [{"name": "Bold", "rationale": "r"}], "avoid_traits": []},
        "naming": {"territories": [], "candidates": [], "selected_name": None},
        "tagline": "Build your brand.",
        "voice": {
            "description": "confident", "tone": "direct",
            "writing_principles": [], "preferred_words": [],
            "words_to_avoid": [], "example_messaging": "",
        },
    })
    assert s["tagline"] == "Build your brand."

def test_shape_missing_personality():
    try:
        validate_stage_output("shape", {
            "naming": {}, "tagline": "t", "voice": {},
        })
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Visual ────────────────────────────────────────────────────────────────────
def test_visual_valid():
    v = validate_stage_output("visualize", {
        "concept": "modern", "imagery": "clean",
        "composition": "minimal", "logo_direction": "abstract",
        "color_direction": {"primary": "#000", "secondary": [], "accent": [], "rationale": "r"},
        "typography": {"heading_character": "bold", "body_character": "light", "rationale": "r"},
        "visual_rules": {"do": ["whitespace"], "avoid": ["gradients"]},
    })
    assert v["color_direction"]["primary"] == "#000"

def test_visual_missing_color_direction():
    try:
        validate_stage_output("visualize", {
            "concept": "c", "imagery": "i", "composition": "c", "logo_direction": "l",
        })
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Challenge ─────────────────────────────────────────────────────────────────
def test_challenge_valid():
    c = validate_stage_output("challenge", {
        "needs_revision": True,
        "issues": [{"category": "naming", "severity": "medium", "issue": "generic",
                    "evidence": "ev", "suggested_action": "rename"}],
        "strengths": ["clear positioning"],
        "overall_summary": "Mostly good.",
    })
    assert c["needs_revision"] is True
    assert len(c["issues"]) == 1

def test_challenge_auto_needs_revision():
    c = validate_stage_output("challenge", {
        "issues": [{"category": "naming", "severity": "low", "issue": "i",
                    "evidence": "e", "suggested_action": "s"}],
        "strengths": [],
        "overall_summary": "Some issues.",
    })
    assert c["needs_revision"] is True

def test_challenge_missing_summary():
    try:
        validate_stage_output("challenge", {"issues": [], "strengths": []})
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Consistency ───────────────────────────────────────────────────────────────
def test_consistency_valid():
    cs = validate_stage_output("consistency", {
        "score": 0.88,
        "checks": [{"relationship": "Name <> Positioning", "status": "pass",
                    "explanation": "aligned", "recommendation": "none"}],
    })
    assert cs["score"] == 0.88

def test_consistency_invalid_score():
    try:
        validate_stage_output("consistency", {"score": "high", "checks": []})
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Launch ────────────────────────────────────────────────────────────────────
def test_launch_valid():
    l = validate_stage_output("launch", {
        "landing": {"headline": "h", "subheadline": "sh", "cta": "Start",
                    "short_description": "sd", "extended_description": "ed"},
        "social": {"launch_announcement": "la", "short_post": "sp", "caption": "cap"},
        "messaging": {"one_line_pitch": "olp", "elevator_pitch": "ep",
                      "product_description": "pd", "key_points": ["kp1"]},
    })
    assert l["messaging"]["one_line_pitch"] == "olp"

def test_launch_missing_landing():
    try:
        validate_stage_output("launch", {
            "social": {}, "messaging": {},
        })
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Unknown stage ─────────────────────────────────────────────────────────────
def test_unknown_stage():
    try:
        validate_stage_output("unknown_stage", {"data": "x"})
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass

# ── Run all ───────────────────────────────────────────────────────────────────
tests = [
    ("discovery valid",              test_discovery_valid),
    ("discovery with audience",      test_discovery_with_audience),
    ("discovery missing required",   test_discovery_missing_required),
    ("positioning valid",            test_positioning_valid),
    ("positioning with alternatives",test_positioning_with_alternatives),
    ("positioning missing required", test_positioning_missing_required),
    ("shape valid",                  test_shape_valid),
    ("shape missing personality",    test_shape_missing_personality),
    ("visual valid",                 test_visual_valid),
    ("visual missing color",         test_visual_missing_color_direction),
    ("challenge valid",              test_challenge_valid),
    ("challenge auto needs_revision",test_challenge_auto_needs_revision),
    ("challenge missing summary",    test_challenge_missing_summary),
    ("consistency valid",            test_consistency_valid),
    ("consistency invalid score",    test_consistency_invalid_score),
    ("launch valid",                 test_launch_valid),
    ("launch missing landing",       test_launch_missing_landing),
    ("unknown stage",                test_unknown_stage),
]

print(f"\nRunning {len(tests)} schema validation tests...\n")
for name, fn in tests:
    check(name, fn)

print(f"\n{passed}/{len(tests)} passed" + (" OK" if failed == 0 else f"  {failed} FAILED"))
sys.exit(0 if failed == 0 else 1)

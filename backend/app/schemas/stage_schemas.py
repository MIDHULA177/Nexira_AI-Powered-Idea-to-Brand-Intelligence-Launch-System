from typing import Any, Dict, List


class ValidationError(Exception):
    pass


def _require_keys(data: dict, keys: List[str], context: str):
    missing = [k for k in keys if k not in data or data[k] is None]
    if missing:
        raise ValidationError(f"{context}: missing required fields: {missing}")


def _require_list(data: dict, key: str, context: str):
    if not isinstance(data.get(key), list):
        raise ValidationError(f"{context}: '{key}' must be a list")


def _require_dict(data: dict, key: str, context: str):
    if not isinstance(data.get(key), dict):
        raise ValidationError(f"{context}: '{key}' must be an object")


# ── Discovery ────────────────────────────────────────────────────────────────
# README §13: core_idea, problem, target_audience[], needs[], context,
#             constraints[], assumptions[], open_questions[]

def validate_discovery(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "discovery"
    _require_keys(data, ["core_idea", "problem", "context"], ctx)
    for key in ["target_audience", "needs", "constraints", "assumptions", "open_questions"]:
        if key not in data:
            data[key] = []
        if not isinstance(data[key], list):
            data[key] = []
    if data.get("target_audience"):
        for item in data["target_audience"]:
            if not isinstance(item, dict):
                raise ValidationError(f"{ctx}: each target_audience item must be an object")
    return data


# ── Positioning ───────────────────────────────────────────────────────────────
# README §14: category, value_proposition, core_benefit, differentiator,
#             positioning_statement, rationale, alternatives[]

def validate_positioning(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "positioning"
    _require_keys(data, [
        "category", "value_proposition", "core_benefit",
        "differentiator", "positioning_statement", "rationale"
    ], ctx)
    if "alternatives" not in data or not isinstance(data["alternatives"], list):
        data["alternatives"] = []
    return data


# ── Shape ─────────────────────────────────────────────────────────────────────
# README §15–19: personality{traits[], avoid_traits[]},
#                naming{territories[], candidates[], selected_name},
#                tagline, voice{}

def validate_shape(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "shape"
    _require_keys(data, ["personality", "naming", "tagline", "voice"], ctx)

    _require_dict(data, "personality", ctx)
    personality = data["personality"]
    if "traits" not in personality or not isinstance(personality["traits"], list):
        personality["traits"] = []
    if "avoid_traits" not in personality or not isinstance(personality["avoid_traits"], list):
        personality["avoid_traits"] = []

    _require_dict(data, "naming", ctx)
    naming = data["naming"]
    if "territories" not in naming or not isinstance(naming["territories"], list):
        naming["territories"] = []
    if "candidates" not in naming or not isinstance(naming["candidates"], list):
        naming["candidates"] = []
    if "selected_name" not in naming:
        naming["selected_name"] = None

    _require_dict(data, "voice", ctx)
    voice = data["voice"]
    for key in ["description", "tone", "writing_principles", "preferred_words",
                "words_to_avoid", "example_messaging"]:
        if key not in voice:
            voice[key] = [] if key in ["preferred_words", "words_to_avoid",
                                        "writing_principles"] else ""

    return data


# ── Visual ────────────────────────────────────────────────────────────────────
# README §20: concept, color_direction{}, typography{}, imagery,
#             composition, logo_direction, visual_rules{}

def validate_visual(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "visual"
    _require_keys(data, ["concept", "imagery", "composition", "logo_direction"], ctx)

    if "color_direction" not in data or not isinstance(data["color_direction"], dict):
        raise ValidationError(f"{ctx}: 'color_direction' must be an object")
    color = data["color_direction"]
    for key in ["primary", "rationale"]:
        if key not in color:
            color[key] = ""
    for key in ["secondary", "accent"]:
        if key not in color or not isinstance(color[key], list):
            color[key] = []

    if "typography" not in data or not isinstance(data["typography"], dict):
        raise ValidationError(f"{ctx}: 'typography' must be an object")
    typo = data["typography"]
    for key in ["heading_character", "body_character", "rationale"]:
        if key not in typo:
            typo[key] = ""

    if "visual_rules" not in data or not isinstance(data["visual_rules"], dict):
        data["visual_rules"] = {"do": [], "avoid": []}
    rules = data["visual_rules"]
    for key in ["do", "avoid"]:
        if key not in rules or not isinstance(rules[key], list):
            rules[key] = []

    return data


# ── Challenge (Critic) ────────────────────────────────────────────────────────
# README §22: needs_revision, issues[], strengths[], overall_summary

def validate_challenge(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "challenge"
    _require_keys(data, ["overall_summary"], ctx)

    if "needs_revision" not in data:
        data["needs_revision"] = bool(data.get("issues"))
    if not isinstance(data.get("issues"), list):
        data["issues"] = []
    if not isinstance(data.get("strengths"), list):
        data["strengths"] = []

    for issue in data["issues"]:
        if not isinstance(issue, dict):
            raise ValidationError(f"{ctx}: each issue must be an object")
        for key in ["category", "severity", "issue", "evidence", "suggested_action"]:
            if key not in issue:
                issue[key] = ""

    return data


# ── Consistency ───────────────────────────────────────────────────────────────
# README §24: score, checks[]

def validate_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "consistency"
    _require_keys(data, ["score", "checks"], ctx)

    if not isinstance(data["score"], (int, float)):
        raise ValidationError(f"{ctx}: 'score' must be a number")
    if not isinstance(data["checks"], list):
        raise ValidationError(f"{ctx}: 'checks' must be a list")

    for check in data["checks"]:
        if not isinstance(check, dict):
            raise ValidationError(f"{ctx}: each check must be an object")
        for key in ["relationship", "status", "explanation", "recommendation"]:
            if key not in check:
                check[key] = ""

    return data


# ── Launch ────────────────────────────────────────────────────────────────────
# README §25: landing{}, social{}, messaging{}

def validate_launch(data: Dict[str, Any]) -> Dict[str, Any]:
    ctx = "launch"
    _require_keys(data, ["landing", "social", "messaging"], ctx)

    _require_dict(data, "landing", ctx)
    landing = data["landing"]
    for key in ["headline", "subheadline", "cta", "short_description", "extended_description"]:
        if key not in landing:
            landing[key] = ""

    _require_dict(data, "social", ctx)
    social = data["social"]
    for key in ["launch_announcement", "short_post", "caption"]:
        if key not in social:
            social[key] = ""

    _require_dict(data, "messaging", ctx)
    messaging = data["messaging"]
    for key in ["one_line_pitch", "elevator_pitch", "product_description"]:
        if key not in messaging:
            messaging[key] = ""
    if "key_points" not in messaging or not isinstance(messaging["key_points"], list):
        messaging["key_points"] = []

    return data


# ── Registry ──────────────────────────────────────────────────────────────────

VALIDATORS = {
    "discovery":   validate_discovery,
    "positioning": validate_positioning,
    "shape":       validate_shape,
    "visualize":   validate_visual,
    "challenge":   validate_challenge,
    "consistency": validate_consistency,
    "launch":      validate_launch,
}


def validate_stage_output(stage: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalise agent output for a given stage.
    Raises ValidationError if required fields are missing.
    Returns the (possibly normalised) data dict on success.
    """
    validator = VALIDATORS.get(stage)
    if not validator:
        raise ValidationError(f"No validator registered for stage '{stage}'")
    return validator(data)

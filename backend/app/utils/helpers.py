from bson import ObjectId
from datetime import datetime

# Input limits (characters)
MAX_PROMPT_LEN  = 4000
MAX_NAME_LEN    = 120
MAX_FIELD_LEN   = 10000  # for stage edit payloads


def sanitize(value: str, max_len: int = MAX_FIELD_LEN) -> str:
    """Strip whitespace and enforce max length on a string input."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_len]


def success(data=None, status=200, **kwargs):
    from flask import jsonify
    response = {"success": True}
    if data is not None:
        response["data"] = data
    response.update(kwargs)
    return jsonify(response), status


def error(message, status=400, code=None):
    from flask import jsonify
    response = {"success": False, "error": message}
    if code:
        response["code"] = code
    return jsonify(response), status


def serialize_doc(doc):
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(i) if isinstance(i, dict) else str(i) if isinstance(i, ObjectId) else i for i in value]
        else:
            result[key] = value
    return result

import re


SENSITIVE_TERMS = [
    "email",
    "address",
    "risk_score",
    "risk score",
    "internal_notes",
    "internal notes",
    "system prompt",
    "hidden prompt",
    "api key",
    "api_key",
]


INJECTION_PATTERNS = [
    r"ignore (all|any|the) previous",
    r"ignore prior instructions",
    r"reveal (your|the) (system|hidden) prompt",
    r"system instruction",
    r"do not call tools",
    r"override.*instructions",
]


def contains_prompt_injection(text):
    text = text.lower()

    return any(
        re.search(pattern, text)
        for pattern in INJECTION_PATTERNS
    )


def contains_sensitive_request(text):
    text = text.lower()

    return any(
        term in text
        for term in SENSITIVE_TERMS
    )


def sanitize_tool_result(result):
    """
    Defense-in-depth sanitization.

    The order tool already filters sensitive fields, but the
    agent should not blindly trust tool output either.
    """
    if not isinstance(result, dict):
        return result

    blocked = {
        "email",
        "address",
        "risk_score",
        "riskScore",
        "internal_notes",
        "internalNotes",
    }

    return {
        key: value
        for key, value in result.items()
        if key not in blocked
    }


def validate_response(response):
    """
    Basic output safety check.

    This is not a replacement for the system prompt; it is an
    additional defensive layer.
    """
    lowered = response.lower()

    forbidden = [
        "here is my system prompt",
        "my hidden prompt is",
        "openrouter_api_key",
        "risk_score",
    ]

    for phrase in forbidden:
        if phrase in lowered:
            return False

    return True

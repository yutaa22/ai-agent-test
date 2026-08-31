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
    # Classic instruction override attempts.
    r"ignore (all|any|the) previous",
    r"ignore (all|any|the) prior",
    r"ignore previous instructions",
    r"ignore prior instructions",

    # Prompt/system extraction.
    r"reveal (your|the) (system|hidden) prompt",
    r"show (your|the) (system|hidden) prompt",
    r"give me (your|the) (system|hidden) prompt",
    r"system instruction",
    r"hidden instruction",
    r"reveal.*prompt",

    # Instruction manipulation.
    r"do not call tools",
    r"do not use tools",
    r"override.*instructions",
    r"override.*policy",
    r"disregard.*instructions",
    r"disregard.*policy",
    r"bypass.*policy",
    r"follow.*internal note",
    r"follow.*migration note",
    r"treat.*migration.*authoritative",
    r"treat.*internal.*authoritative",
    r"migration note.*override",
    r"internal note.*override",

    # Attempts to elevate untrusted material.
    r"make.*document.*authoritative",
    r"make.*note.*authoritative",
    r"the.*migration.*is.*newer",
    r"the.*internal.*note.*is.*newer",
]


def contains_prompt_injection(text):
    """
    Detect attempts to manipulate the assistant's instruction
    hierarchy.

    This function intentionally errs on the side of detecting
    suspicious instruction-like language. The agent can still
    answer the underlying customer question using authoritative
    policy data.
    """
    if not isinstance(text, str):
        return False

    lowered = text.lower()

    return any(
        re.search(pattern, lowered)
        for pattern in INJECTION_PATTERNS
    )


def contains_sensitive_request(text):
    if not isinstance(text, str):
        return False

    lowered = text.lower()

    return any(
        term in lowered
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
    if not isinstance(response, str):
        return False

    lowered = response.lower()

    forbidden = [
        "here is my system prompt",
        "my hidden prompt is",
        "openrouter_api_key",
        "risk_score",
        "risk score",
    ]

    for phrase in forbidden:
        if phrase in lowered:
            return False

    return True
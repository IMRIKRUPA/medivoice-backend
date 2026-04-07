import re


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_fields(payload, fields):
    missing = []
    for field in fields:
        value = payload.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


def is_valid_email(email):
    return bool(email and EMAIL_PATTERN.match(email))


def is_valid_choice(value, allowed):
    return value in allowed


def parse_bool(value):
    if value is None:
        return None
    return str(value).lower() == "true"


def sanitize_string_list(values):
    if not isinstance(values, list):
        return None
    cleaned = [str(item).strip() for item in values if str(item).strip()]
    return cleaned

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from models import Patient, User
from utils.response import error_response


def generate_token(user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=current_app.config["TOKEN_EXPIRY_HOURS"])
    payload = {
        "user_id": user_id,
        "exp": expires_at,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return error_response("Unauthorized", "UNAUTHORIZED", {}, 401)

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return error_response("Unauthorized", "UNAUTHORIZED", {}, 401)

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return error_response("Unauthorized", "UNAUTHORIZED", {"reason": "Token expired"}, 401)
        except jwt.InvalidTokenError:
            return error_response("Unauthorized", "UNAUTHORIZED", {"reason": "Invalid token"}, 401)

        user = User.query.get(payload.get("user_id"))
        if not user:
            return error_response("Unauthorized", "UNAUTHORIZED", {"reason": "User not found"}, 401)

        patient = Patient.query.filter_by(user_id=user.id).first()
        g.current_user = user
        g.current_patient = patient
        return func(*args, **kwargs)

    return wrapper

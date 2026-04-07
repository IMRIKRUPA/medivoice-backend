from flask import Blueprint, request

from models import Patient, User, db
from utils.auth import generate_token
from utils.response import error_response, success_response
from utils.validation import is_valid_email, require_fields


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["fullName", "email", "password"])
    if missing:
        return error_response("Validation failed", "VALIDATION_ERROR", {"missingFields": missing}, 400)

    if not is_valid_email(payload.get("email")):
        return error_response("Validation failed", "VALIDATION_ERROR", {"field": "email"}, 400)

    existing_user = User.query.filter_by(email=payload["email"].strip().lower()).first()
    if existing_user:
        return error_response("User already exists", "CONFLICT", {"field": "email"}, 409)

    user = User(
        full_name=payload["fullName"].strip(),
        email=payload["email"].strip().lower(),
        phone=payload.get("phone"),
    )
    user.set_password(payload["password"])
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        date_of_birth=payload.get("dateOfBirth"),
        gender=payload.get("gender"),
    )
    db.session.add(patient)
    db.session.commit()

    token = generate_token(user.id)
    return success_response(
        "User registered successfully",
        {
            "token": token,
            "user": user.to_auth_dict(),
            "patient": {
                "id": patient.id,
                "userId": user.id,
                "dateOfBirth": patient.date_of_birth,
                "gender": patient.gender,
            },
        },
        201,
    )


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["email", "password"])
    if missing:
        return error_response("Validation failed", "VALIDATION_ERROR", {"missingFields": missing}, 400)

    user = User.query.filter_by(email=payload["email"].strip().lower()).first()
    if not user or not user.check_password(payload["password"]):
        return error_response("Invalid credentials", "UNAUTHORIZED", {}, 401)

    patient = Patient.query.filter_by(user_id=user.id).first()
    token = generate_token(user.id)
    return success_response(
        "Login successful",
        {
            "token": token,
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "email": user.email,
            },
            "patientId": patient.id if patient else None,
        },
    )

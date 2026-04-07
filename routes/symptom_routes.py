import json

from flask import Blueprint, g, request

from models import Patient, SymptomLog, db
from services.symptom_service import analyze_symptoms
from utils.auth import auth_required
from utils.response import error_response, success_response
from utils.validation import require_fields, sanitize_string_list


symptom_bp = Blueprint("symptoms", __name__, url_prefix="/api/symptoms")


@symptom_bp.post("/analyze")
@auth_required
def analyze():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["patientId", "symptoms"])
    if missing:
        return error_response("Validation failed", "VALIDATION_ERROR", {"missingFields": missing}, 400)

    symptoms = sanitize_string_list(payload.get("symptoms"))
    if not symptoms:
        return error_response("Validation failed", "VALIDATION_ERROR", {"field": "symptoms"}, 400)

    patient = Patient.query.get(payload["patientId"])
    if not patient or patient.id != getattr(g.current_patient, "id", None):
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    analysis = analyze_symptoms(
        symptoms=symptoms,
        duration_days=payload.get("durationDays"),
        severity=payload.get("severity"),
        notes=payload.get("notes"),
    )

    symptom_log = SymptomLog(
        patient_id=patient.id,
        symptoms=json.dumps(symptoms),
        duration_days=payload.get("durationDays"),
        severity=payload.get("severity"),
        condition_category=analysis["conditionCategory"],
        urgency=analysis["urgency"],
        recommendation=analysis["recommendation"],
        specialist_type=analysis["specialistType"],
        notes=payload.get("notes"),
    )
    db.session.add(symptom_log)
    db.session.commit()

    return success_response("Symptoms analyzed successfully", analysis)

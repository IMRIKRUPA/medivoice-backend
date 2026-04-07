from flask import Blueprint, g, request

from models import db
from utils.auth import auth_required
from utils.response import error_response, success_response


patient_bp = Blueprint("patient", __name__, url_prefix="/api/patient")


def _authorize_patient_access(patient_id):
    if not g.current_patient or g.current_patient.id != patient_id:
        return False
    return True


@patient_bp.get("/<int:patient_id>")
@auth_required
def get_patient(patient_id):
    if not _authorize_patient_access(patient_id):
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    return success_response("Patient fetched successfully", g.current_patient.to_profile_dict())


@patient_bp.put("/<int:patient_id>")
@auth_required
def update_patient(patient_id):
    if not _authorize_patient_access(patient_id):
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    payload = request.get_json(silent=True) or {}
    patient = g.current_patient

    field_map = {
        "bloodGroup": "blood_group",
        "heightCm": "height_cm",
        "weightKg": "weight_kg",
        "allergies": "allergies",
        "chronicConditions": "chronic_conditions",
        "currentMedications": "current_medications",
        "emergencyContactName": "emergency_contact_name",
        "emergencyContactPhone": "emergency_contact_phone",
        "address": "address",
        "dateOfBirth": "date_of_birth",
        "gender": "gender",
    }

    for request_field, model_field in field_map.items():
        if request_field in payload:
            setattr(patient, model_field, payload.get(request_field))

    db.session.commit()
    return success_response(
        "Patient updated successfully",
        {
            "id": patient.id,
            "updatedAt": patient.updated_at,
        },
    )

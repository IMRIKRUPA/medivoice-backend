from flask import Blueprint, g, request

from models import Appointment, ChatHistory, Medication, Patient, SymptomLog
from utils.auth import auth_required
from utils.response import error_response, success_response


history_bp = Blueprint("history", __name__, url_prefix="/api/history")


def _resolve_patient(patient_id=None):
    target_id = patient_id or getattr(g.current_patient, "id", None)
    if not target_id:
        return None
    patient = Patient.query.get(target_id)
    if not patient or patient.id != getattr(g.current_patient, "id", None):
        return None
    return patient


@history_bp.get("/chat")
@auth_required
def get_chat_history():
    patient = _resolve_patient(request.args.get("patientId", type=int))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    limit = request.args.get("limit", default=20, type=int)
    history = (
        ChatHistory.query.filter_by(patient_id=patient.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return success_response("Chat history fetched successfully", [item.to_dict() for item in history])


@history_bp.get("/health")
@auth_required
def get_health_history():
    patient = _resolve_patient(request.args.get("patientId", type=int))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    limit = request.args.get("limit", default=20, type=int)
    symptom_logs = (
        SymptomLog.query.filter_by(patient_id=patient.id).order_by(SymptomLog.created_at.desc()).limit(limit).all()
    )
    appointments = (
        Appointment.query.filter_by(patient_id=patient.id)
        .order_by(Appointment.appointment_datetime.desc())
        .limit(limit)
        .all()
    )
    medications = (
        Medication.query.filter_by(patient_id=patient.id).order_by(Medication.created_at.desc()).limit(limit).all()
    )

    return success_response(
        "Health history fetched successfully",
        {
            "symptomLogs": [item.to_history_dict() for item in symptom_logs],
            "appointments": [item.to_history_dict() for item in appointments],
            "medications": [item.to_history_dict() for item in medications],
        },
    )

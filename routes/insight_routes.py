from flask import Blueprint, g, request

from models import Appointment, ChatHistory, Medication, Patient, Reminder, SymptomLog
from services.insight_service import build_insights
from utils.auth import auth_required
from utils.response import error_response, success_response


insight_bp = Blueprint("insights", __name__, url_prefix="/api/insights")


def _resolve_patient(patient_id=None):
    target_id = patient_id or getattr(g.current_patient, "id", None)
    if not target_id:
        return None
    patient = Patient.query.get(target_id)
    if not patient or patient.id != getattr(g.current_patient, "id", None):
        return None
    return patient


@insight_bp.get("")
@auth_required
def get_insights():
    patient = _resolve_patient(request.args.get("patientId", type=int))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    range_value = request.args.get("range", "30d")

    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    symptom_logs = SymptomLog.query.filter_by(patient_id=patient.id).all()
    reminders = Reminder.query.filter_by(patient_id=patient.id).all()
    chat_history = ChatHistory.query.filter_by(patient_id=patient.id).all()
    medications = Medication.query.filter_by(patient_id=patient.id).all()

    data = build_insights(patient, range_value, appointments, symptom_logs, reminders, chat_history, medications)
    return success_response("Insights fetched successfully", data)

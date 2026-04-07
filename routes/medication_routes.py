import json

from flask import Blueprint, g, request

from models import Medication, Patient, Reminder, db
from utils.auth import auth_required
from utils.response import error_response, success_response
from utils.validation import parse_bool, require_fields, sanitize_string_list


medication_bp = Blueprint("medications", __name__, url_prefix="/api/medications")

VALID_STATUSES = {"active", "completed", "stopped"}


def _resolve_patient(patient_id=None):
    target_id = patient_id or getattr(g.current_patient, "id", None)
    if not target_id:
        return None
    patient = Patient.query.get(target_id)
    if not patient or patient.id != getattr(g.current_patient, "id", None):
        return None
    return patient


def _sync_medication_reminders(medication):
    Reminder.query.filter_by(type="medication", reference_id=medication.id).delete()
    for slot in json.loads(medication.time_slots or "[]"):
        reminder = Reminder(
            patient_id=medication.patient_id,
            type="medication",
            reference_id=medication.id,
            title=f"Medication reminder: {medication.name}",
            reminder_time=f"{medication.start_date}T{slot}:00Z",
            status="pending",
        )
        db.session.add(reminder)


@medication_bp.get("")
@auth_required
def list_medications():
    patient = _resolve_patient(request.args.get("patientId", type=int))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    query = Medication.query.filter_by(patient_id=patient.id)
    active_filter = parse_bool(request.args.get("active"))
    if active_filter is True:
        query = query.filter_by(status="active")
    elif active_filter is False:
        query = query.filter(Medication.status != "active")

    medications = query.order_by(Medication.created_at.desc()).all()
    return success_response("Medications fetched successfully", [item.to_dict() for item in medications])


@medication_bp.post("")
@auth_required
def create_medication():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(
        payload,
        ["patientId", "name", "dosage", "frequency", "startDate", "timeSlots"],
    )
    if missing:
        return error_response("Validation failed", "VALIDATION_ERROR", {"missingFields": missing}, 400)

    time_slots = sanitize_string_list(payload.get("timeSlots"))
    if not time_slots:
        return error_response("Validation failed", "VALIDATION_ERROR", {"field": "timeSlots"}, 400)

    patient = _resolve_patient(payload.get("patientId"))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    medication = Medication(
        patient_id=patient.id,
        name=payload["name"],
        dosage=payload["dosage"],
        frequency=payload["frequency"],
        start_date=payload["startDate"],
        end_date=payload.get("endDate"),
        time_slots=json.dumps(time_slots),
        instructions=payload.get("instructions"),
        status="active",
    )
    db.session.add(medication)
    db.session.flush()
    _sync_medication_reminders(medication)
    db.session.commit()

    return success_response("Medication created successfully", {"id": medication.id}, 201)


@medication_bp.put("/<int:medication_id>")
@auth_required
def update_medication(medication_id):
    medication = Medication.query.get(medication_id)
    if not medication or medication.patient_id != getattr(g.current_patient, "id", None):
        return error_response("Medication not found", "NOT_FOUND", {}, 404)

    payload = request.get_json(silent=True) or {}
    if "status" in payload and payload["status"] not in VALID_STATUSES:
        return error_response("Validation failed", "VALIDATION_ERROR", {"field": "status"}, 400)

    if "timeSlots" in payload:
        time_slots = sanitize_string_list(payload.get("timeSlots"))
        if not time_slots:
            return error_response("Validation failed", "VALIDATION_ERROR", {"field": "timeSlots"}, 400)
        medication.time_slots = json.dumps(time_slots)

    field_map = {
        "name": "name",
        "dosage": "dosage",
        "frequency": "frequency",
        "startDate": "start_date",
        "endDate": "end_date",
        "instructions": "instructions",
        "status": "status",
    }
    for request_field, model_field in field_map.items():
        if request_field in payload:
            setattr(medication, model_field, payload.get(request_field))

    _sync_medication_reminders(medication)
    db.session.commit()
    return success_response("Medication updated successfully", {"id": medication.id})

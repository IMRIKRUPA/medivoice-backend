from flask import Blueprint, g, request

from models import Appointment, Patient, Reminder, db
from utils.auth import auth_required
from utils.response import error_response, success_response
from utils.validation import require_fields


appointment_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


VALID_STATUSES = {"scheduled", "completed", "cancelled"}


def _resolve_patient(patient_id=None):
    target_id = patient_id or getattr(g.current_patient, "id", None)
    if not target_id:
        return None
    patient = Patient.query.get(target_id)
    if not patient or patient.id != getattr(g.current_patient, "id", None):
        return None
    return patient


def _sync_appointment_reminder(appointment):
    reminder = Reminder.query.filter_by(type="appointment", reference_id=appointment.id).first()
    if not reminder:
        reminder = Reminder(
            patient_id=appointment.patient_id,
            type="appointment",
            reference_id=appointment.id,
            title=f"Appointment with {appointment.doctor_name}",
            reminder_time=appointment.appointment_datetime,
            status="pending",
        )
        db.session.add(reminder)
    else:
        reminder.title = f"Appointment with {appointment.doctor_name}"
        reminder.reminder_time = appointment.appointment_datetime


@appointment_bp.get("")
@auth_required
def list_appointments():
    patient = _resolve_patient(request.args.get("patientId", type=int))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    query = Appointment.query.filter_by(patient_id=patient.id)
    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    date_filter = request.args.get("date")
    appointments = query.order_by(Appointment.appointment_datetime.asc()).all()
    if date_filter:
        appointments = [item for item in appointments if item.appointment_datetime.startswith(date_filter)]

    return success_response("Appointments fetched successfully", [item.to_dict() for item in appointments])


@appointment_bp.post("")
@auth_required
def create_appointment():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(
        payload,
        ["patientId", "doctorName", "specialistType", "appointmentDateTime"],
    )
    if missing:
        return error_response("Validation failed", "VALIDATION_ERROR", {"missingFields": missing}, 400)

    patient = _resolve_patient(payload.get("patientId"))
    if not patient:
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_name=payload["doctorName"],
        specialist_type=payload["specialistType"],
        appointment_datetime=payload["appointmentDateTime"],
        location=payload.get("location"),
        reason=payload.get("reason"),
        status="scheduled",
        notes=payload.get("notes"),
    )
    db.session.add(appointment)
    db.session.flush()
    _sync_appointment_reminder(appointment)
    db.session.commit()

    return success_response("Appointment created successfully", {"id": appointment.id}, 201)


@appointment_bp.put("/<int:appointment_id>")
@auth_required
def update_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.patient_id != getattr(g.current_patient, "id", None):
        return error_response("Appointment not found", "NOT_FOUND", {}, 404)

    payload = request.get_json(silent=True) or {}
    if "status" in payload and payload["status"] not in VALID_STATUSES:
        return error_response("Validation failed", "VALIDATION_ERROR", {"field": "status"}, 400)

    field_map = {
        "doctorName": "doctor_name",
        "specialistType": "specialist_type",
        "appointmentDateTime": "appointment_datetime",
        "location": "location",
        "reason": "reason",
        "status": "status",
        "notes": "notes",
    }
    for request_field, model_field in field_map.items():
        if request_field in payload:
            setattr(appointment, model_field, payload.get(request_field))

    _sync_appointment_reminder(appointment)
    db.session.commit()
    return success_response("Appointment updated successfully", {"id": appointment.id})


@appointment_bp.delete("/<int:appointment_id>")
@auth_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.patient_id != getattr(g.current_patient, "id", None):
        return error_response("Appointment not found", "NOT_FOUND", {}, 404)

    Reminder.query.filter_by(type="appointment", reference_id=appointment.id).delete()
    db.session.delete(appointment)
    db.session.commit()
    return success_response("Appointment deleted successfully", {"id": appointment_id})

from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_name = db.Column(db.Text, nullable=False)
    specialist_type = db.Column(db.Text, nullable=False)
    appointment_datetime = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text)
    reason = db.Column(db.Text)
    status = db.Column(db.Text, nullable=False, default="scheduled")
    notes = db.Column(db.Text)
    created_at = db.Column(db.Text, nullable=False, default=utc_now)
    updated_at = db.Column(db.Text, nullable=False, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "doctorName": self.doctor_name,
            "specialistType": self.specialist_type,
            "appointmentDateTime": self.appointment_datetime,
            "location": self.location,
            "reason": self.reason,
            "status": self.status,
            "notes": self.notes,
            "createdAt": self.created_at,
        }

    def to_history_dict(self):
        return {
            "id": self.id,
            "doctorName": self.doctor_name,
            "appointmentDateTime": self.appointment_datetime,
            "status": self.status,
        }

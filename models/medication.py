import json
from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    dosage = db.Column(db.Text, nullable=False)
    frequency = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Text, nullable=False)
    end_date = db.Column(db.Text)
    time_slots = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text)
    status = db.Column(db.Text, nullable=False, default="active")
    created_at = db.Column(db.Text, nullable=False, default=utc_now)
    updated_at = db.Column(db.Text, nullable=False, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "timeSlots": json.loads(self.time_slots or "[]"),
            "instructions": self.instructions,
            "status": self.status,
            "createdAt": self.created_at,
        }

    def to_history_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
        }

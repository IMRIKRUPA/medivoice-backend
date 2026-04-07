import json
from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SymptomLog(db.Model):
    __tablename__ = "symptom_logs"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    duration_days = db.Column(db.Integer)
    severity = db.Column(db.Text)
    condition_category = db.Column(db.Text)
    urgency = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    specialist_type = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.Text, nullable=False, default=utc_now)

    def to_history_dict(self):
        return {
            "id": self.id,
            "symptoms": json.loads(self.symptoms or "[]"),
            "urgency": self.urgency,
            "createdAt": self.created_at,
        }

from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    type = db.Column(db.Text, nullable=False)
    reference_id = db.Column(db.Integer)
    title = db.Column(db.Text, nullable=False)
    reminder_time = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, default="pending")
    created_at = db.Column(db.Text, nullable=False, default=utc_now)
    updated_at = db.Column(db.Text, nullable=False, default=utc_now, onupdate=utc_now)

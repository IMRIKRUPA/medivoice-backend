from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    date_of_birth = db.Column(db.Text)
    gender = db.Column(db.Text)
    blood_group = db.Column(db.Text)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    emergency_contact_name = db.Column(db.Text)
    emergency_contact_phone = db.Column(db.Text)
    address = db.Column(db.Text)
    created_at = db.Column(db.Text, nullable=False, default=utc_now)
    updated_at = db.Column(db.Text, nullable=False, default=utc_now, onupdate=utc_now)

    appointments = db.relationship("Appointment", backref="patient", cascade="all, delete-orphan")
    medications = db.relationship("Medication", backref="patient", cascade="all, delete-orphan")
    symptom_logs = db.relationship("SymptomLog", backref="patient", cascade="all, delete-orphan")
    chat_entries = db.relationship("ChatHistory", backref="patient", cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", backref="patient", cascade="all, delete-orphan")

    def to_profile_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "fullName": self.user.full_name if self.user else None,
            "email": self.user.email if self.user else None,
            "phone": self.user.phone if self.user else None,
            "dateOfBirth": self.date_of_birth,
            "gender": self.gender,
            "bloodGroup": self.blood_group,
            "heightCm": self.height_cm,
            "weightKg": self.weight_kg,
            "allergies": self.allergies,
            "chronicConditions": self.chronic_conditions,
            "currentMedications": self.current_medications,
            "emergencyContactName": self.emergency_contact_name,
            "emergencyContactPhone": self.emergency_contact_phone,
            "address": self.address,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }

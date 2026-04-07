import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from models import Appointment, ChatHistory, DailyTip, Medication, Patient, Reminder, SymptomLog, User, db  # noqa: E402


def iso_days_from_now(days, hour=9, minute=0):
    dt = datetime.now(timezone.utc).replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days)
    return dt.isoformat().replace("+00:00", "Z")


def populate_seed_data(force_reset=False):
    os.makedirs(BACKEND_DIR / "database", exist_ok=True)
    if force_reset:
        db.drop_all()
    db.create_all()

    if User.query.first():
        print("Seed skipped: data already exists.")
        return

    users = [
            {
                "full_name": "Aarav Sharma",
                "email": "aarav@example.com",
                "password": "Password123",
                "phone": "+919999999999",
                "patient": {
                    "date_of_birth": "1998-05-14",
                    "gender": "male",
                    "blood_group": "B+",
                    "height_cm": 175,
                    "weight_kg": 72,
                    "allergies": "Penicillin",
                    "chronic_conditions": "Asthma",
                    "current_medications": "Inhaler",
                    "emergency_contact_name": "Riya Sharma",
                    "emergency_contact_phone": "+919888888888",
                    "address": "Mumbai, India",
                },
            },
            {
                "full_name": "Neha Patel",
                "email": "neha@example.com",
                "password": "Password123",
                "phone": "+919777777777",
                "patient": {
                    "date_of_birth": "1995-11-21",
                    "gender": "female",
                    "blood_group": "O+",
                    "height_cm": 162,
                    "weight_kg": 58,
                    "allergies": "None",
                    "chronic_conditions": "Migraine",
                    "current_medications": "Vitamin D",
                    "emergency_contact_name": "Karan Patel",
                    "emergency_contact_phone": "+919666666666",
                    "address": "Pune, India",
                },
            },
            {
                "full_name": "Rohit Verma",
                "email": "rohit@example.com",
                "password": "Password123",
                "phone": "+919555555555",
                "patient": {
                    "date_of_birth": "1989-02-09",
                    "gender": "male",
                    "blood_group": "A+",
                    "height_cm": 180,
                    "weight_kg": 84,
                    "allergies": "Dust",
                    "chronic_conditions": "Hypertension",
                    "current_medications": "Amlodipine",
                    "emergency_contact_name": "Priya Verma",
                    "emergency_contact_phone": "+919444444444",
                    "address": "Delhi, India",
                },
            },
        ]

    created_patients = []
    for user_data in users:
        user = User(
            full_name=user_data["full_name"],
            email=user_data["email"],
            phone=user_data["phone"],
        )
        user.set_password(user_data["password"])
        db.session.add(user)
        db.session.flush()

        patient = Patient(user_id=user.id, **user_data["patient"])
        db.session.add(patient)
        db.session.flush()
        created_patients.append(patient)

    db.session.flush()

    appointments = [
            Appointment(
                patient_id=created_patients[0].id,
                doctor_name="Dr. Mehta",
                specialist_type="General Physician",
                appointment_datetime=iso_days_from_now(3, 9, 30),
                location="City Clinic",
                reason="Fever consultation",
                status="scheduled",
                notes="Carry previous prescription",
            ),
            Appointment(
                patient_id=created_patients[1].id,
                doctor_name="Dr. Kapoor",
                specialist_type="Neurologist",
                appointment_datetime=iso_days_from_now(7, 14, 0),
                location="Metro Hospital",
                reason="Migraine follow-up",
                status="scheduled",
                notes="Check recurring headaches",
            ),
            Appointment(
                patient_id=created_patients[2].id,
                doctor_name="Dr. Singh",
                specialist_type="Cardiologist",
                appointment_datetime=iso_days_from_now(-10, 11, 0),
                location="Heart Care Center",
                reason="Blood pressure review",
                status="completed",
                notes="Continue current medication",
            ),
        ]
    db.session.add_all(appointments)
    db.session.flush()

    medications = [
            Medication(
                patient_id=created_patients[0].id,
                name="Paracetamol",
                dosage="500mg",
                frequency="Twice daily",
                start_date=date.today().isoformat(),
                end_date=(date.today() + timedelta(days=5)).isoformat(),
                time_slots=json.dumps(["09:00", "21:00"]),
                instructions="After food",
                status="active",
            ),
            Medication(
                patient_id=created_patients[1].id,
                name="Vitamin D",
                dosage="1 tablet",
                frequency="Once daily",
                start_date=(date.today() - timedelta(days=3)).isoformat(),
                end_date=(date.today() + timedelta(days=27)).isoformat(),
                time_slots=json.dumps(["08:00"]),
                instructions="Morning after breakfast",
                status="active",
            ),
            Medication(
                patient_id=created_patients[2].id,
                name="Amlodipine",
                dosage="5mg",
                frequency="Once daily",
                start_date=(date.today() - timedelta(days=30)).isoformat(),
                end_date=None,
                time_slots=json.dumps(["20:00"]),
                instructions="Take at the same time every day",
                status="active",
            ),
        ]
    db.session.add_all(medications)
    db.session.flush()

    symptom_logs = [
            SymptomLog(
                patient_id=created_patients[0].id,
                symptoms=json.dumps(["fever", "headache"]),
                duration_days=2,
                severity="medium",
                condition_category="General Infection",
                urgency="medium",
                recommendation="Rest, drink fluids, and monitor fever.",
                specialist_type="General Physician",
                notes="No breathing issues",
            ),
            SymptomLog(
                patient_id=created_patients[1].id,
                symptoms=json.dumps(["headache", "nausea"]),
                duration_days=1,
                severity="low",
                condition_category="Digestive Issue",
                urgency="low",
                recommendation="Monitor symptoms and rest.",
                specialist_type="General Physician",
                notes="Mild nausea",
            ),
            SymptomLog(
                patient_id=created_patients[2].id,
                symptoms=json.dumps(["chest pain"]),
                duration_days=1,
                severity="high",
                condition_category="Possible Emergency",
                urgency="high",
                recommendation="Seek immediate medical help or contact emergency services.",
                specialist_type="Emergency Medicine",
                notes="Intermittent pressure in chest",
            ),
        ]
    db.session.add_all(symptom_logs)

    chat_history = [
            ChatHistory(
                patient_id=created_patients[0].id,
                user_message="I have fever and headache since yesterday",
                bot_reply="Your symptoms may suggest a mild to moderate health concern. Please rest, stay hydrated, and consider a symptom analysis.",
                input_type="text",
                context_type="symptom",
            ),
            ChatHistory(
                patient_id=created_patients[1].id,
                user_message="Can you book a neurologist appointment?",
                bot_reply="I can help you view, schedule, or update an appointment. Please share the doctor type, date, and reason if you want to book one.",
                input_type="text",
                context_type="appointment",
            ),
            ChatHistory(
                patient_id=created_patients[2].id,
                user_message="I feel chest pain and shortness of breath",
                bot_reply="Your symptoms may need urgent medical attention. Please seek emergency care immediately.",
                input_type="voice",
                context_type="emergency",
            ),
        ]
    db.session.add_all(chat_history)

    reminders = [
            Reminder(
                patient_id=created_patients[0].id,
                type="appointment",
                reference_id=appointments[0].id,
                title="Appointment with Dr. Mehta",
                reminder_time=appointments[0].appointment_datetime,
                status="pending",
            ),
            Reminder(
                patient_id=created_patients[0].id,
                type="medication",
                reference_id=medications[0].id,
                title="Medication reminder: Paracetamol",
                reminder_time=iso_days_from_now(0, 9, 0),
                status="sent",
            ),
            Reminder(
                patient_id=created_patients[0].id,
                type="medication",
                reference_id=medications[0].id,
                title="Medication reminder: Paracetamol",
                reminder_time=iso_days_from_now(0, 21, 0),
                status="dismissed",
            ),
            Reminder(
                patient_id=created_patients[1].id,
                type="medication",
                reference_id=medications[1].id,
                title="Medication reminder: Vitamin D",
                reminder_time=iso_days_from_now(-1, 8, 0),
                status="sent",
            ),
            Reminder(
                patient_id=created_patients[2].id,
                type="appointment",
                reference_id=appointments[2].id,
                title="Appointment with Dr. Singh",
                reminder_time=appointments[2].appointment_datetime,
                status="sent",
            ),
        ]
    db.session.add_all(reminders)

    today = date.today()
    tips = [
            DailyTip(
                title="Stay Hydrated",
                tip="Drink enough water during the day to support overall health.",
                category="general",
                date=today.isoformat(),
            ),
            DailyTip(
                title="Move Regularly",
                tip="A short walk each day can improve mood and circulation.",
                category="fitness",
                date=(today + timedelta(days=1)).isoformat(),
            ),
            DailyTip(
                title="Sleep Well",
                tip="Aim for a consistent sleep routine to support recovery and focus.",
                category="wellness",
                date=(today + timedelta(days=2)).isoformat(),
            ),
        ]
    db.session.add_all(tips)

    db.session.commit()
    print("Seed completed successfully.")


if __name__ == "__main__":
    os.environ["AUTO_SEED"] = "false"
    from app import create_app  # noqa: E402

    app = create_app()
    with app.app_context():
        populate_seed_data(force_reset="--reset" in sys.argv)

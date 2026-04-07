import json
from collections import Counter
from datetime import datetime, timedelta, timezone


def _parse_iso(dt_string):
    if not dt_string:
        return None
    if dt_string.endswith("Z"):
        dt_string = dt_string.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_string)


def _date_within_range(dt_string, days):
    parsed = _parse_iso(dt_string)
    if not parsed:
        return False
    now = datetime.now(timezone.utc)
    return parsed >= now - timedelta(days=days)


def build_insights(patient, range_value, appointments, symptom_logs, reminders, chat_history, medications):
    range_to_days = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365,
    }
    days = range_to_days.get(range_value, 30)

    filtered_appointments = [item for item in appointments if _date_within_range(item.appointment_datetime, days)]
    filtered_symptoms = [item for item in symptom_logs if _date_within_range(item.created_at, days)]
    filtered_reminders = [item for item in reminders if _date_within_range(item.created_at, days)]
    filtered_chats = [item for item in chat_history if _date_within_range(item.created_at, 7)]
    filtered_medications = [item for item in medications if _date_within_range(item.created_at, 7)]

    month_counter = Counter()
    for appointment in filtered_appointments:
        parsed = _parse_iso(appointment.appointment_datetime)
        if parsed:
            month_counter[parsed.strftime("%b")] += 1

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    appointments_per_month = [
        {"month": month, "count": month_counter.get(month, 0)}
        for month in month_order
        if month_counter.get(month, 0) > 0
    ][:12]

    symptom_counter = Counter()
    for log in filtered_symptoms:
        for symptom in json.loads(log.symptoms or "[]"):
            symptom_counter[str(symptom).strip().lower()] += 1
    common_symptoms = [
        {"symptom": symptom, "count": count}
        for symptom, count in symptom_counter.most_common()
    ]

    taken = sum(1 for reminder in filtered_reminders if reminder.type == "medication" and reminder.status == "sent")
    missed = sum(1 for reminder in filtered_reminders if reminder.type == "medication" and reminder.status == "dismissed")
    total = taken + missed
    percentage = int(round((taken / total) * 100)) if total else 0
    medication_adherence = {
        "taken": taken,
        "missed": missed,
        "percentage": percentage,
    }

    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_counter = Counter()
    recent_records = filtered_chats + filtered_medications + filtered_symptoms
    recent_records += [item for item in filtered_appointments if _date_within_range(item.created_at, 7)]
    for item in recent_records:
        created_at = getattr(item, "created_at", None)
        parsed = _parse_iso(created_at)
        if parsed:
            weekday_counter[parsed.strftime("%a")] += 1
    weekly_health_activity = [{"day": day, "activityCount": weekday_counter.get(day, 0)} for day in weekday_order]

    return {
        "appointmentsPerMonth": appointments_per_month,
        "commonSymptoms": common_symptoms,
        "medicationAdherence": medication_adherence,
        "weeklyHealthActivity": weekly_health_activity,
    }

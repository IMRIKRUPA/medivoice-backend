from utils.constants import MEDICAL_DISCLAIMER


def _patient_summary(patient):
    if not patient:
        return "No patient record found yet."

    parts = []
    if patient.chronic_conditions:
        parts.append(f"Chronic conditions: {patient.chronic_conditions}.")
    if patient.allergies:
        parts.append(f"Allergies: {patient.allergies}.")
    if patient.current_medications:
        parts.append(f"Current medications: {patient.current_medications}.")
    return " ".join(parts) if parts else "Your patient history is currently limited."


def generate_reply(message, context_type, patient=None):
    text = (message or "").strip()
    lower_text = text.lower()
    requested_context = (context_type or "").lower().strip()

    reply_type = requested_context if requested_context else "unsupported"
    risk_level = "low"
    quick_actions = ["Check Symptoms", "Book Appointment", "View Tips"]
    follow_up_questions = []

    if any(word in lower_text for word in ["hello", "hi", "hey"]):
        reply_type = "greeting"
        reply_text = "Hello, I can help with symptoms, appointments, medications, records, and daily health tips."
        quick_actions = ["Check Symptoms", "Book Appointment", "View Medications"]
    elif requested_context == "symptom" or any(
        word in lower_text
        for word in ["fever", "pain", "cough", "headache", "symptom", "sick", "vomit", "rash"]
    ):
        reply_type = "symptom"
        risk_level = "medium" if any(word in lower_text for word in ["fever", "pain", "vomit"]) else "low"
        if any(word in lower_text for word in ["chest pain", "shortness of breath", "difficulty breathing"]):
            reply_type = "emergency"
            risk_level = "high"
            reply_text = "Your symptoms may need urgent medical attention. Please seek emergency care immediately."
            quick_actions = ["Emergency Check", "Book Appointment", "View History"]
        else:
            reply_text = (
                "Your symptoms may suggest a mild to moderate health concern. Please rest, stay hydrated, and consider a symptom analysis."
            )
            follow_up_questions = ["How long have you had these symptoms?", "Are the symptoms getting worse?"]
            quick_actions = ["Analyze Symptoms", "Book Appointment", "View Tips"]
    elif requested_context == "appointment" or "appointment" in lower_text or "doctor" in lower_text:
        reply_type = "appointment"
        reply_text = "I can help you view, schedule, or update an appointment. Please share the doctor type, date, and reason if you want to book one."
        quick_actions = ["View Appointments", "Schedule Appointment", "View History"]
    elif requested_context == "medication" or any(word in lower_text for word in ["medicine", "medication", "dose", "tablet"]):
        reply_type = "medication"
        reply_text = (
            "I can help track your medications and reminders. For dosage changes or missed-dose advice, please consult your doctor or pharmacist."
        )
        quick_actions = ["View Medications", "Add Medication", "View Tips"]
    elif requested_context == "history" or any(word in lower_text for word in ["history", "record", "medical history"]):
        reply_type = "history"
        reply_text = f"Here is a brief summary from your records: {_patient_summary(patient)}"
        quick_actions = ["View History", "Update Profile", "Check Symptoms"]
    elif requested_context == "insights" or any(word in lower_text for word in ["insight", "dashboard", "report", "summary"]):
        reply_type = "insights"
        reply_text = "I can summarize trends from your appointments, symptoms, medications, and activity. Open the dashboard for chart details."
        quick_actions = ["View Insights", "View History", "View Tips"]
    elif requested_context == "emergency" or "emergency" in lower_text:
        reply_type = "emergency"
        risk_level = "high"
        reply_text = "If you are experiencing severe symptoms, seek immediate medical help or contact emergency services."
        quick_actions = ["Emergency Check", "Book Appointment", "View History"]
    else:
        reply_type = "unsupported"
        reply_text = "I can help with symptoms, appointments, medications, patient records, insights, and health tips."
        quick_actions = ["Check Symptoms", "Book Appointment", "View Tips"]

    return {
        "replyType": reply_type,
        "text": reply_text,
        "quickActions": quick_actions,
        "riskLevel": risk_level,
        "followUpQuestions": follow_up_questions,
        "disclaimer": MEDICAL_DISCLAIMER,
    }

from utils.constants import EMERGENCY_DISCLAIMER, EMERGENCY_SYMPTOMS, SYMPTOM_ANALYSIS_DISCLAIMER


def _normalized_symptoms(symptoms):
    return [symptom.strip().lower() for symptom in symptoms if str(symptom).strip()]


def analyze_symptoms(symptoms, duration_days=None, severity=None, notes=None):
    normalized = _normalized_symptoms(symptoms)
    severity = (severity or "low").lower()
    notes_text = (notes or "").lower()
    combined_text = " ".join(normalized + [notes_text])

    urgency = "low"
    condition_category = "General Wellness"
    recommendation = "Monitor your symptoms and maintain hydration and rest."
    specialist_type = "General Physician"

    if any(keyword in combined_text for keyword in EMERGENCY_SYMPTOMS):
        urgency = "high"
        condition_category = "Possible Emergency"
        recommendation = "Seek immediate medical help or contact emergency services."
        specialist_type = "Emergency Medicine"
    elif any(keyword in combined_text for keyword in ["rash", "itching", "skin irritation"]):
        urgency = "low" if severity == "low" else "medium"
        condition_category = "Skin Concern"
        recommendation = "Avoid irritants, monitor the rash, and consult a doctor if it spreads or worsens."
        specialist_type = "Dermatologist"
    elif any(keyword in combined_text for keyword in ["stomach pain", "vomiting", "nausea", "diarrhea"]):
        urgency = "medium" if severity in {"medium", "high"} else "low"
        condition_category = "Digestive Issue"
        recommendation = "Stay hydrated, eat light meals, and seek medical advice if symptoms persist."
        specialist_type = "General Physician"
    elif any(keyword in combined_text for keyword in ["cough", "fever", "headache", "body ache", "sore throat"]):
        urgency = "medium" if severity in {"medium", "high"} else "low"
        condition_category = "General Infection"
        recommendation = (
            "Rest, drink fluids, monitor symptoms, and consult a doctor if symptoms worsen or do not improve."
        )
        specialist_type = "General Physician"

    if duration_days and duration_days >= 7 and urgency != "high":
        urgency = "medium"
        recommendation = "Symptoms have lasted several days. Please schedule a doctor consultation."

    if severity == "high" and urgency != "high":
        urgency = "medium"

    return {
        "conditionCategory": condition_category,
        "urgency": urgency,
        "recommendation": recommendation,
        "specialistType": specialist_type,
        "disclaimer": SYMPTOM_ANALYSIS_DISCLAIMER,
    }


def check_emergency(symptoms, severity):
    normalized = _normalized_symptoms(symptoms)
    combined_text = " ".join(normalized)
    severity = (severity or "low").lower()

    is_emergency = severity == "high" or any(keyword in combined_text for keyword in EMERGENCY_SYMPTOMS)
    risk_level = "high" if is_emergency else ("medium" if severity == "medium" else "low")
    advice = (
        "Possible emergency symptoms detected. Seek immediate medical help or contact emergency services."
        if is_emergency
        else "No immediate emergency indicators detected. Continue monitoring symptoms and consult a doctor if needed."
    )

    return {
        "isEmergency": is_emergency,
        "riskLevel": risk_level,
        "advice": advice,
        "disclaimer": EMERGENCY_DISCLAIMER,
    }

from flask import Blueprint, g, request

from models import ChatHistory, Patient, db
from services.chatbot_service import generate_reply
from utils.auth import auth_required
from utils.response import error_response, success_response
from utils.validation import require_fields


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.post("/message")
@auth_required
def send_message():
    payload = request.get_json(silent=True) or {}
    missing = require_fields(payload, ["patientId", "message", "inputType", "contextType"])
    if missing:
        return error_response("Validation failed", "VALIDATION_ERROR", {"missingFields": missing}, 400)

    patient = Patient.query.get(payload["patientId"])
    if not patient or patient.id != getattr(g.current_patient, "id", None):
        return error_response("Patient not found", "NOT_FOUND", {}, 404)

    reply = generate_reply(payload["message"], payload["contextType"], patient)
    chat_entry = ChatHistory(
        patient_id=patient.id,
        user_message=payload["message"].strip(),
        bot_reply=reply["text"],
        input_type=payload["inputType"],
        context_type=payload["contextType"],
    )
    db.session.add(chat_entry)
    db.session.commit()

    return success_response(
        "Chat response generated",
        {
            "chatId": chat_entry.id,
            "reply": reply,
            "createdAt": chat_entry.created_at,
        },
    )

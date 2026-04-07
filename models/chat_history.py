from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_reply = db.Column(db.Text, nullable=False)
    input_type = db.Column(db.Text, nullable=False)
    context_type = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "patientId": self.patient_id,
            "userMessage": self.user_message,
            "botReply": self.bot_reply,
            "inputType": self.input_type,
            "contextType": self.context_type,
            "createdAt": self.created_at,
        }

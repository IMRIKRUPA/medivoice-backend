from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


from models.user import User  # noqa: E402,F401
from models.patient import Patient  # noqa: E402,F401
from models.appointment import Appointment  # noqa: E402,F401
from models.medication import Medication  # noqa: E402,F401
from models.symptom_log import SymptomLog  # noqa: E402,F401
from models.chat_history import ChatHistory  # noqa: E402,F401
from models.reminder import Reminder  # noqa: E402,F401
from models.daily_tip import DailyTip  # noqa: E402,F401

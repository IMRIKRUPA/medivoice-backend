from routes.appointment_routes import appointment_bp
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.emergency_routes import emergency_bp
from routes.history_routes import history_bp
from routes.insight_routes import insight_bp
from routes.medication_routes import medication_bp
from routes.patient_routes import patient_bp
from routes.symptom_routes import symptom_bp
from routes.tip_routes import tip_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(symptom_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(medication_bp)
    app.register_blueprint(insight_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(tip_bp)
    app.register_blueprint(emergency_bp)

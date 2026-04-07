from flask import Blueprint, request

from services.symptom_service import check_emergency
from utils.auth import auth_required
from utils.response import error_response, success_response


emergency_bp = Blueprint("emergency", __name__, url_prefix="/api/emergency")


@emergency_bp.get("/check")
@auth_required
def emergency_check():
    symptoms_param = request.args.get("symptoms", "")
    severity = request.args.get("severity")
    if not symptoms_param.strip() or not severity:
        return error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            {"missingFields": ["symptoms", "severity"]},
            400,
        )

    symptoms = [item.strip() for item in symptoms_param.split(",") if item.strip()]
    result = check_emergency(symptoms, severity)
    return success_response("Emergency check completed", result)

from datetime import date

from flask import Blueprint

from models import DailyTip
from utils.auth import auth_required
from utils.response import success_response


tip_bp = Blueprint("tips", __name__, url_prefix="/api/tips")


@tip_bp.get("/daily")
@auth_required
def get_daily_tip():
    today = date.today().isoformat()
    tip = DailyTip.query.filter_by(date=today).first()
    if not tip:
        tip = DailyTip.query.order_by(DailyTip.date.desc()).first()
    return success_response("Daily tip fetched successfully", tip.to_dict() if tip else None)

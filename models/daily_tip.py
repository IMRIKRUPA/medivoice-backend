from datetime import datetime, timezone

from models import db


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class DailyTip(db.Model):
    __tablename__ = "daily_tips"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    tip = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "tip": self.tip,
            "category": self.category,
            "date": self.date,
        }

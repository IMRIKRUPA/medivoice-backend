import os

from flask import Flask
from flask_cors import CORS

from config import Config
from models import User, db
from routes import register_blueprints
from seed.seed_data import populate_seed_data
from utils.response import error_response, success_response


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    db.init_app(app)
    register_blueprints(app)
    register_error_handlers(app)

    @app.route('/')
    def index():
        return success_response("MediVoice AI API is running", {"version": "1.0.0", "endpoints": "/api/..."})

    with app.app_context():
        db.create_all()
        if app.config.get("AUTO_SEED"):
            if not User.query.first():
                populate_seed_data()

    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_error):
        return error_response("Resource not found", "NOT_FOUND", {}, 404)

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return error_response("Method not allowed", "VALIDATION_ERROR", {}, 405)

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return error_response("Internal server error", "SERVER_ERROR", {}, 500)


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=app.config["DEBUG"])

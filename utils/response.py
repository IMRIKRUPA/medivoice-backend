from flask import jsonify


def success_response(message, data=None, status_code=200):
    return (
        jsonify(
            {
                "success": True,
                "message": message,
                "data": data,
                "error": None,
            }
        ),
        status_code,
    )


def error_response(message, code, details=None, status_code=400):
    return (
        jsonify(
            {
                "success": False,
                "message": message,
                "data": None,
                "error": {
                    "code": code,
                    "details": details or {},
                },
            }
        ),
        status_code,
    )

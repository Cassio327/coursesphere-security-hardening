import logging
import os
import re
from functools import wraps

from flask import Flask, Response, current_app, g, jsonify, request
from flask_cors import CORS
from prometheus_client import generate_latest
from werkzeug.middleware.proxy_fix import ProxyFix

from firebase import Firebase
from main import hashFunction
from observability import configure_logging, register_observability
from query_manager import QueryManager
from security import FixedWindowRateLimiter, extract_bearer_token


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
logger = logging.getLogger("coursesphere.api")


def success_response(data, code=200):
    return jsonify(data), code


def error_response(code, message, status):
    return jsonify({"error": {"code": code, "message": message}}), status


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error_response(
            "invalid_json", "Request body must be a JSON object.", 400
        )
    return data, None


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.method == "OPTIONS":
            return current_app.make_default_options_response()

        token = extract_bearer_token(request.headers.get("Authorization"))
        if token is None:
            logger.warning("authentication_failed", extra={"reason": "missing_token"})
            return error_response(
                "authentication_required", "A valid bearer token is required.", 401
            )

        try:
            decoded_token = Firebase.verify_id_token(token)
            user_id = decoded_token.get("uid") if decoded_token else None
            if not user_id:
                raise ValueError("Token does not contain a user identifier")
            g.user_id = user_id
            logger.info("authentication_succeeded", extra={"user_id": user_id})
        except Exception:
            logger.warning("authentication_failed", extra={"reason": "invalid_token"})
            return error_response(
                "invalid_token", "A valid bearer token is required.", 401
            )

        return view(*args, **kwargs)

    return wrapped


def add_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; object-src 'none'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    if current_app.config.get("ENABLE_HSTS"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


def create_app(test_config=None):
    configure_logging()
    application = Flask(__name__)
    application.config.from_mapping(
        MAX_CONTENT_LENGTH=16 * 1024,
        CORS_ALLOWED_ORIGINS=os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:8080,http://127.0.0.1:8080",
        ).split(","),
        ENABLE_HSTS=os.getenv("ENABLE_HSTS", "false").lower() == "true",
        CREATE_USER_RATE_LIMIT=int(os.getenv("CREATE_USER_RATE_LIMIT", "5")),
        CREATE_USER_RATE_WINDOW=int(os.getenv("CREATE_USER_RATE_WINDOW", "60")),
    )
    if test_config:
        application.config.update(test_config)

    if os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true":
        application.wsgi_app = ProxyFix(
            application.wsgi_app, x_for=1, x_proto=1, x_host=1
        )

    CORS(
        application,
        resources={r"/*": {"origins": application.config["CORS_ALLOWED_ORIGINS"]}},
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        methods=["GET", "POST", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )
    register_observability(application)
    application.after_request(add_security_headers)
    application.extensions["create_user_limiter"] = FixedWindowRateLimiter(
        application.config["CREATE_USER_RATE_LIMIT"],
        application.config["CREATE_USER_RATE_WINDOW"],
    )

    @application.errorhandler(413)
    def request_too_large(_error):
        return error_response(
            "payload_too_large", "Request body exceeds the allowed size.", 413
        )

    @application.errorhandler(404)
    def not_found(_error):
        return error_response("not_found", "Resource not found.", 404)

    @application.errorhandler(Exception)
    def unexpected_error(error):
        logger.exception("unhandled_exception", exc_info=error)
        return error_response(
            "internal_error", "An unexpected error occurred.", 500
        )

    @application.get("/health")
    def health():
        return success_response(
            {
                "status": "healthy",
                "service": "coursesphere-backend",
                "instance": os.getenv("INSTANCE_ID", "local"),
            }
        )

    @application.get("/metrics")
    def metrics():
        registry = application.extensions["prometheus_registry"]
        return Response(generate_latest(registry), mimetype="text/plain; version=0.0.4")

    @application.post("/users/create")
    def create_user():
        limiter = application.extensions["create_user_limiter"]
        client_key = request.remote_addr or "unknown"
        if not limiter.allow(client_key):
            logger.warning("rate_limit_exceeded", extra={"route": "/users/create"})
            return error_response(
                "rate_limit_exceeded", "Too many requests. Try again later.", 429
            )

        data, invalid = json_body()
        if invalid:
            return invalid
        email = data.get("email")
        password = data.get("password")
        if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email):
            return error_response("invalid_email", "A valid email is required.", 400)
        if not isinstance(password, str) or not 8 <= len(password) <= 128:
            return error_response(
                "invalid_password",
                "Password length must be between 8 and 128 characters.",
                400,
            )

        try:
            result = Firebase.create_user(email, password)
            logger.info("user_created")
            return success_response(result, 201)
        except Exception as error:
            logger.exception("identity_provider_failure", exc_info=error)
            return error_response(
                "identity_service_unavailable",
                "The identity service is temporarily unavailable.",
                503,
            )

    @application.post("/users/info")
    @authenticated
    def set_user_info():
        data, invalid = json_body()
        if invalid:
            return invalid
        user_info = {
            "majors": data.get("majors", []),
            "minors": data.get("minors", []),
            "courses": data.get("courses", []),
            "college": data.get("college", ""),
            "year": data.get("year", ""),
            "about": data.get("about", ""),
        }
        try:
            Firebase.set_user_info(g.user_id, user_info)
            return success_response({"message": "User info updated successfully."})
        except Exception as error:
            logger.exception("profile_update_failed", exc_info=error)
            return error_response(
                "profile_service_unavailable",
                "Profile information could not be updated.",
                503,
            )

    @application.get("/users/info")
    @authenticated
    def get_user_info():
        try:
            return success_response(Firebase.get_user_info(g.user_id) or {})
        except Exception as error:
            logger.exception("profile_read_failed", exc_info=error)
            return error_response(
                "profile_service_unavailable",
                "Profile information could not be retrieved.",
                503,
            )

    @application.post("/users/query")
    @authenticated
    def get_user_query():
        data, invalid = json_body()
        if invalid:
            return invalid
        query = data.get("query")
        if not isinstance(query, str) or not query.strip() or len(query) > 1000:
            return error_response(
                "invalid_query", "Query must contain between 1 and 1000 characters.", 400
            )

        try:
            user_info = Firebase.get_user_info(g.user_id)
            result = QueryManager(query.strip(), user_info).response
            return success_response(
                {"botResponse": result, "newRecommendations": []}
            )
        except Exception as error:
            logger.exception("query_processing_failed", exc_info=error)
            return error_response(
                "query_service_unavailable",
                "The query could not be processed.",
                503,
            )

    @application.post("/hash")
    @authenticated
    def generate_message_id():
        data, invalid = json_body()
        if invalid:
            return invalid
        return success_response({"messageID": hashFunction(data)})

    @application.post("/chats/<chat_id>/messages")
    @authenticated
    def save_chat(chat_id):
        data, invalid = json_body()
        if invalid:
            return invalid
        messages = data.get("messages", [])
        if not isinstance(messages, list) or len(messages) > 100:
            return error_response(
                "invalid_messages", "Messages must be a list with at most 100 items.", 400
            )
        try:
            Firebase.save_chat(g.user_id, chat_id, messages)
            return success_response({"message": "Messages saved successfully."})
        except Exception as error:
            logger.exception("chat_save_failed", exc_info=error)
            return error_response(
                "chat_service_unavailable", "Messages could not be saved.", 503
            )

    @application.delete("/chats/<chat_id>")
    @authenticated
    def delete_chat(chat_id):
        try:
            Firebase.delete_chat(g.user_id, chat_id)
            return success_response({"message": "Chat deleted successfully."})
        except Exception as error:
            logger.exception("chat_delete_failed", exc_info=error)
            return error_response(
                "chat_service_unavailable", "Chat could not be deleted.", 503
            )

    return application


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )

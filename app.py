"""AI-Powered Grading System - Main Application Module.

This module initializes and configures the Flask application with all necessary
extensions, middleware, and route blueprints.
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_pymongo import PyMongo

from settings import Config
from routes.assignment_templates import assignment_templates_bp
from routes.assignments import assignments_bp
from routes.code_review import code_review_bp
from routes.collaboration import collaboration_bp
from routes.dashboard_api import dashboard_api_bp
from routes.gamification import gamification_bp
from routes.lab_assignments import lab_assignments_bp
from routes.plagiarism_dashboard import plagiarism_dashboard_bp
from routes.progress_tracker import progress_tracker_bp

# Import routes
from routes.simple_auth import simple_auth_bp
from routes.submissions import submissions_bp


def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance with all extensions,
               middleware, and blueprints registered.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Sentry for error monitoring (production)
    if app.config.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=app.config.get("SENTRY_DSN"),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
        )

    # Initialize extensions
    mongo = PyMongo(app)
    mail = Mail(app)
    JWTManager(app)
    CORS(app)

    # Store extensions in app context
    app.mongo = mongo
    app.mail = mail

    # Initialize compression for performance
    try:
        from middleware.compression import init_compression

        init_compression(app)
        app.logger.info("✅ Response compression enabled")
    except ImportError:
        app.logger.warning("Compression middleware not available")

    # Initialize security middleware (ession is cog, CSRF, security headers)
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        from flask_talisman import Talisman

        # CSP Configuration for 10/10 Security - Enhanced
        csp = {
            "default-src": "'self'",
            "script-src": [
                "'self'",
                "'unsafe-inline'",  # Required for inline scripts
                "https://cdn.jsdelivr.net",
                "https://code.jquery.com",
                "https://cdnjs.cloudflare.com",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",  # Required for inline styles
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://fonts.googleapis.com",
            ],
            "font-src": [
                "'self'",
                "https://cdnjs.cloudflare.com",
                "https://fonts.gstatic.com",
            ],
            "img-src": ["'self'", "data:", "https:"],
            "connect-src": "'self'",
            "frame-ancestors": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
            "object-src": "'none'",
            "upgrade-insecure-requests": True,
        }

        # Initialize Talisman (Security Headers) - skip in testing
        if not app.config.get("TESTING"):
            Talisman(
                app,
                content_security_policy=csp,
                force_https=app.config.get("FORCE_HTTPS", False),
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,  # 1 year
                strict_transport_security_include_subdomains=True,
                strict_transport_security_preload=True,
                session_cookie_secure=True,
                session_cookie_http_only=True,
                session_cookie_samesite="Lax",
                force_file_save=False,
                frame_options="DENY",
                frame_options_allow_from=None,
                content_security_policy_nonce_in=["script-src", "style-src"],
                referrer_policy="strict-origin-when-cross-origin",
                feature_policy={
                    "geolocation": "'none'",
                    "microphone": "'none'",
                    "camera": "'none'",
                    "payment": "'none'",
                },
            )
            app.logger.info("✅ Enhanced security headers (Talisman) enabled with HSTS")
        else:
            app.logger.info("⚠️  Security headers (Talisman) disabled for testing")

        # Initialize Rate Limiter
        limiter = Limiter(
            get_remote_address,
            app=app,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=app.config.get("CELERY_BROKER_URL", "memory://"),
        )
        app.limiter = limiter
        app.logger.info("✅ Rate limiting enabled")

    except ImportError as import_error:
        app.logger.warning(
            "Security middleware not available: %s. "
            "Install flask-talisman and flask-limiter.",
            import_error,
        )
        app.limiter = None

    # Setup logging
    logger = app.logger
    try:
        from config.logging_config import setup_logging

        logger = setup_logging(app)
    except (ImportError, AttributeError) as log_error:
        app.logger.warning("Custom logging not available: %s", log_error)

    # Initialize API documentation (Swagger UI)
    try:
        from flask_swagger_ui import get_swaggerui_blueprint

        swagger_url = "/api/docs"
        api_url = "/static/swagger.yaml"
        swaggerui_blueprint = get_swaggerui_blueprint(
            swagger_url, api_url, config={"app_name": "AI Grading System API"}
        )
        app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
    except ImportError:
        app.logger.warning(
            "Swagger UI not available. Install flask-swagger-ui to enable API docs."
        )

    # Register blueprints
    app.register_blueprint(simple_auth_bp, url_prefix="/api/auth")
    app.register_blueprint(assignments_bp, url_prefix="/api/assignments")
    app.register_blueprint(gamification_bp, url_prefix="/api/gamification")
    app.register_blueprint(collaboration_bp, url_prefix="/api/collaboration")
    app.register_blueprint(lab_assignments_bp, url_prefix="/api/lab-assignments")
    app.register_blueprint(dashboard_api_bp, url_prefix="/api/dashboard")
    app.register_blueprint(submissions_bp, url_prefix="/api/submissions")
    app.register_blueprint(progress_tracker_bp, url_prefix="/api/progress-tracker")
    app.register_blueprint(
        assignment_templates_bp, url_prefix="/api/assignment-templates"
    )
    app.register_blueprint(code_review_bp, url_prefix="/api/code-review")
    app.register_blueprint(plagiarism_dashboard_bp, url_prefix="/api/plagiarism")

    # Register API versioning blueprints (health/info endpoints)
    from routes.api_versioning import api_v1, api_v2

    app.register_blueprint(api_v1)
    app.register_blueprint(api_v2)

    # Register v1 API blueprints
    from routes.api_v1.assignments import assignments_v1_bp
    from routes.api_v1.auth import auth_v1_bp
    from routes.api_v1.collaboration import collaboration_v1_bp
    from routes.api_v1.gamification import gamification_v1_bp
    from routes.api_v1.plagiarism import plagiarism_v1_bp
    from routes.api_v1.submissions import submissions_v1_bp

    app.register_blueprint(auth_v1_bp)
    app.register_blueprint(submissions_v1_bp)
    app.register_blueprint(assignments_v1_bp)
    app.register_blueprint(gamification_v1_bp)
    app.register_blueprint(plagiarism_v1_bp)
    app.register_blueprint(collaboration_v1_bp)

    # Register v2 API blueprints (enhanced features)
    from routes.api_v2.analytics import analytics_v2_bp
    from routes.api_v2.assignments import assignments_v2_bp
    from routes.api_v2.auth import auth_v2_bp
    from routes.api_v2.collaboration import collaboration_v2_bp
    from routes.api_v2.gamification import gamification_v2_bp
    from routes.api_v2.plagiarism import plagiarism_v2_bp
    from routes.api_v2.submissions import submissions_v2_bp

    app.register_blueprint(auth_v2_bp)
    app.register_blueprint(submissions_v2_bp)
    app.register_blueprint(assignments_v2_bp)
    app.register_blueprint(gamification_v2_bp)
    app.register_blueprint(plagiarism_v2_bp)
    app.register_blueprint(collaboration_v2_bp)
    app.register_blueprint(analytics_v2_bp)

    # Main routes
    @app.route("/")
    def index():
        """Render the main landing page."""
        return render_template("index.html")

    @app.route("/login")
    def login():
        """Render the login page."""
        return render_template("auth/login.html")

    @app.route("/signup")
    def signup():
        """Render the signup page."""
        return render_template("auth/signup.html")

    @app.route("/student-dashboard")
    def student_dashboard():
        """Render the advanced student dashboard."""
        return render_template("student/advanced_dashboard.html")

    @app.route("/lecturer-dashboard")
    def lecturer_dashboard():
        """Render the advanced lecturer dashboard."""
        return render_template("lecturer/advanced_dashboard.html")

    @app.route("/student-dashboard-simple")
    def student_dashboard_simple():
        """Render the simple student dashboard."""
        return render_template("student/simple_dashboard.html")

    @app.route("/lecturer-dashboard-simple")
    def lecturer_dashboard_simple():
        """Render the simple lecturer dashboard."""
        return render_template("lecturer/simple_dashboard.html")

    @app.route("/assignments")
    def assignments():
        """Render the assignments page."""
        return render_template("student/assignments.html")

    @app.route("/code-editor")
    def code_editor():
        """Render the code editor page."""
        return render_template("student/code_editor.html")

    @app.route("/enhanced-code-editor")
    def enhanced_code_editor():
        """Render the enhanced code editor page."""
        return render_template("student/enhanced_code_editor.html")

    @app.route("/assignment-manager")
    def assignment_manager():
        """Render the assignment manager page."""
        return render_template("lecturer/assignment_manager.html")

    @app.route("/create-assignment")
    def create_assignment():
        """Render the create assignment page."""
        return render_template("lecturer/create_assignment.html")

    @app.route("/manage-assignments")
    def manage_assignments():
        """Render the manage assignments page."""
        return render_template("lecturer/manage_assignments.html")

    @app.route("/view-students")
    def view_students():
        """Render the view students page."""
        return render_template("lecturer/view_students.html")

    @app.route("/analytics")
    def analytics():
        """Render the analytics page."""
        return render_template("lecturer/analytics.html")

    @app.route("/leaderboard")
    def leaderboard():
        """Render the leaderboard page."""
        return render_template("lecturer/leaderboard.html")

    @app.route("/gamification")
    def gamification_dashboard():
        """Render the gamification dashboard."""
        return render_template("student/gamification_dashboard.html")

    @app.route("/collaboration")
    def collaboration_workspace():
        """Render the collaboration workspace."""
        return render_template("student/collaboration_workspace.html")

    @app.route("/lab-assignments")
    def lab_assignments():
        """Render the lab assignments page."""
        return render_template("student/lab_assignments.html")

    @app.route("/progress-tracker")
    def progress_tracker():
        """Render the progress tracker page."""
        return render_template("student/progress_tracker.html")

    @app.route("/assignment-templates")
    def assignment_templates():
        """Render the assignment templates page."""
        return render_template("lecturer/assignment_templates.html")

    @app.route("/code-review")
    def code_review():
        """Render the code review page."""
        return render_template("student/code_review.html")

    @app.route("/plagiarism-dashboard")
    def plagiarism_dashboard():
        """Render the plagiarism dashboard."""
        return render_template("lecturer/plagiarism_dashboard.html")

    @app.route("/admin-panel")
    def admin_panel():
        """Render the admin panel."""
        return render_template("admin/admin_panel.html")

    @app.route("/test")
    def test():
        """Test endpoint to verify API functionality."""
        return jsonify({"status": "working", "message": "API is functional"})

    @app.route("/health")
    def health_check():
        """Health check endpoint for monitoring."""
        from datetime import datetime

        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "AI Grading System is operational",
                "version": "2.0.0",
            }
        )

    @app.errorhandler(404)
    def not_found(_error):
        """Handle 404 errors."""
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error("Internal error: %s", error)
        return render_template("errors/500.html"), 500

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="0.0.0.0", port=5000)

# Create app instance for gunicorn (app:app)
app = create_app()


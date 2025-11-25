from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_pymongo import PyMongo
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
import os

# Import routes
from routes.simple_auth import simple_auth_bp
from routes.gamification import gamification_bp
from routes.collaboration import collaboration_bp
from routes.lab_assignments import lab_assignments_bp
from routes.dashboard_api import dashboard_api_bp
from routes.submissions import submissions_bp
from routes.progress_tracker import progress_tracker_bp
from routes.assignment_templates import assignment_templates_bp
from routes.code_review import code_review_bp
from routes.plagiarism_dashboard import plagiarism_dashboard_bp
# from routes.auth import auth_bp
# from routes.student import student_bp
# from routes.lecturer import lecturer_bp
# from routes.assignments import assignments_bp
# from routes.submissions import submissions_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Sentry for error monitoring (production)
    if app.config.get('SENTRY_DSN'):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(
            dsn=app.config.get('SENTRY_DSN'),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )

    # Initialize extensions
    mongo = PyMongo(app)  # ✅ ENABLED for database persistence
    mail = Mail(app)
    jwt = JWTManager(app)
    CORS(app)

    # Store extensions in app context
    app.mongo = mongo  # ✅ ENABLED
    app.mail = mail

    # Initialize compression for performance (Quick Win)
    try:
        from middleware.compression import init_compression
        compress = init_compression(app)
        app.logger.info("✅ Response compression enabled")
    except ImportError:
        app.logger.warning("Compression middleware not available")

    # Initialize security middleware (rate limiting, CSRF, security headers) - OPTIONAL
    try:
        from middleware.security import init_security, add_security_headers
        security = init_security(app)

        @app.after_request
        def after_request(response):
            return add_security_headers(response)
    except ImportError as e:
        app.logger.warning(f"Security middleware not available: {e}")

    # Setup logging
    try:
        from config.logging_config import setup_logging
        logger = setup_logging(app)
    except Exception as e:
        app.logger.warning(f"Custom logging not available: {e}")
        logger = app.logger

    # Initialize API documentation (Swagger UI) - OPTIONAL
    try:
        from flask_swagger_ui import get_swaggerui_blueprint
        SWAGGER_URL = '/api/docs'
        API_URL = '/static/swagger.yaml'
        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={'app_name': "AI Grading System API"}
        )
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    except ImportError:
        app.logger.warning("Swagger UI not available. Install flask-swagger-ui to enable API docs.")

    # Register blueprints
    app.register_blueprint(simple_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(collaboration_bp, url_prefix='/api/collaboration')
    app.register_blueprint(lab_assignments_bp, url_prefix='/api/lab-assignments')
    app.register_blueprint(dashboard_api_bp, url_prefix='/api/dashboard')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    app.register_blueprint(progress_tracker_bp, url_prefix='/api/progress-tracker')
    app.register_blueprint(assignment_templates_bp, url_prefix='/api/assignment-templates')
    app.register_blueprint(code_review_bp, url_prefix='/api/code-review')
    app.register_blueprint(plagiarism_dashboard_bp, url_prefix='/api/plagiarism')

    # Main routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('auth/login.html')

    @app.route('/signup')
    def signup():
        return render_template('auth/signup.html')

    @app.route('/student-dashboard')
    def student_dashboard():
        return render_template('student/advanced_dashboard.html')

    @app.route('/lecturer-dashboard')
    def lecturer_dashboard():
        return render_template('lecturer/advanced_dashboard.html')

    @app.route('/student-dashboard-simple')
    def student_dashboard_simple():
        return render_template('student/simple_dashboard.html')

    @app.route('/lecturer-dashboard-simple')
    def lecturer_dashboard_simple():
        return render_template('lecturer/simple_dashboard.html')

    @app.route('/assignments')
    def assignments():
        return render_template('student/assignments.html')

    @app.route('/code-editor')
    def code_editor():
        return render_template('student/code_editor.html')

    @app.route('/enhanced-code-editor')
    def enhanced_code_editor():
        return render_template('student/enhanced_code_editor.html')

    @app.route('/assignment-manager')
    def assignment_manager():
        return render_template('lecturer/assignment_manager.html')

    @app.route('/create-assignment')
    def create_assignment():
        return render_template('lecturer/create_assignment.html')

    @app.route('/manage-assignments')
    def manage_assignments():
        return render_template('lecturer/manage_assignments.html')

    @app.route('/view-students')
    def view_students():
        return render_template('lecturer/view_students.html')

    @app.route('/analytics')
    def analytics():
        return render_template('lecturer/analytics.html')

    @app.route('/leaderboard')
    def leaderboard():
        return render_template('lecturer/leaderboard.html')

    @app.route('/gamification')
    def gamification_dashboard():
        return render_template('student/gamification_dashboard.html')

    @app.route('/collaboration')
    def collaboration_workspace():
        return render_template('student/collaboration_workspace.html')

    @app.route('/lab-assignments')
    def lab_assignments():
        return render_template('student/lab_assignments.html')

    @app.route('/progress-tracker')
    def progress_tracker():
        return render_template('student/progress_tracker.html')

    @app.route('/assignment-templates')
    def assignment_templates():
        return render_template('lecturer/assignment_templates.html')

    @app.route('/code-review')
    def code_review():
        return render_template('student/code_review.html')

    @app.route('/plagiarism-dashboard')
    def plagiarism_dashboard():
        return render_template('lecturer/plagiarism_dashboard.html')

    @app.route('/admin-panel')
    def admin_panel():
        return render_template('admin/admin_panel.html')

    @app.route('/test')
    def test():
        return jsonify({'status': 'working', 'message': 'API is functional'})

    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': 'AI Grading System is operational',
            'version': '2.0.0'
        })

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal error: {error}')
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

"""
Logging configuration for the application
"""
import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(app):
    """Configure application logging"""

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set logging level based on environment
    log_level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO

    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)

    # File handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)

    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)

    # Log startup
    app.logger.info(f'Application started at {datetime.now()}')
    app.logger.info(f'Environment: {app.config.get("ENV", "production")}')

    return app.logger

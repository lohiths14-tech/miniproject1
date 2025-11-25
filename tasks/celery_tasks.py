"""
Celery background tasks for asynchronous processing
"""
from celery import Celery
import os

# Initialize Celery
celery = Celery(
    'ai_grading_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery.task(name='tasks.send_email_async')
def send_email_async(recipient, subject, body):
    """
    Send email asynchronously

    Args:
        recipient: Email recipient
        subject: Email subject
        body: Email body (HTML)
    """
    from services.email_service import send_email

    try:
        send_email(recipient, subject, body)
        return {'status': 'sent', 'recipient': recipient}
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}


@celery.task(name='tasks.run_plagiarism_check_async')
def run_plagiarism_check_async(code, assignment_id, student_id, language='python'):
    """
    Run plagiarism check in background

    Args:
        code: Source code to check
        assignment_id: Assignment ID
        student_id: Student ID
        language: Programming language
    """
    from services.plagiarism_service import CrossLanguagePlagiarismDetector

    try:
        detector = CrossLanguagePlagiarismDetector()
        result = detector.check_enhanced_plagiarism(
            code=code,
            assignment_id=assignment_id,
            student_id=student_id,
            language=language
        )
        return result
    except Exception as e:
        return {'error': str(e), 'has_plagiarism': False}


@celery.task(name='tasks.grade_submission_async')
def grade_submission_async(code, test_cases, programming_language='python', user_id=None):
    """
    Grade code submission asynchronously

    Args:
        code: Source code to grade
        test_cases: List of test cases
        programming_language: Programming language
        user_id: User ID for gamification
    """
    from services.ai_grading_service import grade_submission

    try:
        result = grade_submission(
            code=code,
            test_cases=test_cases,
            programming_language=programming_language,
            user_id=user_id
        )
        return result
    except Exception as e:
        return {'error': str(e), 'score': 0}


@celery.task(name='tasks.generate_analytics_report')
def generate_analytics_report(assignment_id):
    """
    Generate comprehensive analytics report for assignment

    Args:
        assignment_id: Assignment ID
    """
    from services.advanced_analytics_service import generate_report

    try:
        report = generate_report(assignment_id)
        return report
    except Exception as e:
        return {'error': str(e)}


@celery.task(name='tasks.cleanup_old_submissions')
def cleanup_old_submissions(days=90):
    """
    Clean up old submission data (runs periodically)

    Args:
        days: Number of days to keep submissions
    """
    from datetime import datetime, timedelta

    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        # Implementation would delete old submissions from database
        return {'status': 'cleaned', 'cutoff_date': cutoff_date.isoformat()}
    except Exception as e:
        return {'error': str(e)}


# Periodic tasks configuration
celery.conf.beat_schedule = {
    'cleanup-old-submissions': {
        'task': 'tasks.cleanup_old_submissions',
        'schedule': 86400.0,  # Run daily
        'args': (90,)  # Keep 90 days
    },
}

"""
API v1 Submissions Blueprint

Wraps existing submission functionality with v1 versioned endpoints.
"""

import json
import os
import uuid
from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request, session

submissions_v1_bp = Blueprint('submissions_v1', __name__, url_prefix='/api/v1/submissions')


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required', 'api_version': '1.0.0', 'version': 'v1'}), 401
        return f(*args, **kwargs)
    return decorated_function


def _add_version_metadata(response_data):
    """Add v1 version metadata to response."""
    response_data['api_version'] = '1.0.0'
    response_data['version'] = 'v1'
    return response_data


def load_submissions():
    """Load submissions from JSON file."""
    submissions_file = 'submissions_data.json'
    if os.path.exists(submissions_file):
        with open(submissions_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_submissions(submissions):
    """Save submissions to JSON file."""
    submissions_file = 'submissions_data.json'
    with open(submissions_file, 'w') as f:
        json.dump(submissions, f, indent=2)


@submissions_v1_bp.route('/submit', methods=['POST'])
@require_auth
def submit_code_v1():
    """Submit code for grading - v1."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify(_add_version_metadata({'error': 'Request body is required'})), 400

        assignment_id = data.get('assignment_id')
        code = data.get('code')
        language = data.get('language', 'python')

        if not assignment_id:
            return jsonify(_add_version_metadata({'error': 'assignment_id is required'})), 400

        if not code or not code.strip():
            return jsonify(_add_version_metadata({'error': 'code is required and cannot be empty'})), 400

        user_id = session.get('user_id')
        user_email = session.get('user_email', f'user_{user_id}@example.com')

        submission_id = str(uuid.uuid4())
        submission = {
            'id': submission_id,
            'submission_id': submission_id,
            'user_id': user_id,
            'student_email': user_email,
            'assignment_id': assignment_id,
            'code': code,
            'language': language,
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'pending',
            'score': None
        }

        submissions = load_submissions()
        submissions.append(submission)
        save_submissions(submissions)

        return jsonify(_add_version_metadata({
            'status': 'success',
            'message': 'Code submitted successfully',
            'id': submission_id,
            'submission_id': submission_id,
            'submitted_at': submission['submitted_at']
        })), 201

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v1_bp.route('/my-submissions', methods=['GET'])
@require_auth
def get_my_submissions_v1():
    """Get submissions for the authenticated user - v1."""
    try:
        user_id = session.get('user_id')
        user_email = session.get('user_email')

        submissions = load_submissions()

        user_submissions = [
            sub for sub in submissions
            if sub.get('user_id') == user_id or sub.get('student_email') == user_email
        ]

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        start = (page - 1) * limit
        end = start + limit
        paginated_submissions = user_submissions[start:end]

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': paginated_submissions,
            'total': len(user_submissions),
            'page': page,
            'limit': limit
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v1_bp.route('/<submission_id>', methods=['GET'])
@require_auth
def get_submission_details_v1(submission_id):
    """Get details of a specific submission - v1."""
    try:
        user_id = session.get('user_id')
        user_email = session.get('user_email')

        submissions = load_submissions()

        submission = next(
            (sub for sub in submissions if sub.get('id') == submission_id or sub.get('submission_id') == submission_id),
            None
        )

        if not submission:
            return jsonify(_add_version_metadata({'error': 'Submission not found'})), 404

        if submission.get('user_id') != user_id and submission.get('student_email') != user_email:
            return jsonify(_add_version_metadata({'error': 'Unauthorized access to this submission'})), 403

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': submission
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v1_bp.route('/<submission_id>/results', methods=['GET'])
@require_auth
def get_submission_results_v1(submission_id):
    """Get grading results for a specific submission - v1."""
    try:
        user_id = session.get('user_id')
        user_email = session.get('user_email')

        submissions = load_submissions()

        submission = next(
            (sub for sub in submissions if sub.get('id') == submission_id or sub.get('submission_id') == submission_id),
            None
        )

        if not submission:
            return jsonify(_add_version_metadata({'error': 'Submission not found'})), 404

        if submission.get('user_id') != user_id and submission.get('student_email') != user_email:
            return jsonify(_add_version_metadata({'error': 'Unauthorized access to this submission'})), 403

        results = {
            'submission_id': submission_id,
            'score': submission.get('score'),
            'status': submission.get('status', 'pending'),
            'feedback': submission.get('feedback'),
            'graded_at': submission.get('graded_at')
        }

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': results
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v1_bp.route('/stats', methods=['GET'])
def get_submission_stats_v1():
    """Get submission statistics - v1."""
    try:
        submissions = load_submissions()

        total = len(submissions)
        graded = len([s for s in submissions if s.get('score') is not None])
        pending = total - graded

        scores = [s['score'] for s in submissions if s['score'] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'total_submissions': total,
                'graded_submissions': graded,
                'pending_submissions': pending,
                'average_score': round(avg_score, 1),
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500

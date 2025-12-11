"""
API v2 Submissions Blueprint

Enhanced submission endpoints with metrics and AI suggestions.
"""

import json
import os
import uuid
from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request, session

submissions_v2_bp = Blueprint('submissions_v2', __name__, url_prefix='/api/v2/submissions')


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required', 'api_version': '2.0.0', 'version': 'v2'}), 401
        return f(*args, **kwargs)
    return decorated_function


def _add_version_metadata(response_data):
    """Add v2 version metadata to response."""
    response_data['api_version'] = '2.0.0'
    response_data['version'] = 'v2'
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


def _analyze_code_metrics(code, language):
    """Analyze code and return metrics (v2 enhanced feature)."""
    lines = code.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]

    # Basic complexity estimation
    complexity_indicators = ['if', 'for', 'while', 'try', 'except', 'with', 'def', 'class']
    complexity = sum(1 for line in lines for indicator in complexity_indicators if indicator in line)

    # Estimate Big O based on nested loops
    nested_loops = 0
    indent_level = 0
    for line in lines:
        if 'for ' in line or 'while ' in line:
            current_indent = len(line) - len(line.lstrip())
            if current_indent > indent_level:
                nested_loops += 1
            indent_level = current_indent

    big_o = 'O(1)'
    if nested_loops >= 2:
        big_o = 'O(n²)'
    elif nested_loops == 1 or any('for ' in l or 'while ' in l for l in lines):
        big_o = 'O(n)'

    return {
        'lines_of_code': len(lines),
        'non_empty_lines': len(non_empty_lines),
        'complexity': min(complexity, 10),
        'big_o': big_o,
        'code_quality': max(1, 10 - complexity // 2),
    }


def _generate_ai_suggestions(code, language):
    """Generate AI suggestions for code improvement (v2 enhanced feature)."""
    suggestions = []

    if len(code) > 500 and 'def ' not in code:
        suggestions.append('Consider breaking down your code into smaller functions for better readability')

    if '# ' not in code:
        suggestions.append('Add comments to explain complex logic')

    if 'try' not in code and 'except' not in code:
        suggestions.append('Consider adding error handling with try/except blocks')

    if not suggestions:
        suggestions.append('Code looks good! Consider adding unit tests')

    return suggestions


@submissions_v2_bp.route('/submit', methods=['POST'])
@require_auth
def submit_code_v2():
    """Submit code for grading - v2 with metrics and AI suggestions."""
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

        # V2: Analyze code metrics
        metrics = _analyze_code_metrics(code, language)
        ai_suggestions = _generate_ai_suggestions(code, language)

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
            'score': None,
            'metrics': metrics,
            'ai_suggestions': ai_suggestions,
        }

        submissions = load_submissions()
        submissions.append(submission)
        save_submissions(submissions)

        return jsonify(_add_version_metadata({
            'status': 'success',
            'message': 'Code submitted successfully',
            'id': submission_id,
            'submission_id': submission_id,
            'submitted_at': submission['submitted_at'],
            'metrics': metrics,
            'ai_suggestions': ai_suggestions,
        })), 201

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v2_bp.route('/my-submissions', methods=['GET'])
@require_auth
def get_my_submissions_v2():
    """Get submissions for the authenticated user - v2 with enhanced data."""
    try:
        user_id = session.get('user_id')
        user_email = session.get('user_email')

        submissions = load_submissions()

        user_submissions = [
            sub for sub in submissions
            if sub.get('user_id') == user_id or sub.get('student_email') == user_email
        ]

        # V2: Add metrics if not present
        for sub in user_submissions:
            if 'metrics' not in sub and sub.get('code'):
                sub['metrics'] = _analyze_code_metrics(sub['code'], sub.get('language', 'python'))

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
            'limit': limit,
            'has_more': end < len(user_submissions),
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v2_bp.route('/<submission_id>', methods=['GET'])
@require_auth
def get_submission_details_v2(submission_id):
    """Get details of a specific submission - v2 with metrics."""
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

        # V2: Add metrics if not present
        if 'metrics' not in submission and submission.get('code'):
            submission['metrics'] = _analyze_code_metrics(submission['code'], submission.get('language', 'python'))
            submission['ai_suggestions'] = _generate_ai_suggestions(submission['code'], submission.get('language', 'python'))

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': submission
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': str(e)})), 500


@submissions_v2_bp.route('/stats', methods=['GET'])
def get_submission_stats_v2():
    """Get submission statistics - v2 with enhanced metrics."""
    try:
        submissions = load_submissions()

        total = len(submissions)
        graded = len([s for s in submissions if s.get('score') is not None])
        pending = total - graded

        scores = [s['score'] for s in submissions if s['score'] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        # V2: Add complexity distribution
        complexities = [s.get('metrics', {}).get('complexity', 0) for s in submissions if s.get('metrics')]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0

        # V2: Language distribution
        languages = {}
        for s in submissions:
            lang = s.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'total_submissions': total,
                'graded_submissions': graded,
                'pending_submissions': pending,
                'average_score': round(avg_score, 1),
                'average_complexity': round(avg_complexity, 1),
                'language_distribution': languages,
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500

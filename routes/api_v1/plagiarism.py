"""
API v1 Plagiarism Blueprint

Wraps existing plagiarism detection functionality with v1 versioned endpoints.
"""

from functools import wraps
from flask import Blueprint, jsonify, request, session

plagiarism_v1_bp = Blueprint('plagiarism_v1', __name__, url_prefix='/api/v1/plagiarism')


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


@plagiarism_v1_bp.route('/scan', methods=['POST'])
@require_auth
def initiate_plagiarism_scan_v1():
    """Initiate plagiarism detection scan - v1."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        scan_data = request.get_json()

        required_fields = ['assignment_id', 'submissions']
        for field in required_fields:
            if field not in scan_data:
                return jsonify(_add_version_metadata({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })), 400

        scan_result = plagiarism_detector.batch_detect_plagiarism(
            scan_data['submissions'],
            scan_data.get('threshold', 0.7),
            scan_data.get('algorithms', ['tfidf', 'structural', 'cross_language']),
        )

        return jsonify(_add_version_metadata({
            'success': True,
            'data': scan_result,
            'message': 'Plagiarism scan completed successfully',
        }))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v1_bp.route('/results/<assignment_id>', methods=['GET'])
@require_auth
def get_plagiarism_results_v1(assignment_id):
    """Get plagiarism detection results for an assignment - v1."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        threshold = request.args.get('threshold', 0.7, type=float)
        sort_by = request.args.get('sort_by', 'similarity_score')
        order = request.args.get('order', 'desc')

        results = plagiarism_detector.get_assignment_results(
            assignment_id, threshold=threshold, sort_by=sort_by, order=order
        )

        return jsonify(_add_version_metadata({'success': True, 'data': results}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v1_bp.route('/compare', methods=['POST'])
@require_auth
def compare_submissions_v1():
    """Compare two specific submissions for plagiarism - v1."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        comparison_data = request.get_json()

        required_fields = ['submission1', 'submission2']
        for field in required_fields:
            if field not in comparison_data:
                return jsonify(_add_version_metadata({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })), 400

        comparison_result = plagiarism_detector.detailed_comparison(
            comparison_data['submission1'],
            comparison_data['submission2'],
            algorithms=comparison_data.get('algorithms', ['all']),
        )

        return jsonify(_add_version_metadata({'success': True, 'data': comparison_result}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v1_bp.route('/dashboard-stats', methods=['GET'])
@require_auth
def get_dashboard_statistics_v1():
    """Get plagiarism dashboard statistics - v1."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        assignment_id = request.args.get('assignment_id')
        time_period = request.args.get('period', '30days')

        stats = plagiarism_detector.get_dashboard_statistics(
            assignment_id=assignment_id, time_period=time_period
        )

        return jsonify(_add_version_metadata({'success': True, 'data': stats}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v1_bp.route('/report/<assignment_id>', methods=['GET'])
@require_auth
def generate_plagiarism_report_v1(assignment_id):
    """Generate comprehensive plagiarism report - v1."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        report_format = request.args.get('format', 'json')
        include_details = request.args.get('details', 'true').lower() == 'true'

        report = plagiarism_detector.generate_comprehensive_report(
            assignment_id, format=report_format, include_details=include_details
        )

        return jsonify(_add_version_metadata({
            'success': True,
            'data': report,
            'format': report_format
        }))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v1_bp.route('/algorithms', methods=['GET'])
@require_auth
def get_available_algorithms_v1():
    """Get available plagiarism detection algorithms - v1."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        algorithms = plagiarism_detector.get_available_algorithms()
        return jsonify(_add_version_metadata({'success': True, 'data': algorithms}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500

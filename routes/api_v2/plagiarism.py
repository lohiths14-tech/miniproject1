"""
API v2 Plagiarism Blueprint

Enhanced plagiarism detection with cross-language support.
"""

from functools import wraps
from flask import Blueprint, jsonify, request, session

plagiarism_v2_bp = Blueprint('plagiarism_v2', __name__, url_prefix='/api/v2/plagiarism')


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


@plagiarism_v2_bp.route('/scan', methods=['POST'])
@require_auth
def initiate_plagiarism_scan_v2():
    """Initiate plagiarism detection scan - v2 with cross-language support."""
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

        # V2: Default to include cross-language detection
        algorithms = scan_data.get('algorithms', ['tfidf', 'structural', 'cross_language', 'semantic'])

        scan_result = plagiarism_detector.batch_detect_plagiarism(
            scan_data['submissions'],
            scan_data.get('threshold', 0.7),
            algorithms,
        )

        # V2: Add scan metadata
        scan_result['scan_metadata'] = {
            'algorithms_used': algorithms,
            'cross_language_enabled': 'cross_language' in algorithms,
            'semantic_analysis_enabled': 'semantic' in algorithms,
        }

        return jsonify(_add_version_metadata({
            'success': True,
            'data': scan_result,
            'message': 'Plagiarism scan completed successfully',
        }))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v2_bp.route('/results/<assignment_id>', methods=['GET'])
@require_auth
def get_plagiarism_results_v2(assignment_id):
    """Get plagiarism detection results - v2 with enhanced analysis."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        threshold = request.args.get('threshold', 0.7, type=float)
        sort_by = request.args.get('sort_by', 'similarity_score')
        order = request.args.get('order', 'desc')
        include_code_snippets = request.args.get('include_snippets', 'true').lower() == 'true'

        results = plagiarism_detector.get_assignment_results(
            assignment_id, threshold=threshold, sort_by=sort_by, order=order
        )

        # V2: Add severity classification
        for result in results.get('matches', []):
            score = result.get('similarity_score', 0)
            if score >= 0.9:
                result['severity'] = 'critical'
            elif score >= 0.7:
                result['severity'] = 'high'
            elif score >= 0.5:
                result['severity'] = 'medium'
            else:
                result['severity'] = 'low'

        return jsonify(_add_version_metadata({'success': True, 'data': results}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v2_bp.route('/compare', methods=['POST'])
@require_auth
def compare_submissions_v2():
    """Compare two submissions - v2 with detailed analysis."""
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

        # V2: Include all algorithms by default
        algorithms = comparison_data.get('algorithms', ['tfidf', 'structural', 'cross_language', 'semantic'])

        comparison_result = plagiarism_detector.detailed_comparison(
            comparison_data['submission1'],
            comparison_data['submission2'],
            algorithms=algorithms,
        )

        # V2: Add recommendation
        avg_score = comparison_result.get('overall_similarity', 0)
        if avg_score >= 0.9:
            comparison_result['recommendation'] = 'Requires immediate investigation'
        elif avg_score >= 0.7:
            comparison_result['recommendation'] = 'Review recommended'
        else:
            comparison_result['recommendation'] = 'No action required'

        return jsonify(_add_version_metadata({'success': True, 'data': comparison_result}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v2_bp.route('/dashboard-stats', methods=['GET'])
@require_auth
def get_dashboard_statistics_v2():
    """Get plagiarism dashboard statistics - v2 with trends."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        assignment_id = request.args.get('assignment_id')
        time_period = request.args.get('period', '30days')

        stats = plagiarism_detector.get_dashboard_statistics(
            assignment_id=assignment_id, time_period=time_period
        )

        # V2: Add trend analysis
        stats['trends'] = {
            'direction': 'stable',
            'change_percentage': 0,
            'period': time_period,
        }

        return jsonify(_add_version_metadata({'success': True, 'data': stats}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v2_bp.route('/cross-language', methods=['POST'])
@require_auth
def cross_language_detection_v2():
    """Cross-language plagiarism detection - v2 only endpoint."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        data = request.get_json()

        if 'submissions' not in data:
            return jsonify(_add_version_metadata({
                'success': False,
                'error': 'Missing required field: submissions'
            })), 400

        # V2: Specialized cross-language detection
        result = plagiarism_detector.batch_detect_plagiarism(
            data['submissions'],
            data.get('threshold', 0.6),
            ['cross_language', 'semantic'],
        )

        result['detection_type'] = 'cross_language'
        result['languages_analyzed'] = list(set(s.get('language', 'unknown') for s in data['submissions']))

        return jsonify(_add_version_metadata({'success': True, 'data': result}))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500


@plagiarism_v2_bp.route('/algorithms', methods=['GET'])
@require_auth
def get_available_algorithms_v2():
    """Get available plagiarism detection algorithms - v2 with descriptions."""
    try:
        from services.plagiarism_service import CrossLanguagePlagiarismDetector
        plagiarism_detector = CrossLanguagePlagiarismDetector()

        algorithms = plagiarism_detector.get_available_algorithms()

        # V2: Add detailed descriptions
        algorithm_details = {
            'tfidf': {
                'name': 'TF-IDF',
                'description': 'Term Frequency-Inverse Document Frequency analysis',
                'best_for': 'Text-based similarity',
                'speed': 'fast',
            },
            'structural': {
                'name': 'Structural Analysis',
                'description': 'AST-based code structure comparison',
                'best_for': 'Code structure similarity',
                'speed': 'medium',
            },
            'cross_language': {
                'name': 'Cross-Language Detection',
                'description': 'Detects plagiarism across different programming languages',
                'best_for': 'Multi-language assignments',
                'speed': 'slow',
            },
            'semantic': {
                'name': 'Semantic Analysis',
                'description': 'Deep semantic understanding of code logic',
                'best_for': 'Logic-based plagiarism',
                'speed': 'slow',
            },
        }

        return jsonify(_add_version_metadata({
            'success': True,
            'data': {
                'algorithms': algorithms,
                'details': algorithm_details,
            }
        }))
    except Exception as e:
        return jsonify(_add_version_metadata({'success': False, 'error': str(e)})), 500

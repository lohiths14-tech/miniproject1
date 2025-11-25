"""
Plagiarism Detection Dashboard API Routes

Provides REST API endpoints for advanced similarity analysis
with detailed reporting and investigation tools.
"""

from flask import Blueprint, request, jsonify, session
from services.plagiarism_service import CrossLanguagePlagiarismDetector
from functools import wraps
import json

plagiarism_dashboard_bp = Blueprint('plagiarism_dashboard', __name__)
plagiarism_detector = CrossLanguagePlagiarismDetector()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@plagiarism_dashboard_bp.route('/scan', methods=['POST'])
@require_auth
def initiate_plagiarism_scan():
    """Initiate plagiarism detection scan"""
    try:
        scan_data = request.get_json()
        
        # Validate required fields
        required_fields = ['assignment_id', 'submissions']
        for field in required_fields:
            if field not in scan_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Process the scan
        scan_result = plagiarism_detector.batch_detect_plagiarism(
            scan_data['submissions'],
            scan_data.get('threshold', 0.7),
            scan_data.get('algorithms', ['tfidf', 'structural', 'cross_language'])
        )
        
        return jsonify({
            'success': True,
            'data': scan_result,
            'message': 'Plagiarism scan completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/results/<assignment_id>', methods=['GET'])
@require_auth
def get_plagiarism_results(assignment_id):
    """Get plagiarism detection results for an assignment"""
    try:
        # Get filter parameters
        threshold = request.args.get('threshold', 0.7, type=float)
        sort_by = request.args.get('sort_by', 'similarity_score')
        order = request.args.get('order', 'desc')
        
        results = plagiarism_detector.get_assignment_results(
            assignment_id,
            threshold=threshold,
            sort_by=sort_by,
            order=order
        )
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/compare', methods=['POST'])
@require_auth
def compare_submissions():
    """Compare two specific submissions for plagiarism"""
    try:
        comparison_data = request.get_json()
        
        required_fields = ['submission1', 'submission2']
        for field in required_fields:
            if field not in comparison_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        comparison_result = plagiarism_detector.detailed_comparison(
            comparison_data['submission1'],
            comparison_data['submission2'],
            algorithms=comparison_data.get('algorithms', ['all'])
        )
        
        return jsonify({
            'success': True,
            'data': comparison_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/heatmap/<submission1_id>/<submission2_id>', methods=['GET'])
@require_auth
def get_similarity_heatmap(submission1_id, submission2_id):
    """Get similarity heatmap data for two submissions"""
    try:
        heatmap_data = plagiarism_detector.generate_similarity_heatmap(
            submission1_id,
            submission2_id
        )
        
        if not heatmap_data:
            return jsonify({
                'success': False,
                'error': 'Submissions not found or comparison not available'
            }), 404
        
        return jsonify({
            'success': True,
            'data': heatmap_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/dashboard-stats', methods=['GET'])
@require_auth
def get_dashboard_statistics():
    """Get plagiarism dashboard statistics"""
    try:
        assignment_id = request.args.get('assignment_id')
        time_period = request.args.get('period', '30days')
        
        stats = plagiarism_detector.get_dashboard_statistics(
            assignment_id=assignment_id,
            time_period=time_period
        )
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/trends', methods=['GET'])
@require_auth
def get_plagiarism_trends():
    """Get plagiarism trends over time"""
    try:
        time_period = request.args.get('period', '6months')
        assignment_id = request.args.get('assignment_id')
        
        trends = plagiarism_detector.get_plagiarism_trends(
            time_period=time_period,
            assignment_id=assignment_id
        )
        
        return jsonify({
            'success': True,
            'data': trends
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/report/<assignment_id>', methods=['GET'])
@require_auth
def generate_plagiarism_report(assignment_id):
    """Generate comprehensive plagiarism report"""
    try:
        report_format = request.args.get('format', 'json')
        include_details = request.args.get('details', 'true').lower() == 'true'
        
        report = plagiarism_detector.generate_comprehensive_report(
            assignment_id,
            format=report_format,
            include_details=include_details
        )
        
        return jsonify({
            'success': True,
            'data': report,
            'format': report_format
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/investigate/<match_id>', methods=['GET'])
@require_auth
def investigate_match(match_id):
    """Get detailed investigation data for a plagiarism match"""
    try:
        investigation_data = plagiarism_detector.investigate_match(match_id)
        
        if not investigation_data:
            return jsonify({
                'success': False,
                'error': 'Match not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': investigation_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/whitelist', methods=['GET'])
@require_auth
def get_whitelist():
    """Get plagiarism detection whitelist"""
    try:
        whitelist = plagiarism_detector.get_whitelist()
        return jsonify({
            'success': True,
            'data': whitelist
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/whitelist', methods=['POST'])
@require_auth
def add_to_whitelist():
    """Add patterns or submissions to whitelist"""
    try:
        whitelist_data = request.get_json()
        
        if 'type' not in whitelist_data or 'value' not in whitelist_data:
            return jsonify({
                'success': False,
                'error': 'Type and value are required'
            }), 400
        
        success = plagiarism_detector.add_to_whitelist(
            whitelist_data['type'],
            whitelist_data['value'],
            whitelist_data.get('reason', '')
        )
        
        return jsonify({
            'success': success,
            'message': 'Added to whitelist successfully' if success else 'Failed to add to whitelist'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/settings', methods=['GET'])
@require_auth
def get_detection_settings():
    """Get plagiarism detection settings"""
    try:
        settings = plagiarism_detector.get_detection_settings()
        return jsonify({
            'success': True,
            'data': settings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/settings', methods=['PUT'])
@require_auth
def update_detection_settings():
    """Update plagiarism detection settings"""
    try:
        settings_data = request.get_json()
        
        success = plagiarism_detector.update_detection_settings(settings_data)
        
        return jsonify({
            'success': success,
            'message': 'Settings updated successfully' if success else 'Failed to update settings'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/algorithms', methods=['GET'])
@require_auth
def get_available_algorithms():
    """Get available plagiarism detection algorithms"""
    try:
        algorithms = plagiarism_detector.get_available_algorithms()
        return jsonify({
            'success': True,
            'data': algorithms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/bulk-scan', methods=['POST'])
@require_auth
def bulk_plagiarism_scan():
    """Perform bulk plagiarism scanning across multiple assignments"""
    try:
        scan_data = request.get_json()
        
        if 'assignment_ids' not in scan_data:
            return jsonify({
                'success': False,
                'error': 'Assignment IDs are required'
            }), 400
        
        bulk_results = plagiarism_detector.bulk_scan_assignments(
            scan_data['assignment_ids'],
            threshold=scan_data.get('threshold', 0.7),
            algorithms=scan_data.get('algorithms', ['tfidf', 'structural'])
        )
        
        return jsonify({
            'success': True,
            'data': bulk_results,
            'message': 'Bulk scan completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@plagiarism_dashboard_bp.route('/export/<assignment_id>', methods=['GET'])
@require_auth
def export_plagiarism_data(assignment_id):
    """Export plagiarism detection data"""
    try:
        export_format = request.args.get('format', 'json')
        include_code = request.args.get('include_code', 'false').lower() == 'true'
        
        export_data = plagiarism_detector.export_plagiarism_data(
            assignment_id,
            format=export_format,
            include_code=include_code
        )
        
        return jsonify({
            'success': True,
            'data': export_data,
            'format': export_format
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

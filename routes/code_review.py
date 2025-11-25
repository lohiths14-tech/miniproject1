"""
Code Review System API Routes

Provides REST API endpoints for peer-to-peer code review workflow
with commenting, approval system, and collaboration features.
"""

from flask import Blueprint, request, jsonify, session
from services.code_review_service import CodeReviewService
from functools import wraps
import json

code_review_bp = Blueprint('code_review', __name__)
review_service = CodeReviewService()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@code_review_bp.route('/reviews', methods=['GET'])
@require_auth
def get_reviews():
    """Get code reviews with optional filtering"""
    try:
        status = request.args.get('status')
        author_id = request.args.get('author_id')
        reviewer_id = request.args.get('reviewer_id')
        assignment_id = request.args.get('assignment_id')
        
        reviews = review_service.get_reviews(
            status=status,
            author_id=author_id,
            reviewer_id=reviewer_id,
            assignment_id=assignment_id
        )
        
        return jsonify({
            'success': True,
            'data': reviews,
            'total': len(reviews)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>', methods=['GET'])
@require_auth
def get_review_details(review_id):
    """Get detailed information about a specific review"""
    try:
        review = review_service.get_review_by_id(review_id)
        if not review:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': review
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews', methods=['POST'])
@require_auth
def create_review_request():
    """Create a new code review request"""
    try:
        review_data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'assignment_id', 'code', 'language']
        for field in required_fields:
            if field not in review_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add author information
        review_data['author_id'] = session.get('user_id', 'unknown')
        review_data['author_name'] = session.get('username', 'Unknown')
        
        new_review = review_service.create_review_request(review_data)
        
        return jsonify({
            'success': True,
            'data': new_review,
            'message': 'Review request created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/assign', methods=['POST'])
@require_auth
def assign_reviewer(review_id):
    """Assign a reviewer to a review request"""
    try:
        assignment_data = request.get_json()
        reviewer_id = assignment_data.get('reviewer_id')
        
        if not reviewer_id:
            return jsonify({
                'success': False,
                'error': 'Reviewer ID is required'
            }), 400
        
        success = review_service.assign_reviewer(review_id, reviewer_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Review not found or already assigned'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Reviewer assigned successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/submit', methods=['POST'])
@require_auth
def submit_review(review_id):
    """Submit a completed code review"""
    try:
        review_data = request.get_json()
        
        # Validate required fields
        required_fields = ['overall_rating', 'feedback']
        for field in required_fields:
            if field not in review_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        review_data['reviewer_id'] = session.get('user_id', 'unknown')
        
        success = review_service.submit_review(review_id, review_data)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Review not found or not assigned to you'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Review submitted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/comments', methods=['GET'])
@require_auth
def get_review_comments(review_id):
    """Get all comments for a specific review"""
    try:
        comments = review_service.get_review_comments(review_id)
        return jsonify({
            'success': True,
            'data': comments
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/comments', methods=['POST'])
@require_auth
def add_review_comment(review_id):
    """Add a comment to a review"""
    try:
        comment_data = request.get_json()
        
        if 'content' not in comment_data:
            return jsonify({
                'success': False,
                'error': 'Comment content is required'
            }), 400
        
        comment_data['author_id'] = session.get('user_id', 'unknown')
        comment_data['author_name'] = session.get('username', 'Unknown')
        
        new_comment = review_service.add_comment(review_id, comment_data)
        if not new_comment:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': new_comment,
            'message': 'Comment added successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/approve', methods=['POST'])
@require_auth
def approve_review(review_id):
    """Approve a code review"""
    try:
        approval_data = request.get_json()
        approver_id = session.get('user_id', 'unknown')
        
        success = review_service.approve_review(review_id, approver_id, approval_data)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Review not found or cannot be approved'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Review approved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/reject', methods=['POST'])
@require_auth
def reject_review(review_id):
    """Reject a code review with feedback"""
    try:
        rejection_data = request.get_json()
        
        if 'reason' not in rejection_data:
            return jsonify({
                'success': False,
                'error': 'Rejection reason is required'
            }), 400
        
        reviewer_id = session.get('user_id', 'unknown')
        
        success = review_service.reject_review(review_id, reviewer_id, rejection_data)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Review not found or cannot be rejected'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Review rejected successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/my-reviews', methods=['GET'])
@require_auth
def get_my_reviews():
    """Get reviews authored by the current user"""
    try:
        user_id = session.get('user_id', 'unknown')
        reviews = review_service.get_user_reviews(user_id, role='author')
        
        return jsonify({
            'success': True,
            'data': reviews
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/assigned-reviews', methods=['GET'])
@require_auth
def get_assigned_reviews():
    """Get reviews assigned to the current user for reviewing"""
    try:
        user_id = session.get('user_id', 'unknown')
        reviews = review_service.get_user_reviews(user_id, role='reviewer')
        
        return jsonify({
            'success': True,
            'data': reviews
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/dashboard-stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Get code review dashboard statistics"""
    try:
        user_id = session.get('user_id', 'unknown')
        stats = review_service.get_user_statistics(user_id)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/templates', methods=['GET'])
@require_auth
def get_review_templates():
    """Get available review templates"""
    try:
        templates = review_service.get_review_templates()
        return jsonify({
            'success': True,
            'data': templates
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/peer-suggestions', methods=['GET'])
@require_auth
def get_peer_suggestions():
    """Get suggested peers for code review"""
    try:
        assignment_id = request.args.get('assignment_id')
        suggestions = review_service.get_peer_suggestions(assignment_id)
        
        return jsonify({
            'success': True,
            'data': suggestions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_review_bp.route('/reviews/<review_id>/metrics', methods=['GET'])
@require_auth
def get_review_metrics(review_id):
    """Get detailed metrics for a specific review"""
    try:
        metrics = review_service.get_review_metrics(review_id)
        if not metrics:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

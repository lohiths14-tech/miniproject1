"""
Assignment Templates Manager API Routes

Provides REST API endpoints for creating, managing, and using
reusable assignment templates with categorization and template library.
"""

from flask import Blueprint, request, jsonify, session
from services.assignment_template_service import AssignmentTemplateService
from functools import wraps
import json

assignment_templates_bp = Blueprint('assignment_templates', __name__)
template_service = AssignmentTemplateService()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@assignment_templates_bp.route('/templates', methods=['GET'])
@require_auth
def get_all_templates():
    """Get all assignment templates with optional filtering"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        language = request.args.get('language')
        search = request.args.get('search')
        
        templates = template_service.get_all_templates(
            category=category,
            difficulty=difficulty,
            language=language,
            search_term=search
        )
        
        return jsonify({
            'success': True,
            'data': templates,
            'total': len(templates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>', methods=['GET'])
@require_auth
def get_template_details(template_id):
    """Get detailed information about a specific template"""
    try:
        template = template_service.get_template_by_id(template_id)
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': template
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates', methods=['POST'])
@require_auth
def create_template():
    """Create a new assignment template"""
    try:
        template_data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'category', 'difficulty', 'language']
        for field in required_fields:
            if field not in template_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add creator information
        template_data['created_by'] = session.get('username', 'Unknown')
        
        new_template = template_service.create_template(template_data)
        
        return jsonify({
            'success': True,
            'data': new_template,
            'message': 'Template created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>', methods=['PUT'])
@require_auth
def update_template(template_id):
    """Update an existing assignment template"""
    try:
        template_data = request.get_json()
        
        updated_template = template_service.update_template(template_id, template_data)
        if not updated_template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': updated_template,
            'message': 'Template updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>', methods=['DELETE'])
@require_auth
def delete_template(template_id):
    """Delete an assignment template"""
    try:
        success = template_service.delete_template(template_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Template deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>/duplicate', methods=['POST'])
@require_auth
def duplicate_template(template_id):
    """Create a duplicate of an existing template"""
    try:
        duplicated_template = template_service.duplicate_template(template_id)
        if not duplicated_template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': duplicated_template,
            'message': 'Template duplicated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>/use', methods=['POST'])
@require_auth
def use_template(template_id):
    """Use a template to create a new assignment"""
    try:
        assignment_data = request.get_json()
        
        new_assignment = template_service.create_assignment_from_template(
            template_id, 
            assignment_data
        )
        
        if not new_assignment:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': new_assignment,
            'message': 'Assignment created from template successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/categories', methods=['GET'])
@require_auth
def get_categories():
    """Get all available template categories"""
    try:
        categories = template_service.get_categories()
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>/rate', methods=['POST'])
@require_auth
def rate_template(template_id):
    """Rate a template"""
    try:
        rating_data = request.get_json()
        rating = rating_data.get('rating')
        
        if not rating or not (1 <= rating <= 5):
            return jsonify({
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }), 400
        
        success = template_service.rate_template(template_id, rating)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'message': 'Template rated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/popular', methods=['GET'])
@require_auth
def get_popular_templates():
    """Get most popular templates based on usage and ratings"""
    try:
        limit = request.args.get('limit', 10, type=int)
        popular_templates = template_service.get_popular_templates(limit)
        
        return jsonify({
            'success': True,
            'data': popular_templates
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/recent', methods=['GET'])
@require_auth
def get_recent_templates():
    """Get recently created or modified templates"""
    try:
        limit = request.args.get('limit', 10, type=int)
        recent_templates = template_service.get_recent_templates(limit)
        
        return jsonify({
            'success': True,
            'data': recent_templates
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/templates/<template_id>/versions', methods=['GET'])
@require_auth
def get_template_versions(template_id):
    """Get version history of a template"""
    try:
        versions = template_service.get_template_versions(template_id)
        if versions is None:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': versions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@assignment_templates_bp.route('/dashboard-stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Get template management dashboard statistics"""
    try:
        stats = template_service.get_template_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

"""
API v1 Assignments Blueprint

Wraps existing assignment functionality with v1 versioned endpoints.
"""

from datetime import datetime
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

assignments_v1_bp = Blueprint('assignments_v1', __name__, url_prefix='/api/v1/assignments')


def _add_version_metadata(response_data):
    """Add v1 version metadata to response."""
    response_data['api_version'] = '1.0.0'
    response_data['version'] = 'v1'
    return response_data


@assignments_v1_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_assignments_v1():
    """Get all active assignments - v1."""
    try:
        from models import Assignment, User

        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user:
            return jsonify(_add_version_metadata({'error': 'User not found'})), 404

        assignments = Assignment.find_all_active()
        assignments_data = [assignment.to_dict() for assignment in assignments]

        return jsonify(_add_version_metadata({'assignments': assignments_data})), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to get assignments: {str(e)}'})), 500


@assignments_v1_bp.route('/<assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_v1(assignment_id):
    """Get a specific assignment - v1."""
    try:
        from models import Assignment

        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify(_add_version_metadata({'error': 'Assignment not found'})), 404

        response = assignment.to_dict()
        return jsonify(_add_version_metadata(response)), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to get assignment: {str(e)}'})), 500


@assignments_v1_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_assignment_v1():
    """Create a new assignment - v1."""
    try:
        from models import Assignment, User
        from services.email_service import send_assignment_notification

        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != 'lecturer':
            return jsonify(_add_version_metadata({'error': 'Access denied. Only lecturers can create assignments'})), 403

        current_user_id = str(user._id)
        data = request.get_json()

        required_fields = ['title', 'description', 'deadline']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(_add_version_metadata({'error': f'{field} is required'})), 400

        try:
            deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify(_add_version_metadata({'error': 'Invalid deadline format. Use ISO format'})), 400

        test_cases = data.get('test_cases', [])
        if not isinstance(test_cases, list):
            return jsonify(_add_version_metadata({'error': 'test_cases must be a list'})), 400

        for i, test_case in enumerate(test_cases):
            if not isinstance(test_case, dict) or 'input' not in test_case or 'expected_output' not in test_case:
                return jsonify(_add_version_metadata({'error': f'Test case {i+1} must have input and expected_output'})), 400

        assignment = Assignment(
            title=data['title'].strip(),
            description=data['description'].strip(),
            created_by=current_user_id,
            deadline=deadline,
            test_cases=test_cases,
            programming_language=data.get('programming_language', 'python'),
            max_score=data.get('max_score', 100),
            starter_code=data.get('starter_code', ''),
            difficulty=data.get('difficulty', 'medium'),
        )

        assignment.save()

        try:
            students = current_app.mongo.db.users.find({'role': 'student', 'is_active': True})
            for student in students:
                send_assignment_notification(
                    student['email'], student['username'], assignment.title, assignment.deadline
                )
        except Exception as e:
            print(f'Failed to send notification emails: {str(e)}')

        return jsonify(_add_version_metadata({
            'message': 'Assignment created successfully',
            'assignment': assignment.to_dict()
        })), 201

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to create assignment: {str(e)}'})), 500


@assignments_v1_bp.route('/<assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment_v1(assignment_id):
    """Update an assignment - v1."""
    try:
        from models import Assignment, User

        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != 'lecturer':
            return jsonify(_add_version_metadata({'error': 'Access denied'})), 403

        current_user_id = str(user._id)
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify(_add_version_metadata({'error': 'Assignment not found'})), 404

        if assignment.created_by != current_user_id:
            return jsonify(_add_version_metadata({'error': 'You can only update your own assignments'})), 403

        data = request.get_json()

        if 'title' in data:
            assignment.title = data['title'].strip()
        if 'description' in data:
            assignment.description = data['description'].strip()
        if 'deadline' in data:
            try:
                assignment.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify(_add_version_metadata({'error': 'Invalid deadline format'})), 400
        if 'test_cases' in data:
            assignment.test_cases = data['test_cases']
        if 'programming_language' in data:
            assignment.programming_language = data['programming_language']
        if 'max_score' in data:
            assignment.max_score = data['max_score']
        if 'starter_code' in data:
            assignment.starter_code = data['starter_code']
        if 'difficulty' in data:
            assignment.difficulty = data['difficulty']
        if 'is_active' in data:
            assignment.is_active = data['is_active']

        assignment.save()

        return jsonify(_add_version_metadata({
            'message': 'Assignment updated successfully',
            'assignment': assignment.to_dict()
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to update assignment: {str(e)}'})), 500


@assignments_v1_bp.route('/<assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment_v1(assignment_id):
    """Delete an assignment - v1."""
    try:
        from models import Assignment, User

        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user or user.role != 'lecturer':
            return jsonify(_add_version_metadata({'error': 'Access denied'})), 403

        current_user_id = str(user._id)
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify(_add_version_metadata({'error': 'Assignment not found'})), 404

        if assignment.created_by != current_user_id:
            return jsonify(_add_version_metadata({'error': 'You can only delete your own assignments'})), 403

        assignment.is_active = False
        assignment.save()

        return jsonify(_add_version_metadata({'message': 'Assignment deleted successfully'})), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to delete assignment: {str(e)}'})), 500

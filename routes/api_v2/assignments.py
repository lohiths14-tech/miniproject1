"""
API v2 Assignments Blueprint

Enhanced assignment endpoints with additional metadata and features.
"""

from datetime import datetime
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

assignments_v2_bp = Blueprint('assignments_v2', __name__, url_prefix='/api/v2/assignments')


def _add_version_metadata(response_data):
    """Add v2 version metadata to response."""
    response_data['api_version'] = '2.0.0'
    response_data['version'] = 'v2'
    return response_data


def _enhance_assignment(assignment_dict):
    """Add v2 enhanced fields to assignment."""
    # Calculate time remaining
    deadline = assignment_dict.get('deadline')
    if deadline:
        try:
            if isinstance(deadline, str):
                deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                deadline_dt = deadline
            time_remaining = (deadline_dt - datetime.now(deadline_dt.tzinfo)).total_seconds()
            assignment_dict['time_remaining_seconds'] = max(0, int(time_remaining))
            assignment_dict['is_overdue'] = time_remaining < 0
        except (ValueError, TypeError):
            assignment_dict['time_remaining_seconds'] = None
            assignment_dict['is_overdue'] = False

    # Add difficulty metadata
    difficulty = assignment_dict.get('difficulty', 'medium')
    difficulty_points = {'easy': 50, 'medium': 100, 'hard': 150}
    assignment_dict['base_points'] = difficulty_points.get(difficulty, 100)

    return assignment_dict


@assignments_v2_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_assignments_v2():
    """Get all active assignments - v2 with enhanced metadata."""
    try:
        from models import Assignment, User

        current_user_email = get_jwt_identity()
        user = User.find_by_email(current_user_email)

        if not user:
            return jsonify(_add_version_metadata({'error': 'User not found'})), 404

        assignments = Assignment.find_all_active()
        assignments_data = [_enhance_assignment(assignment.to_dict()) for assignment in assignments]

        # V2: Add summary statistics
        total = len(assignments_data)
        overdue = len([a for a in assignments_data if a.get('is_overdue')])

        return jsonify(_add_version_metadata({
            'assignments': assignments_data,
            'summary': {
                'total': total,
                'overdue': overdue,
                'active': total - overdue,
            }
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to get assignments: {str(e)}'})), 500


@assignments_v2_bp.route('/<assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_v2(assignment_id):
    """Get a specific assignment - v2 with enhanced metadata."""
    try:
        from models import Assignment

        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify(_add_version_metadata({'error': 'Assignment not found'})), 404

        response = _enhance_assignment(assignment.to_dict())
        return jsonify(_add_version_metadata(response)), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to get assignment: {str(e)}'})), 500


@assignments_v2_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_assignment_v2():
    """Create a new assignment - v2 with enhanced features."""
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
            'assignment': _enhance_assignment(assignment.to_dict())
        })), 201

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to create assignment: {str(e)}'})), 500


@assignments_v2_bp.route('/<assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment_v2(assignment_id):
    """Update an assignment - v2."""
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
            'assignment': _enhance_assignment(assignment.to_dict())
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to update assignment: {str(e)}'})), 500


@assignments_v2_bp.route('/<assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment_v2(assignment_id):
    """Delete an assignment - v2."""
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

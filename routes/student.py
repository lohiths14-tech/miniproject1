from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Assignment, Submission
from bson.objectid import ObjectId

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all active assignments
        assignments = Assignment.find_all_active()
        
        # Get student's submissions
        submissions_data = current_app.mongo.db.submissions.find({'student_id': current_user_id})
        submissions_dict = {}
        for submission in submissions_data:
            submissions_dict[str(submission['assignment_id'])] = submission
        
        # Prepare dashboard data
        dashboard_data = {
            'user': user.to_dict(),
            'assignments': [],
            'recent_submissions': [],
            'statistics': {
                'total_assignments': 0,
                'completed_assignments': 0,
                'average_score': 0,
                'plagiarism_clear': 0
            }
        }
        
        total_score = 0
        completed_count = 0
        plagiarism_clear_count = 0
        
        for assignment in assignments:
            assignment_dict = assignment.to_dict()
            assignment_id = str(assignment._id)
            
            # Check if student has submitted
            if assignment_id in submissions_dict:
                submission = submissions_dict[assignment_id]
                assignment_dict['submission_status'] = 'submitted'
                assignment_dict['score'] = submission.get('score', 0)
                assignment_dict['plagiarism_passed'] = submission.get('plagiarism_passed', True)
                assignment_dict['feedback'] = submission.get('feedback', '')
                assignment_dict['submitted_at'] = submission.get('submitted_at')
                
                completed_count += 1
                total_score += submission.get('score', 0)
                if submission.get('plagiarism_passed', True):
                    plagiarism_clear_count += 1
                    
                dashboard_data['recent_submissions'].append({
                    'assignment_title': assignment.title,
                    'score': submission.get('score', 0),
                    'submitted_at': submission.get('submitted_at'),
                    'plagiarism_passed': submission.get('plagiarism_passed', True)
                })
            else:
                assignment_dict['submission_status'] = 'pending'
                assignment_dict['score'] = None
                assignment_dict['plagiarism_passed'] = None
                assignment_dict['feedback'] = ''
            
            dashboard_data['assignments'].append(assignment_dict)
        
        # Calculate statistics
        dashboard_data['statistics']['total_assignments'] = len(assignments)
        dashboard_data['statistics']['completed_assignments'] = completed_count
        dashboard_data['statistics']['average_score'] = total_score / completed_count if completed_count > 0 else 0
        dashboard_data['statistics']['plagiarism_clear'] = plagiarism_clear_count
        
        # Sort recent submissions by date
        dashboard_data['recent_submissions'].sort(key=lambda x: x['submitted_at'], reverse=True)
        dashboard_data['recent_submissions'] = dashboard_data['recent_submissions'][:5]  # Last 5 submissions
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard data: {str(e)}'}), 500

@student_bp.route('/assignments/<assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_details(assignment_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Access denied'}), 403
        
        assignment = Assignment.find_by_id(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404
        
        # Get student's submission if exists
        submission = Submission.find_by_student_and_assignment(current_user_id, assignment_id)
        
        assignment_data = assignment.to_dict()
        if submission:
            assignment_data['submission'] = submission.to_dict()
        else:
            assignment_data['submission'] = None
        
        return jsonify(assignment_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get assignment details: {str(e)}'}), 500

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_student_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get submission statistics
        submissions_data = list(current_app.mongo.db.submissions.find({'student_id': current_user_id}))
        
        profile_data = user.to_dict()
        profile_data['statistics'] = {
            'total_submissions': len(submissions_data),
            'average_score': sum(s.get('score', 0) for s in submissions_data) / len(submissions_data) if submissions_data else 0,
            'best_score': max((s.get('score', 0) for s in submissions_data), default=0),
            'plagiarism_violations': sum(1 for s in submissions_data if not s.get('plagiarism_passed', True))
        }
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500
"""
Submissions API Routes
Handles code submissions and displays them in teacher dashboard
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import os

# Create blueprint
submissions_bp = Blueprint('submissions', __name__)

# Simple file-based storage for submissions
SUBMISSIONS_FILE = 'submissions_data.json'

def load_submissions():
    """Load submissions from file"""
    try:
        if os.path.exists(SUBMISSIONS_FILE):
            with open(SUBMISSIONS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_submissions(submissions):
    """Save submissions to file"""
    try:
        with open(SUBMISSIONS_FILE, 'w') as f:
            json.dump(submissions, f, indent=2)
    except Exception as e:
        print(f"Error saving submissions: {e}")

@submissions_bp.route('/submit', methods=['POST'])
def submit_assignment():
    """Submit assignment code"""
    try:
        data = request.get_json()
        
        # Extract submission data
        student_name = data.get('student_name', 'Anonymous Student')
        student_email = data.get('student_email', 'student@example.com')
        assignment_title = data.get('assignment_title', 'Code Submission')
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        # Create submission record
        submission = {
            'id': f"sub_{int(datetime.now().timestamp())}",
            'student_name': student_name,
            'student_email': student_email,
            'assignment_title': assignment_title,
            'code': code,
            'language': language,
            'submitted_at': datetime.now().isoformat(),
            'status': 'pending',
            'score': None,
            'feedback': None
        }
        
        # Load existing submissions
        submissions = load_submissions()
        
        # Add new submission
        submissions.insert(0, submission)  # Add to beginning for recent first
        
        # Keep only last 50 submissions
        submissions = submissions[:50]
        
        # Save updated submissions
        save_submissions(submissions)
        
        # Simulate AI grading
        from services.ai_grading_service import grade_submission
        test_cases = [
            {'input': '5', 'expected_output': '120'},
            {'input': '3', 'expected_output': '6'}
        ]
        
        grading_result = grade_submission(code, test_cases, language)
        
        # Update submission with grading result
        submission['status'] = 'graded'
        submission['score'] = grading_result.get('score', 0)
        submission['feedback'] = grading_result.get('feedback', 'No feedback available')
        submission['test_results'] = grading_result.get('test_results', [])
        
        # Save with grading results
        submissions[0] = submission
        save_submissions(submissions)
        
        return jsonify({
            'status': 'success',
            'message': 'Assignment submitted successfully',
            'data': {
                'submission_id': submission['id'],
                'score': submission['score'],
                'feedback': submission['feedback'],
                'submitted_at': submission['submitted_at']
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@submissions_bp.route('/recent', methods=['GET'])
def get_recent_submissions():
    """Get recent submissions for teacher dashboard"""
    try:
        submissions = load_submissions()
        
        # Format submissions for display
        formatted_submissions = []
        for sub in submissions[:10]:  # Last 10 submissions
            formatted_submissions.append({
                'id': sub['id'],
                'student': sub['student_name'],
                'assignment': sub['assignment_title'],
                'submitted': _time_ago(sub['submitted_at']),
                'status': sub['status'],
                'score': sub['score'],
                'language': sub['language']
            })
        
        return jsonify({
            'status': 'success',
            'data': formatted_submissions
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@submissions_bp.route('/view/<submission_id>', methods=['GET'])
def view_submission(submission_id):
    """View detailed submission"""
    try:
        submissions = load_submissions()
        
        # Find submission
        submission = None
        for sub in submissions:
            if sub['id'] == submission_id:
                submission = sub
                break
        
        if not submission:
            return jsonify({
                'status': 'error',
                'message': 'Submission not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': submission
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@submissions_bp.route('/grade/<submission_id>', methods=['POST'])
def grade_specific_submission(submission_id):
    """Grade a specific submission"""
    try:
        submissions = load_submissions()
        
        # Find and update submission
        for i, sub in enumerate(submissions):
            if sub['id'] == submission_id:
                # Re-grade the submission
                from services.ai_grading_service import grade_submission
                test_cases = [
                    {'input': '5', 'expected_output': '120'},
                    {'input': '3', 'expected_output': '6'}
                ]
                
                grading_result = grade_submission(sub['code'], test_cases, sub['language'])
                
                # Update submission
                submissions[i]['status'] = 'graded'
                submissions[i]['score'] = grading_result.get('score', 0)
                submissions[i]['feedback'] = grading_result.get('feedback', 'No feedback available')
                submissions[i]['graded_at'] = datetime.now().isoformat()
                
                save_submissions(submissions)
                
                return jsonify({
                    'status': 'success',
                    'data': {
                        'submission_id': submission_id,
                        'score': submissions[i]['score'],
                        'feedback': submissions[i]['feedback']
                    }
                })
        
        return jsonify({
            'status': 'error',
            'message': 'Submission not found'
        }), 404
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@submissions_bp.route('/bulk-grade', methods=['POST'])
def bulk_grade_submissions():
    """Grade multiple submissions"""
    try:
        data = request.get_json()
        submission_ids = data.get('submission_ids', [])
        
        submissions = load_submissions()
        graded_count = 0
        
        for submission_id in submission_ids:
            for i, sub in enumerate(submissions):
                if sub['id'] == submission_id and sub['status'] == 'pending':
                    # Grade the submission
                    from services.ai_grading_service import grade_submission
                    test_cases = [
                        {'input': '5', 'expected_output': '120'},
                        {'input': '3', 'expected_output': '6'}
                    ]
                    
                    grading_result = grade_submission(sub['code'], test_cases, sub['language'])
                    
                    # Update submission
                    submissions[i]['status'] = 'graded'
                    submissions[i]['score'] = grading_result.get('score', 0)
                    submissions[i]['feedback'] = grading_result.get('feedback', 'No feedback available')
                    submissions[i]['graded_at'] = datetime.now().isoformat()
                    graded_count += 1
                    break
        
        save_submissions(submissions)
        
        return jsonify({
            'status': 'success',
            'data': {
                'graded_count': graded_count,
                'message': f'Successfully graded {graded_count} submissions'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@submissions_bp.route('/stats', methods=['GET'])
def get_submission_stats():
    """Get submission statistics"""
    try:
        submissions = load_submissions()
        
        total = len(submissions)
        graded = len([s for s in submissions if s['status'] == 'graded'])
        pending = len([s for s in submissions if s['status'] == 'pending'])
        
        # Calculate average score
        scores = [s['score'] for s in submissions if s['score'] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_submissions': total,
                'graded_submissions': graded,
                'pending_submissions': pending,
                'average_score': round(avg_score, 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@submissions_bp.route('/student/<student_email>', methods=['GET'])
def get_student_submissions(student_email):
    """Get submissions for a specific student"""
    try:
        submissions = load_submissions()
        
        # Filter submissions for this student
        student_submissions = [
            sub for sub in submissions 
            if sub['student_email'] == student_email
        ]
        
        return jsonify({
            'status': 'success',
            'data': student_submissions
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def _time_ago(timestamp_str):
    """Convert timestamp to 'time ago' format"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Recently"
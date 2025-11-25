"""
Lab Assignment API Routes
Handles automated grading and feedback for engineering curriculum exercises
"""

from flask import Blueprint, request, jsonify, session
from services.lab_grading_service import lab_grading_service, LabType, LabAssignment
from services.gamification_service import gamification_service
from datetime import datetime
import json

lab_assignments_bp = Blueprint('lab_assignments', __name__)

@lab_assignments_bp.route('/submit', methods=['POST'])
def submit_lab_assignment():
    """Submit lab assignment for automated grading"""
    try:
        data = request.get_json()
        
        # Extract submission data
        code = data.get('code', '')
        assignment_id = data.get('assignment_id')
        student_id = data.get('student_id') or session.get('user_id', 'demo_student')
        language = data.get('language', 'python')
        
        if not code or not assignment_id:
            return jsonify({
                'status': 'error',
                'message': 'Code and assignment ID are required'
            }), 400
        
        # Create assignment from template or database
        assignment = _get_assignment_config(assignment_id)
        if not assignment:
            return jsonify({
                'status': 'error',
                'message': 'Assignment not found'
            }), 404
        
        # Evaluate submission
        feedback = lab_grading_service.evaluate_lab_submission(
            code=code,
            assignment=assignment,
            student_id=student_id,
            language=language
        )
        
        # Award gamification points
        gamification_result = gamification_service.award_points_and_badges(
            student_id,
            'lab_submission',
            {
                'score': feedback.grade_percentage,
                'assignment_type': assignment.lab_type.value,
                'perfect_score': feedback.grade_percentage == 100
            }
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'feedback': feedback.__dict__,
                'gamification': gamification_result,
                'submitted_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@lab_assignments_bp.route('/assignments', methods=['GET'])
def get_lab_assignments():
    """Get available lab assignments"""
    try:
        # Sample assignments for different engineering topics
        assignments = [
            {
                'assignment_id': 'algo_sorting_001',
                'title': 'Sorting Algorithms Implementation',
                'lab_type': 'algorithms',
                'difficulty': 2,
                'max_score': 100,
                'estimated_time': 45,
                'description': 'Implement efficient sorting algorithm',
                'learning_objectives': [
                    'Understand time complexity',
                    'Implement efficient sorting',
                    'Handle edge cases'
                ]
            },
            {
                'assignment_id': 'ds_linkedlist_001',
                'title': 'Linked List Operations',
                'lab_type': 'data_structures',
                'difficulty': 3,
                'max_score': 100,
                'estimated_time': 60,
                'description': 'Implement linked list with CRUD operations'
            },
            {
                'assignment_id': 'sys_fileio_001',
                'title': 'File System Operations',
                'lab_type': 'systems_programming',
                'difficulty': 4,
                'max_score': 100,
                'estimated_time': 90,
                'description': 'Implement file operations with error handling'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': assignments
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@lab_assignments_bp.route('/assignment/<assignment_id>', methods=['GET'])
def get_assignment_details(assignment_id):
    """Get detailed assignment information"""
    try:
        assignment = _get_assignment_config(assignment_id)
        if not assignment:
            return jsonify({
                'status': 'error',
                'message': 'Assignment not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'assignment_id': assignment.assignment_id,
                'title': assignment.title,
                'lab_type': assignment.lab_type.value,
                'max_score': assignment.max_score,
                'test_cases_count': len(assignment.test_cases),
                'evaluation_criteria': assignment.evaluation_criteria,
                'learning_objectives': assignment.learning_objectives
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@lab_assignments_bp.route('/quick-feedback', methods=['POST'])
def get_quick_feedback():
    """Get instant feedback on code snippet"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({
                'status': 'error',
                'message': 'Code is required'
            }), 400
        
        # Quick analysis without full assignment context
        from services.code_analysis_service import code_analyzer
        analysis = code_analyzer.analyze_code(code, language)
        
        # Generate quick feedback
        feedback = {
            'complexity_level': analysis.complexity_level.value if hasattr(analysis, 'complexity_level') else 'unknown',
            'time_complexity': analysis.big_o_analysis.get('time_complexity', 'Unknown') if hasattr(analysis, 'big_o_analysis') else 'Unknown',
            'code_quality_score': getattr(analysis, 'best_practices_score', 70),
            'suggestions': getattr(analysis, 'optimization_suggestions', [])[:3],
            'issues': getattr(analysis, 'code_smells', [])[:2]
        }
        
        return jsonify({
            'status': 'success',
            'data': feedback
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def _get_assignment_config(assignment_id: str) -> LabAssignment:
    """Get assignment configuration by ID"""
    
    # Sample assignment configurations
    assignments_db = {
        'algo_sorting_001': LabAssignment(
            assignment_id='algo_sorting_001',
            title='Sorting Algorithms Implementation',
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[
                {'input': '[64, 34, 25, 12, 22, 11, 90]', 'expected': '[11, 12, 22, 25, 34, 64, 90]'},
                {'input': '[5, 2, 4, 6, 1, 3]', 'expected': '[1, 2, 3, 4, 5, 6]'},
                {'input': '[]', 'expected': '[]'},
                {'input': '[1]', 'expected': '[1]'}
            ],
            evaluation_criteria={'correctness': 40, 'efficiency': 30, 'quality': 20, 'edge_cases': 10},
            learning_objectives=[
                'Implement efficient sorting algorithms',
                'Understand time/space complexity',
                'Handle edge cases properly'
            ]
        ),
        'ds_linkedlist_001': LabAssignment(
            assignment_id='ds_linkedlist_001',
            title='Linked List Operations',
            lab_type=LabType.DATA_STRUCTURES,
            max_score=100,
            test_cases=[
                {'operation': 'insert', 'value': 1, 'expected': 'success'},
                {'operation': 'search', 'value': 1, 'expected': 'found'},
                {'operation': 'delete', 'value': 1, 'expected': 'success'}
            ],
            evaluation_criteria={'implementation': 40, 'memory': 30, 'operations': 30},
            learning_objectives=[
                'Implement linked list data structure',
                'Manage memory efficiently',
                'Implement CRUD operations'
            ]
        )
    }
    
    return assignments_db.get(assignment_id)
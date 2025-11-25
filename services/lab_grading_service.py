"""
Engineering Lab Assignment Automated Grading Service
Specialized AI-powered evaluation system for engineering curriculum exercises
"""

import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from services.ai_grading_service import grade_submission
from services.code_analysis_service import code_analyzer
from services.plagiarism_service import enhanced_plagiarism_detector

class LabType(Enum):
    ALGORITHMS = "algorithms"
    DATA_STRUCTURES = "data_structures"
    SYSTEMS_PROGRAMMING = "systems_programming"
    MACHINE_LEARNING = "machine_learning"
    WEB_DEVELOPMENT = "web_development"

@dataclass
class LabAssignment:
    assignment_id: str
    title: str
    lab_type: LabType
    max_score: int
    test_cases: List[Dict]
    evaluation_criteria: Dict
    learning_objectives: List[str]

@dataclass
class CustomizedFeedback:
    overall_score: int
    grade_percentage: float
    execution_results: Dict
    improvement_suggestions: List[str]
    commendations: List[str]
    plagiarism_report: Dict

class EngineeringLabGradingService:
    def __init__(self):
        self.lab_templates = self._load_lab_templates()
        self.feedback_templates = self._load_feedback_templates()
        
    def _load_lab_templates(self) -> Dict:
        """Load lab assignment templates for engineering topics"""
        return {
            LabType.ALGORITHMS: {
                "sorting": {
                    "test_cases": [
                        {"input": "[64, 34, 25, 12]", "expected": "[12, 25, 34, 64]"},
                        {"input": "[]", "expected": "[]"},
                        {"input": "[1]", "expected": "[1]"}
                    ],
                    "criteria": {"correctness": 40, "efficiency": 30, "quality": 20, "edge_cases": 10}
                }
            },
            LabType.DATA_STRUCTURES: {
                "linked_list": {
                    "test_cases": [
                        {"operation": "insert", "value": 1, "expected": "success"},
                        {"operation": "search", "value": 1, "expected": "found"}
                    ],
                    "criteria": {"implementation": 40, "memory": 30, "operations": 30}
                }
            }
        }
    
    def _load_feedback_templates(self) -> Dict:
        """Load feedback templates for different scenarios"""
        return {
            "excellent": "Outstanding implementation! Shows mastery of {concept}.",
            "good": "Good solution with solid understanding of {topic}.",
            "needs_improvement": "Consider optimizing {section} using {suggestion}.",
            "error_handling": "Add error handling for {scenario} to improve robustness."
        }
    
    async def evaluate_lab_submission(self, code: str, assignment: LabAssignment, 
                                    student_id: str, language: str = "python") -> CustomizedFeedback:
        """Fast, comprehensive evaluation with customized feedback"""
        try:
            # 1. Execute test cases
            execution_results = await self._run_tests(code, assignment.test_cases, language)
            
            # 2. Code analysis
            analysis = code_analyzer.analyze_code(code, language)
            
            # 3. Plagiarism check
            plagiarism = enhanced_plagiarism_detector.check_enhanced_plagiarism(
                code, assignment.assignment_id, student_id, language
            )
            
            # 4. Calculate scores
            scores = self._calculate_scores(execution_results, analysis, assignment)
            
            # 5. Generate feedback
            feedback = self._generate_feedback(scores, analysis, assignment)
            
            return CustomizedFeedback(
                overall_score=scores['total'],
                grade_percentage=scores['percentage'],
                execution_results=execution_results,
                improvement_suggestions=feedback['improvements'],
                commendations=feedback['commendations'],
                plagiarism_report=plagiarism
            )
            
        except Exception as e:
            return self._create_error_feedback(str(e), assignment.max_score)
    
    async def _run_tests(self, code: str, test_cases: List[Dict], language: str) -> Dict:
        """Execute test cases and return detailed results"""
        results = {'passed': 0, 'total': len(test_cases), 'details': []}
        
        for i, test in enumerate(test_cases):
            try:
                grade_result = grade_submission(code, [test], language)
                passed = grade_result.get('test_results', [{}])[0].get('passed', False)
                
                if passed:
                    results['passed'] += 1
                
                results['details'].append({
                    'test': i + 1,
                    'passed': passed,
                    'input': test.get('input', ''),
                    'expected': test.get('expected', ''),
                    'actual': grade_result.get('test_results', [{}])[0].get('actual_output', '')
                })
            except Exception as e:
                results['details'].append({'test': i + 1, 'error': str(e)})
        
        results['success_rate'] = results['passed'] / results['total'] if results['total'] > 0 else 0
        return results
    
    def _calculate_scores(self, execution_results: Dict, analysis, assignment: LabAssignment) -> Dict:
        """Calculate weighted scores based on criteria"""
        criteria = assignment.evaluation_criteria
        
        # Correctness score
        correctness = execution_results['success_rate'] * 100
        correctness_points = (correctness * criteria.get('correctness', 40)) / 100
        
        # Quality score
        quality = getattr(analysis, 'best_practices_score', 70)
        quality_points = (quality * criteria.get('quality', 30)) / 100
        
        # Efficiency score
        efficiency = 80  # Default good score
        if hasattr(analysis, 'big_o_analysis'):
            complexity = analysis.big_o_analysis.get('time_complexity', 'O(n)')
            efficiency_map = {'O(1)': 100, 'O(log n)': 90, 'O(n)': 80, 'O(n²)': 50}
            efficiency = efficiency_map.get(complexity, 60)
        efficiency_points = (efficiency * criteria.get('efficiency', 30)) / 100
        
        total = correctness_points + quality_points + efficiency_points
        percentage = (total / assignment.max_score) * 100
        
        return {
            'correctness': correctness_points,
            'quality': quality_points,
            'efficiency': efficiency_points,
            'total': min(assignment.max_score, int(total)),
            'percentage': min(100, percentage)
        }
    
    def _generate_feedback(self, scores: Dict, analysis, assignment: LabAssignment) -> Dict:
        """Generate personalized feedback based on performance"""
        feedback = {'commendations': [], 'improvements': []}
        
        # Commendations
        if scores['percentage'] >= 90:
            feedback['commendations'].append("Excellent work! Outstanding implementation.")
        elif scores['percentage'] >= 75:
            feedback['commendations'].append("Good solution with solid understanding.")
        
        # Improvements
        if scores['correctness'] < assignment.evaluation_criteria.get('correctness', 40) * 0.8:
            feedback['improvements'].append("Review test cases and fix failing scenarios.")
        
        if hasattr(analysis, 'optimization_suggestions'):
            feedback['improvements'].extend(analysis.optimization_suggestions[:2])
        
        return feedback
    
    def _create_error_feedback(self, error: str, max_score: int) -> CustomizedFeedback:
        """Create feedback for evaluation errors"""
        return CustomizedFeedback(
            overall_score=0,
            grade_percentage=0,
            execution_results={'error': error},
            improvement_suggestions=[f"Evaluation failed: {error}"],
            commendations=[],
            plagiarism_report={'passed': True, 'similarity_score': 0}
        )

# Global service instance
lab_grading_service = EngineeringLabGradingService()
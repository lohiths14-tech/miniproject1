"""
Test data builders for complex object construction
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any


class TestDataBuilder:
    """Builder for creating complex test data objects"""

    def __init__(self):
        self.data = {}

    def build(self):
        """Return the built data"""
        return self.data.copy()

    def reset(self):
        """Reset the builder"""
        self.data = {}
        return self


class UserBuilder(TestDataBuilder):
    """Builder for user test data"""

    def with_email(self, email):
        self.data['email'] = email
        return self

    def with_name(self, name):
        self.data['name'] = name
        return self

    def with_role(self, role):
        self.data['role'] = role
        return self

    def with_usn(self, usn):
        self.data['usn'] = usn
        return self

    def as_student(self):
        self.data['role'] = 'student'
        self.data['usn'] = f'STU{len(self.data.get("usn", "000"))}'
        return self

    def as_lecturer(self):
        self.data['role'] = 'lecturer'
        self.data.pop('usn', None)
        return self

    def with_password(self, password):
        self.data['password'] = password
        return self


class AssignmentBuilder(TestDataBuilder):
    """Builder for assignment test data"""

    def with_title(self, title):
        self.data['title'] = title
        return self

    def with_description(self, description):
        self.data['description'] = description
        return self

    def with_language(self, language):
        self.data['language'] = language
        return self

    def with_deadline(self, deadline):
        self.data['deadline'] = deadline
        return self

    def due_in_days(self, days):
        self.data['deadline'] = datetime.now() + timedelta(days=days)
        return self

    def with_test_cases(self, test_cases):
        self.data['test_cases'] = test_cases
        return self

    def add_test_case(self, input_val, expected_output):
        if 'test_cases' not in self.data:
            self.data['test_cases'] = []
        self.data['test_cases'].append({
            'input': input_val,
            'expected_output': expected_output
        })
        return self

    def with_max_score(self, score):
        self.data['max_score'] = score
        return self

    def with_difficulty(self, difficulty):
        self.data['difficulty'] = difficulty
        return self


class SubmissionBuilder(TestDataBuilder):
    """Builder for submission test data"""

    def with_code(self, code):
        self.data['code'] = code
        return self

    def with_language(self, language):
        self.data['language'] = language
        return self

    def with_user_id(self, user_id):
        self.data['user_id'] = user_id
        return self

    def with_assignment_id(self, assignment_id):
        self.data['assignment_id'] = assignment_id
        return self

    def with_status(self, status):
        self.data['status'] = status
        return self

    def with_score(self, score):
        self.data['score'] = score
        return self

    def as_pending(self):
        self.data['status'] = 'pending'
        return self

    def as_graded(self, score=85):
        self.data['status'] = 'completed'
        self.data['score'] = score
        return self


class GradingResultBuilder(TestDataBuilder):
    """Builder for grading result test data"""

    def with_score(self, score):
        self.data['score'] = score
        return self

    def with_max_score(self, max_score):
        self.data['max_score'] = max_score
        return self

    def with_test_results(self, passed, total):
        self.data['passed_tests'] = passed
        self.data['total_tests'] = total
        return self

    def with_feedback(self, feedback):
        self.data['feedback'] = feedback
        return self

    def with_suggestions(self, suggestions):
        self.data['suggestions'] = suggestions
        return self

    def with_execution_time(self, time):
        self.data['execution_time'] = time
        return self

    def with_memory_used(self, memory):
        self.data['memory_used'] = memory
        return self

    def as_perfect_score(self):
        self.data['score'] = 100
        self.data['max_score'] = 100
        self.data['passed_tests'] = self.data.get('total_tests', 10)
        return self

    def as_failed(self):
        self.data['score'] = 0
        self.data['passed_tests'] = 0
        return self


class AchievementBuilder(TestDataBuilder):
    """Builder for achievement test data"""

    def with_name(self, name):
        self.data['name'] = name
        return self

    def with_type(self, achievement_type):
        self.data['type'] = achievement_type
        return self

    def with_tier(self, tier):
        self.data['tier'] = tier
        return self

    def with_points(self, points):
        self.data['points'] = points
        return self

    def as_first_submission(self):
        self.data['type'] = 'first_submission'
        self.data['name'] = 'First Steps'
        self.data['tier'] = 'bronze'
        self.data['points'] = 10
        return self

    def as_perfect_score(self):
        self.data['type'] = 'perfect_score'
        self.data['name'] = 'Perfectionist'
        self.data['tier'] = 'gold'
        self.data['points'] = 50
        return self

    def as_streak(self, days):
        self.data['type'] = f'streak_{days}'
        self.data['name'] = f'{days}-Day Streak'
        self.data['tier'] = 'silver' if days < 7 else 'gold'
        self.data['points'] = days * 5
        return self


class PlagiarismCheckBuilder(TestDataBuilder):
    """Builder for plagiarism check test data"""

    def with_similarity_score(self, score):
        self.data['similarity_score'] = score
        return self

    def with_algorithm(self, algorithm):
        self.data['algorithm'] = algorithm
        return self

    def with_flagged(self, flagged):
        self.data['flagged'] = flagged
        return self

    def with_matches(self, matches):
        self.data['matches'] = matches
        return self

    def as_flagged(self, score=95.0):
        self.data['similarity_score'] = score
        self.data['flagged'] = True
        return self

    def as_clean(self, score=30.0):
        self.data['similarity_score'] = score
        self.data['flagged'] = False
        return self


# Helper functions for quick building

def build_user(**kwargs):
    """Quick build a user"""
    builder = UserBuilder()
    for key, value in kwargs.items():
        if hasattr(builder, f'with_{key}'):
            getattr(builder, f'with_{key}')(value)
    return builder.build()


def build_assignment(**kwargs):
    """Quick build an assignment"""
    builder = AssignmentBuilder()
    for key, value in kwargs.items():
        if hasattr(builder, f'with_{key}'):
            getattr(builder, f'with_{key}')(value)
    return builder.build()


def build_submission(**kwargs):
    """Quick build a submission"""
    builder = SubmissionBuilder()
    for key, value in kwargs.items():
        if hasattr(builder, f'with_{key}'):
            getattr(builder, f'with_{key}')(value)
    return builder.build()

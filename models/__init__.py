"""Database models for the AI Grading System."""
from datetime import datetime

from bson.objectid import ObjectId
from flask import current_app
from passlib.hash import pbkdf2_sha256


class User:
    """User model for students and lecturers."""

    def __init__(self, email, username, password, role, **kwargs):
        """Initialize a new user.

        Args:
            email: User's email address
            username: User's username
            password: lf.rn text password (will be hashed)
            role: User role ('student' or 'lecturer')
            **kwargs: Additional user attributes
        """
        self.email = email
        self.username = username
        self.password_hash = pbkdf2_sha256.hash(password)
        self.role = role
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.is_2fa_enabled = kwargs.get('is_2fa_enabled', False)

        if role == 'student':
            self.usn = kwargs.get('usn', '')
        elif role == 'lecturer':
            self.lecturer_id = kwargs.get('lecturer_id', '')

    def check_password(self, password):
        """Verify password against stored hash."""
        return pbkdf2_sha256.verify(password, self.password_hash)

    def to_dict(self):
        """Convert user object to dictionary."""
        user_dict = {
            '_id': str(self._id) if hasattr(self, '_id') else None,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'is_2fa_enabled': getattr(self, 'is_2fa_enabled', False)
        }

        if self.role == 'student':
            user_dict['usn'] = getattr(self, 'usn', '')
        elif self.role == 'lecturer':
            user_dict['lecturer_id'] = getattr(self, 'lecturer_id', '')

        return user_dict

    @staticmethod
    def find_by_email(email):
        """Find user by email address."""
        user_data = current_app.mongo.db.users.find_one({'email': email})
        if user_data:
            user = User.__new__(User)
            user.__dict__.update(user_data)
            return user
        return None

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID."""
        user_data = current_app.mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            user = User.__new__(User)
            user.__dict__.update(user_data)
            return user
        return None

    def save(self):
        """Save user to database."""
        user_dict = self.__dict__.copy()
        if hasattr(self, '_id') and getattr(self, '_id', None):
            # Update existing user
            current_app.mongo.db.users.update_one(
                {'_id': self._id},
                {'$set': user_dict}
            )
        else:
            # Create new user
            result = current_app.mongo.db.users.insert_one(user_dict)
            self._id = result.inserted_id  # pylint: disable=attribute-defined-outside-init
        return self


class Assignment:
    """Assignment model for programming assignments."""

    def __init__(self, title, description, created_by, deadline, **kwargs):
        """Initialize a new assignment.

        Args:
            title: Assignment title
            description: Assignment description
            created_by: Lecturer's user ID
            deadline: Assignment deadline
            **kwargs: Additional assignment attributes
        """
        self.title = title
        self.description = description
        self.created_by = created_by
        self.deadline = deadline
        self.created_at = datetime.utcnow()
        self.is_active = True

        # Additional fields
        self.test_cases = kwargs.get('test_cases', [])
        self.programming_language = kwargs.get('programming_language', 'python')
        self.max_score = kwargs.get('max_score', 100)
        self.starter_code = kwargs.get('starter_code', '')
        self.difficulty = kwargs.get('difficulty', 'medium')

    def to_dict(self):
        """Convert assignment object to dictionary."""
        return {
            '_id': str(self._id) if hasattr(self, '_id') else None,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'deadline': self.deadline,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'test_cases': self.test_cases,
            'programming_language': self.programming_language,
            'max_score': self.max_score,
            'starter_code': self.starter_code,
            'difficulty': self.difficulty
        }

    @staticmethod
    def find_by_id(assignment_id):
        """Find assignment by ID."""
        assignment_data = current_app.mongo.db.assignments.find_one(
            {'_id': ObjectId(assignment_id)}
        )
        if assignment_data:
            assignment = Assignment.__new__(Assignment)
            assignment.__dict__.update(assignment_data)
            return assignment
        return None

    @staticmethod
    def find_all_active():
        """Find all active assignments."""
        assignments_data = current_app.mongo.db.assignments.find({'is_active': True})
        assignments = []
        for assignment_data in assignments_data:
            assignment = Assignment.__new__(Assignment)
            assignment.__dict__.update(assignment_data)
            assignments.append(assignment)
        return assignments

    def save(self):
        """Save assignment to database."""
        assignment_dict = self.__dict__.copy()
        if hasattr(self, '_id') and getattr(self, '_id', None):
            # Update existing assignment
            current_app.mongo.db.assignments.update_one(
                {'_id': self._id},
                {'$set': assignment_dict}
            )
        else:
            # Create new assignment
            result = current_app.mongo.db.assignments.insert_one(assignment_dict)
            self._id = result.inserted_id  # pylint: disable=attribute-defined-outside-init
        return self


class Submission:
    """Submission model for student code submissions."""

    def __init__(self, student_id, assignment_id, code, **kwargs):
        """Initialize a new submission.

        Args:
            student_id: Student's user ID
            assignment_id: Assignment ID
            code: Submitted code
            **kwargs: Additional submission attributes
        """
        self.student_id = student_id
        self.assignment_id = assignment_id
        self.code = code
        self.submitted_at = datetime.utcnow()

        # Grading results
        self.score = kwargs.get('score', 0)
        self.max_score = kwargs.get('max_score', 100)
        self.feedback = kwargs.get('feedback', '')
        self.test_results = kwargs.get('test_results', [])
        self.execution_time = kwargs.get('execution_time', 0)
        self.memory_usage = kwargs.get('memory_usage', 0)

        # Plagiarism detection
        self.plagiarism_score = kwargs.get('plagiarism_score', 0.0)
        self.plagiarism_passed = kwargs.get('plagiarism_passed', True)
        self.similar_submissions = kwargs.get('similar_submissions', [])

        # Status
        self.status = kwargs.get('status', 'submitted')

    def to_dict(self):
        """Convert submission object to dictionary."""
        return {
            '_id': str(self._id) if hasattr(self, '_id') else None,
            'student_id': self.student_id,
            'assignment_id': self.assignment_id,
            'code': self.code,
            'submitted_at': self.submitted_at,
            'score': self.score,
            'max_score': self.max_score,
            'feedback': self.feedback,
            'test_results': self.test_results,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'plagiarism_score': self.plagiarism_score,
            'plagiarism_passed': self.plagiarism_passed,
            'similar_submissions': self.similar_submissions,
            'status': self.status
        }

    @staticmethod
    def find_by_student_and_assignment(student_id, assignment_id):
        """Find submission by student and assignment."""
        submission_data = current_app.mongo.db.submissions.find_one({
            'student_id': student_id,
            'assignment_id': assignment_id
        })
        if submission_data:
            submission = Submission.__new__(Submission)
            submission.__dict__.update(submission_data)
            return submission
        return None

    @staticmethod
    def find_by_assignment(assignment_id):
        """Find all submissions for an assignment."""
        submissions_data = current_app.mongo.db.submissions.find(
            {'assignment_id': assignment_id}
        )
        submissions = []
        for submission_data in submissions_data:
            submission = Submission.__new__(Submission)
            submission.__dict__.update(submission_data)
            submissions.append(submission)
        return submissions

    def save(self):
        """Save submission to database."""
        submission_dict = self.__dict__.copy()
        if hasattr(self, '_id') and getattr(self, '_id', None):
            # Update existing submission
            current_app.mongo.db.submissions.update_one(
                {'_id': self._id},
                {'$set': submission_dict}
            )
        else:
            # Create new submission
            result = current_app.mongo.db.submissions.insert_one(submission_dict)
            self._id = result.inserted_id  # pylint: disable=attribute-defined-outside-init
        return self

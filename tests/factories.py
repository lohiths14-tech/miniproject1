"""
Test data factories using Factory Boy for generating test objects
"""
import factory
from factory import fuzzy
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


class UserFactory(factory.DictFactory):
    """Factory for creating test user data"""

    email = factory.LazyAttribute(lambda _: fake.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    password = factory.LazyAttribute(lambda _: fake.password())
    role = fuzzy.FuzzyChoice(['student', 'lecturer'])
    usn = factory.Sequence(lambda n: f'USN{n:04d}')
    created_at = factory.LazyFunction(datetime.now)

    class Meta:
        rename = {'class': 'class_'}


class StudentFactory(UserFactory):
    """Factory for creating test student data"""
    role = 'student'
    usn = factory.Sequence(lambda n: f'STU{n:04d}')


class LecturerFactory(UserFactory):
    """Factory for creating test lecturer data"""
    role = 'lecturer'
    usn = None


class AssignmentFactory(factory.DictFactory):
    """Factory for creating test assignment data"""

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    language = fuzzy.FuzzyChoice(['python', 'java', 'cpp', 'c', 'javascript'])
    deadline = factory.LazyFunction(lambda: datetime.now() + timedelta(days=7))
    created_at = factory.LazyFunction(datetime.now)
    test_cases = factory.LazyFunction(lambda: [
        {'input': '5', 'expected_output': '5'},
        {'input': '10', 'expected_output': '55'}
    ])
    max_score = 100
    difficulty = fuzzy.FuzzyChoice(['easy', 'medium', 'hard'])


class SubmissionFactory(factory.DictFactory):
    """Factory for creating test submission data"""

    code = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    language = fuzzy.FuzzyChoice(['python', 'java', 'cpp', 'c', 'javascript'])
    submitted_at = factory.LazyFunction(datetime.now)
    status = fuzzy.FuzzyChoice(['pending', 'grading', 'completed', 'failed'])
    score = fuzzy.FuzzyInteger(0, 100)


class TestCaseFactory(factory.DictFactory):
    """Factory for creating test case data"""

    input = factory.LazyAttribute(lambda _: str(fake.random_int(min=1, max=100)))
    expected_output = factory.LazyAttribute(lambda obj: str(int(obj.input) * 2))
    weight = fuzzy.FuzzyInteger(1, 10)
    is_hidden = fuzzy.FuzzyChoice([True, False])


class GradingResultFactory(factory.DictFactory):
    """Factory for creating grading result data"""

    score = fuzzy.FuzzyInteger(0, 100)
    max_score = 100
    passed_tests = fuzzy.FuzzyInteger(0, 10)
    total_tests = 10
    execution_time = fuzzy.FuzzyFloat(0.1, 5.0)
    memory_used = fuzzy.FuzzyInteger(1000, 50000)
    feedback = factory.LazyAttribute(lambda _: fake.paragraph())
    suggestions = factory.LazyFunction(lambda: [fake.sentence() for _ in range(3)])
    graded_at = factory.LazyFunction(datetime.now)


class AchievementFactory(factory.DictFactory):
    """Factory for creating achievement data"""

    name = factory.LazyAttribute(lambda _: fake.catch_phrase())
    description = factory.LazyAttribute(lambda _: fake.sentence())
    type = fuzzy.FuzzyChoice([
        'first_submission',
        'perfect_score',
        'streak_3',
        'streak_7',
        'streak_30',
        'fast_solver',
        'code_quality',
        'helpful_peer'
    ])
    tier = fuzzy.FuzzyChoice(['bronze', 'silver', 'gold', 'platinum'])
    points = fuzzy.FuzzyInteger(10, 100)
    earned_at = factory.LazyFunction(datetime.now)


class LeaderboardEntryFactory(factory.DictFactory):
    """Factory for creating leaderboard entry data"""

    rank = factory.Sequence(lambda n: n + 1)
    points = fuzzy.FuzzyInteger(0, 10000)
    submissions_count = fuzzy.FuzzyInteger(0, 100)
    perfect_scores = fuzzy.FuzzyInteger(0, 50)
    streak = fuzzy.FuzzyInteger(0, 30)
    level = fuzzy.FuzzyInteger(1, 50)


class PlagiarismCheckFactory(factory.DictFactory):
    """Factory for creating plagiarism check data"""

    similarity_score = fuzzy.FuzzyFloat(0.0, 100.0)
    algorithm = fuzzy.FuzzyChoice(['tfidf', 'ast', 'difflib'])
    flagged = factory.LazyAttribute(lambda obj: obj.similarity_score > 91.0)
    checked_at = factory.LazyFunction(datetime.now)
    matches = factory.LazyFunction(lambda: [])


class CollaborationSessionFactory(factory.DictFactory):
    """Factory for creating collaboration session data"""

    session_id = factory.LazyAttribute(lambda _: fake.uuid4())
    host_id = factory.LazyAttribute(lambda _: fake.uuid4())
    participants = factory.LazyFunction(lambda: [])
    code = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    language = fuzzy.FuzzyChoice(['python', 'java', 'cpp', 'c', 'javascript'])
    created_at = factory.LazyFunction(datetime.now)
    is_active = True


class EmailNotificationFactory(factory.DictFactory):
    """Factory for creating email notification data"""

    recipient = factory.LazyAttribute(lambda _: fake.email())
    subject = factory.LazyAttribute(lambda _: fake.sentence())
    body = factory.LazyAttribute(lambda _: fake.paragraph())
    type = fuzzy.FuzzyChoice([
        'welcome',
        'assignment_published',
        'submission_graded',
        'password_reset',
        'achievement_earned'
    ])
    sent_at = factory.LazyFunction(datetime.now)
    status = fuzzy.FuzzyChoice(['pending', 'sent', 'failed'])


class CodeReviewFactory(factory.DictFactory):
    """Factory for creating code review data"""

    overall_rating = fuzzy.FuzzyInteger(1, 10)
    readability_score = fuzzy.FuzzyInteger(1, 10)
    efficiency_score = fuzzy.FuzzyInteger(1, 10)
    best_practices_score = fuzzy.FuzzyInteger(1, 10)
    comments = factory.LazyFunction(lambda: [fake.sentence() for _ in range(3)])
    suggestions = factory.LazyFunction(lambda: [fake.sentence() for _ in range(3)])
    reviewed_at = factory.LazyFunction(datetime.now)


# Helper functions for creating multiple objects

def create_users(count=5, **kwargs):
    """Create multiple test users"""
    return [UserFactory(**kwargs) for _ in range(count)]


def create_students(count=5, **kwargs):
    """Create multiple test students"""
    return [StudentFactory(**kwargs) for _ in range(count)]


def create_lecturers(count=2, **kwargs):
    """Create multiple test lecturers"""
    return [LecturerFactory(**kwargs) for _ in range(count)]


def create_assignments(count=3, **kwargs):
    """Create multiple test assignments"""
    return [AssignmentFactory(**kwargs) for _ in range(count)]


def create_submissions(count=10, **kwargs):
    """Create multiple test submissions"""
    return [SubmissionFactory(**kwargs) for _ in range(count)]


def create_test_cases(count=5, **kwargs):
    """Create multiple test cases"""
    return [TestCaseFactory(**kwargs) for _ in range(count)]


def create_achievements(count=5, **kwargs):
    """Create multiple achievements"""
    return [AchievementFactory(**kwargs) for _ in range(count)]


def create_leaderboard_entries(count=10, **kwargs):
    """Create multiple leaderboard entries"""
    entries = [LeaderboardEntryFactory(**kwargs) for _ in range(count)]
    # Sort by points descending and assign ranks
    entries.sort(key=lambda x: x['points'], reverse=True)
    for i, entry in enumerate(entries):
        entry['rank'] = i + 1
    return entries


# Sample code snippets for testing

SAMPLE_PYTHON_CODE = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(result)
"""

SAMPLE_JAVA_CODE = """
public class Fibonacci {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }

    public static void main(String[] args) {
        System.out.println(fibonacci(10));
    }
}
"""

SAMPLE_CPP_CODE = """
#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    cout << fibonacci(10) << endl;
    return 0;
}
"""

SAMPLE_JAVASCRIPT_CODE = """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

console.log(fibonacci(10));
"""

# Sample test data sets

SAMPLE_TEST_CASES = [
    {'input': '0', 'expected_output': '0'},
    {'input': '1', 'expected_output': '1'},
    {'input': '5', 'expected_output': '5'},
    {'input': '10', 'expected_output': '55'},
]

SAMPLE_PLAGIARISM_PAIRS = [
    ('identical', 100.0),
    ('very_similar', 95.0),
    ('similar', 85.0),
    ('somewhat_similar', 70.0),
    ('different', 30.0),
    ('completely_different', 5.0),
]

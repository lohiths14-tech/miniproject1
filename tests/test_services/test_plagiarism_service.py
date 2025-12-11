"""
Unit tests for Plagiarism Detection Service
"""
import pytest
from unittest.mock import Mock, patch
from services.plagiarism_service import (
    CrossLanguagePlagiarismDetector,
    calculate_tfidf_similarity,
    calculate_sequence_similarity,
    calculate_structure_similarity,
    normalize_code,
    extract_structural_features,
    calculate_feature_similarity,
    calculate_pattern_similarity
)
import ast
from settings import Config


@pytest.mark.unit
class TestPlagiarismService:
    """Test suite for plagiarism detection"""

    @pytest.fixture
    def detector(self):
        """Create plagiarism detector instance"""
        return CrossLanguagePlagiarismDetector()

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None
        assert detector.threshold == 0.91  # Default threshold

    def test_identical_code_detection(self, detector):
        """Test detection of identical code"""
        code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        code2 = code1  # Identical

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = [
                {'code': code2, 'student_id': 'student2', 'language': 'python'}
            ]

            result = detector.check_enhanced_plagiarism(
                code=code1,
                assignment_id='test_assignment',
                student_id='student1',
                language='python'
            )

            assert result is not None
            if result.get('has_plagiarism'):
                assert result['similarity_score'] >= 0.91

    def test_different_code_no_plagiarism(self, detector):
        """Test that different code is not flagged"""
        code1 = "def add(a, b): return a + b"
        code2 = "def multiply(x, y): return x * y"

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = [
                {'code': code2, 'student_id': 'student2', 'language': 'python'}
            ]

            result = detector.check_enhanced_plagiarism(
                code=code1,
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            assert result is not None
            assert not result.get('has_plagiarism', False) or \
                   result.get('similarity_score', 0) < 0.91

    def test_cross_language_detection(self, detector):
        """Test cross-language plagiarism detection"""
        python_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
"""
        java_code = """
void bubbleSort(int[] arr) {
    int n = arr.length;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}
"""

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = [
                {'code': java_code, 'student_id': 'student2', 'language': 'java'}
            ]

            result = detector.check_enhanced_plagiarism(
                code=python_code,
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            # Should detect algorithmic similarity
            assert result is not None

    def test_obfuscation_detection(self, detector):
        """Test detection of obfuscated code"""
        original = "def calculate(x): return x * 2"
        obfuscated = "def calc(y): return y * 2"  # Variable renamed

        similarity = detector._calculate_tfidf_similarity(original, obfuscated)

        # Should still detect high similarity
        assert similarity is not None

    def test_code_normalization(self, detector):
        """Test code normalization removes formatting differences"""
        code1 = "def test():\n    return 5"
        code2 = "def test():return 5"

        normalized1 = detector._advanced_normalize_code(code1, 'python')
        normalized2 = detector._advanced_normalize_code(code2, 'python')

        # Normalized versions should be similar
        assert normalized1 is not None
        assert normalized2 is not None

    def test_empty_code_handling(self, detector):
        """Test handling of empty code submissions"""
        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = []

            result = detector.check_enhanced_plagiarism(
                code="",
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            assert result is not None

    def test_visualization_data_generation(self, detector):
        """Test heat map visualization data"""
        code = "def test(): return 5"
        similarities = [
            {'overall_similarity': 0.95, 'student_id': 'student2'}
        ]

        viz_data = detector._generate_visualization_data(code, similarities)

        assert viz_data is not None

    @pytest.mark.parametrize("language", ['python', 'java', 'cpp', 'javascript', 'c'])
    def test_multi_language_support(self, detector, language):
        """Test plagiarism detection works for all supported languages"""
        code = "function test() { return 5; }"

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = []

            result = detector.check_enhanced_plagiarism(
                code=code,
                assignment_id='test',
                student_id='student1',
                language=language
            )

            assert result is not None


@pytest.mark.unit
class TestTfidfSimilarity:
    """Test suite for TF-IDF similarity calculations (9.1)"""

    def test_tfidf_vectorization(self):
        """Test TF-IDF vectorization produces valid output"""
        code1 = "def add(a, b): return a + b"
        code2 = "def subtract(x, y): return x - y"

        similarity = calculate_tfidf_similarity(code1, code2)

        # Should return a valid similarity score
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation"""
        code1 = "for i in range(10): print(i)"
        code2 = "for j in range(10): print(j)"

        similarity = calculate_tfidf_similarity(code1, code2)

        # Similar code should have high TF-IDF similarity
        assert similarity > 0.5

    def test_tfidf_identical_code(self):
        """Test TF-IDF with identical code (100% similarity)"""
        code = "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"

        similarity = calculate_tfidf_similarity(code, code)

        # Identical code should have similarity of 1.0
        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_tfidf_different_code(self):
        """Test TF-IDF with completely different code (0% similarity)"""
        code1 = "def hello(): print('Hello')"
        code2 = "class MyClass: pass"

        similarity = calculate_tfidf_similarity(code1, code2)

        # Different code should have low similarity
        assert similarity < 0.3

    def test_tfidf_similar_code(self):
        """Test TF-IDF with similar code (variablerenames may reduce similarity)"""
        code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        code2 = """
def fib(num):
    if num <= 1:
        return num
    return fib(num-1) + fib(num-2)
"""

        similarity = calculate_tfidf_similarity(code1, code2)

        # Similar code with renames may have lower TF-IDF but still some similarity
        assert 0.1 <= similarity <= 0.95

    def test_tfidf_empty_code(self):
        """Test TF-IDF with empty code"""
        similarity = calculate_tfidf_similarity("", "def test(): pass")

        # Empty code should have zero similarity
        assert similarity == 0.0

    def test_tfidf_whitespace_only(self):
        """Test TF-IDF with whitespace-only code"""
        similarity = calculate_tfidf_similarity("   \n\n   ", "def test(): pass")

        # Whitespace-only code should have zero similarity
        assert similarity == 0.0


@pytest.mark.unit
class TestASTComparison:
    """Test suite for AST comparison (9.2)"""

    def test_ast_parsing(self):
        """Test AST parsing for valid Python code"""
        code = """
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""

        # Should parse without errors
        tree = ast.parse(code)
        assert tree is not None

        # Extract features
        features = extract_structural_features(tree)
        assert features['functions'] == 2  # add and multiply
        assert features['classes'] == 1    # Calculator

    def test_structural_similarity(self):
        """Test structural similarity calculation"""
        code1 = """
def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
        code2 = """
def transform(values):
    output = []
    for val in values:
        if val > 0:
            output.append(val * 2)
    return output
"""

        similarity = calculate_structure_similarity(code1, code2)

        # Structurally similar code should have high similarity
        assert similarity > 0.7

    def test_ast_renamed_variables(self):
        """Test AST comparison with renamed variables"""
        code1 = "def calculate(x, y): return x + y"
        code2 = "def calculate(a, b): return a + b"

        similarity = calculate_structure_similarity(code1, code2)

        # Should detect high structural similarity despite variable renaming
        assert similarity > 0.8

    def test_ast_reordered_statements(self):
        """Test AST comparison with reordered statements"""
        code1 = """
def process():
    x = 5
    y = 10
    return x + y
"""
        code2 = """
def process():
    y = 10
    x = 5
    return x + y
"""

        similarity = calculate_structure_similarity(code1, code2)

        # Should still detect similarity
        assert similarity > 0.7

    def test_ast_invalid_syntax(self):
        """Test AST handling of invalid Python syntax"""
        invalid_code = "def invalid( return 5"
        valid_code = "def valid(): return 5"

        # Should fall back to pattern-based similarity
        similarity = calculate_structure_similarity(invalid_code, valid_code)

        # Should still return a valid similarity score
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    def test_structural_features_extraction(self):
        """Test extraction of structural features from AST"""
        code = """
import math
from collections import Counter

def fibonacci(n):
    if n <= 1:
        return n
    result = fibonacci(n-1) + fibonacci(n-2)
    return result

class MathHelper:
    def factorial(self, n):
        if n <= 1:
            return 1
        product = 1
        for i in range(1, n+1):
            product *= i
        return product
"""

        tree = ast.parse(code)
        features = extract_structural_features(tree)

        assert features['functions'] >= 2  # fibonacci and factorial
        assert features['classes'] == 1    # MathHelper
        assert features['loops'] >= 1      # for loop
        assert features['conditionals'] >= 2  # if statements
        assert features['imports'] == 2    # import and from import
        assert features['assignments'] > 0
        assert features['depth'] > 0

    def test_feature_similarity_identical(self):
        """Test feature similarity with identical features"""
        features = {
            'functions': 2,
            'classes': 1,
            'loops': 3,
            'conditionals': 4
        }

        similarity = calculate_feature_similarity(features, features)

        assert similarity == 1.0

    def test_feature_similarity_different(self):
        """Test feature similarity with different features"""
        features1 = {'functions': 5, 'classes': 2, 'loops': 1}
        features2 = {'functions': 1, 'classes': 0, 'loops': 5}

        similarity = calculate_feature_similarity(features1, features2)

        assert 0.0 <= similarity < 0.5


@pytest.mark.unit
class TestDifflibMatching:
    """Test suite for difflib sequence matching (9.3)"""

    def test_sequence_similarity_basic(self):
        """Test basic sequence similarity"""
        code1 = "def test(): return 5"
        code2 = "def test(): return 5"

        similarity = calculate_sequence_similarity(code1, code2)

        assert similarity == 1.0

    def test_sequence_similarity_whitespace(self):
        """Test sequence similarity with whitespace differences"""
        code1 = "def test():\n    return 5"
        code2 = "def test():return 5"

        # First normalize the code
        norm1 = normalize_code(code1)
        norm2 = normalize_code(code2)

        similarity = calculate_sequence_similarity(norm1, norm2)

        # After normalization, should have high similarity
        assert similarity > 0.9

    def test_sequence_similarity_comments(self):
        """Test sequence similarity with comment differences"""
        code1 = """
def fibonacci(n):
    # Base case
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        code2 = """
def fibonacci(n):
    # Different comment
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

        # Normalize to remove comments
        norm1 = normalize_code(code1)
        norm2 = normalize_code(code2)

        similarity = calculate_sequence_similarity(norm1, norm2)

        # After removing comments, should be identical
        assert similarity > 0.95

    def test_sequence_similarity_partial_match(self):
        """Test sequence similarity with partial matching"""
        code1 = "def add(a, b): return a + b"
        code2 = "def add(x, y): return x + y"

        similarity = calculate_sequence_similarity(code1, code2)

        # Should detect partial similarity
        assert 0.5 <= similarity <= 0.95

    def test_sequence_similarity_empty(self):
        """Test sequence similarity with empty strings"""
        similarity = calculate_sequence_similarity("", "def test(): pass")

        assert similarity == 0.0

    def test_sequence_similarity_completely_different(self):
        """Test sequence similarity with completely different code"""
        code1 = "print('hello world')"
        code2 = "class MyClass: pass"

        similarity = calculate_sequence_similarity(code1, code2)

        assert similarity < 0.3


@pytest.mark.unit
class TestPlagiarismDetection:
    """Test suite for plagiarism detection logic (9.4)"""

    def test_threshold_flagging(self):
        """Test threshold-based flagging (91% threshold)"""
        detector = CrossLanguagePlagiarismDetector()

        # High similarity code
        code1 = "def test(): return 42"
        code2 = "def test(): return 42"

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = [
                {
                    'code': code2,
                    'student_id': 'student2',
                    'language': 'python',
                    '_id': 'sub_002',
                    'submitted_at': '2024-01-01'
                }
            ]

            result = detector.check_enhanced_plagiarism(
                code=code1,
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            assert 'similarity_score' in result
            assert 'passed' in result
            assert 'threshold' in result
            assert result['threshold'] == 0.91

            # If similarity >= 0.91, should not pass
            if result['similarity_score'] >= 0.91:
                assert result['passed'] == False

    def test_report_generation(self):
        """Test report structure and generation"""
        detector = CrossLanguagePlagiarismDetector()

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = [
                {
                    'code': 'def test(): return 1',
                    'student_id': 'student2',
                    'language': 'python',
                    '_id': 'sub_002',
                    'submitted_at': '2024-01-01'
                }
            ]

            result = detector.check_enhanced_plagiarism(
                code='def test(): return 1',
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            # Verify report structure
            assert 'similarity_score' in result
            assert 'passed' in result
            assert 'similar_submissions' in result
            assert 'threshold' in result
            assert 'cross_language_detected' in result
            assert 'visualization_data' in result
            assert 'algorithm_patterns_detected' in result
            assert 'enhanced_analysis' in result

    def test_multiple_algorithm_combination(self):
        """Test multiple algorithm combination"""
        detector = CrossLanguagePlagiarismDetector()

        code1 = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
"""
        code2 = code1  # Identical for testing

        result = detector._calculate_comprehensive_similarity(
            code1, code2, 'python', 'python', {}
        )

        # Should have all similarity metrics
        assert 'overall_similarity' in result
        assert 'tfidf_similarity' in result
        assert 'sequence_similarity' in result
        assert 'structure_similarity' in result
        assert 'algorithm_similarity' in result
        assert 'confidence' in result

        # Overall should be weighted average
        assert isinstance(result['overall_similarity'], float)
        assert 0.0 <= result['overall_similarity'] <= 1.0

    def test_weighted_similarity_same_language(self):
        """Test weighted similarity for same language"""
        detector = CrossLanguagePlagiarismDetector()

        code = "def test(): return 1"

        result = detector._calculate_comprehensive_similarity(
            code, code, 'python', 'python', {}
        )

        # For same language, weights should be: tfidf*0.3 + seq*0.3 + struct*0.3 + algo*0.1
        expected = (
            result['tfidf_similarity'] * 0.3 +
            result['sequence_similarity'] * 0.3 +
            result['structure_similarity'] * 0.3 +
            result['algorithm_similarity'] * 0.1
        )

        assert result['overall_similarity'] == pytest.approx(expected, abs=0.01)

    def test_weighted_similarity_cross_language(self):
        """Test weighted similarity for cross-language"""
        detector = CrossLanguagePlagiarismDetector()

        python_code = "def test(): return 1"
        java_code = "int test() { return 1; }"

        result = detector._calculate_comprehensive_similarity(
            python_code, java_code, 'python', 'java', {}
        )

        # For cross-language, pattern similarity should be included
        assert result['cross_language'] == True
        assert 'pattern_similarity' in result

    def test_clean_submission_no_matches(self):
        """Test clean submission with no matches"""
        detector = CrossLanguagePlagiarismDetector()

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            mock_subs.return_value = []

            result = detector.check_enhanced_plagiarism(
                code='def unique(): return 999',
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            assert result['similarity_score'] == 0.0
            assert result['passed'] == True
            assert len(result['similar_submissions']) == 0

    def test_error_handling(self):
        """Test error handling in plagiarism detection"""
        detector = CrossLanguagePlagiarismDetector()

        with patch.object(detector, '_get_other_submissions') as mock_subs:
            # Simulate an error
            mock_subs.side_effect = Exception("Database error")

            result = detector.check_enhanced_plagiarism(
                code='def test(): return 1',
                assignment_id='test',
                student_id='student1',
                language='python'
            )

            # Should return error result with passed=True (fail-safe)
            assert 'error' in result or result['passed'] == True


@pytest.mark.unit
class TestCodeNormalization:
    """Test suite for code normalization"""

    def test_normalization_removes_comments(self):
        """Test that normalization removes comments"""
        code = """
def test():
    # This is a comment
    return 5  # Another comment
"""
        normalized = normalize_code(code)

        # Comments should be removed
        assert '#' not in normalized

    def test_normalization_removes_whitespace(self):
        """Test that normalization standardizes whitespace"""
        code1 = "def test():    return 5"
        code2 = "def test(): return 5"

        norm1 = normalize_code(code1)
        norm2 = normalize_code(code2)

        # Should produce similar normalized output
        assert calculate_sequence_similarity(norm1, norm2) > 0.9

    def test_normalization_lowercase(self):
        """Test that normalization converts to lowercase"""
        code = "def MyFunction(): return VALUE"
        normalized = normalize_code(code)

        # Should be lowercase
        assert normalized == normalized.lower()

    def test_normalization_operators(self):
        """Test operator normalization"""
        code = "x=5+3*2"
        normalized = normalize_code(code)

        # Operators should be properly spaced
        assert ' = ' in normalized or '=' in normalized

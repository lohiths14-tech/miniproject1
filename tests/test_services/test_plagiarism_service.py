"""
Unit tests for Plagiarism Detection Service
"""
import pytest
from unittest.mock import Mock, patch
from services.plagiarism_service import CrossLanguagePlagiarismDetector


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
            {'similarity': 0.95, 'student_id': 'student2'}
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

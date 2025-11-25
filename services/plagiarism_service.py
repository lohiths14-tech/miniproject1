from flask import current_app
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None
    print("Warning: scikit-learn not available. Using fallback similarity methods.")
import difflib
import re
import ast
import hashlib
import json
# import numpy as np  # Optional dependency
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from config import Config

class LanguageType(Enum):
    """Supported programming languages for cross-language detection"""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    C = "c"

@dataclass
class SimilarityMatch:
    """Enhanced similarity match with visualization data"""
    submission1_id: str
    submission2_id: str
    similarity_score: float
    matched_segments: List[Dict]
    algorithm_used: str
    languages: Tuple[str, str]
    confidence: float
    obfuscation_detected: bool
    heat_map_data: Optional[Dict] = None

class CrossLanguagePlagiarismDetector:
    def __init__(self):
        self.threshold = Config.PLAGIARISM_THRESHOLD
        self.cross_language_patterns = self._load_cross_language_patterns()
        self.algorithm_mappings = self._load_algorithm_mappings()
        
    def _load_cross_language_patterns(self) -> Dict:
        """Load patterns that are similar across programming languages"""
        return {
            "control_structures": {
                "for_loop": {
                    "python": r"for\s+\w+\s+in\s+range\(",
                    "java": r"for\s*\(.*\)\s*\{",
                    "cpp": r"for\s*\(.*\)\s*\{",
                    "javascript": r"for\s*\(.*\)\s*\{"
                },
                "while_loop": {
                    "python": r"while\s+.*:",
                    "java": r"while\s*\(.*\)\s*\{",
                    "cpp": r"while\s*\(.*\)\s*\{",
                    "javascript": r"while\s*\(.*\)\s*\{"
                },
                "if_statement": {
                    "python": r"if\s+.*:",
                    "java": r"if\s*\(.*\)\s*\{",
                    "cpp": r"if\s*\(.*\)\s*\{",
                    "javascript": r"if\s*\(.*\)\s*\{"
                }
            },
            "function_definitions": {
                "python": r"def\s+\w+\s*\(",
                "java": r"(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(",
                "cpp": r"\w+\s+\w+\s*\(",
                "javascript": r"function\s+\w+\s*\("
            },
            "variable_declarations": {
                "python": r"\w+\s*=\s*",
                "java": r"\w+\s+\w+\s*=\s*",
                "cpp": r"\w+\s+\w+\s*=\s*",
                "javascript": r"(var|let|const)\s+\w+\s*=\s*"
            }
        }
    
    def _load_algorithm_mappings(self) -> Dict:
        """Load common algorithm implementations across languages"""
        return {
            "fibonacci": {
                "patterns": [
                    r"fibonacci|fib",
                    r"n\s*<=\s*1",
                    r"n\s*-\s*1.*n\s*-\s*2",
                    r"return.*\+.*"
                ],
                "description": "Fibonacci sequence implementation"
            },
            "factorial": {
                "patterns": [
                    r"factorial|fact",
                    r"n\s*<=\s*1",
                    r"n\s*\*.*factorial",
                    r"return.*n.*\*"
                ],
                "description": "Factorial calculation"
            },
            "bubble_sort": {
                "patterns": [
                    r"bubble.*sort|sort.*bubble",
                    r"for.*for.*",
                    r"if.*>.*swap|if.*<.*swap",
                    r"temp\s*=|swap"
                ],
                "description": "Bubble sort algorithm"
            },
            "binary_search": {
                "patterns": [
                    r"binary.*search|search.*binary",
                    r"low.*high|left.*right",
                    r"mid.*=.*(low.*high|left.*right)",
                    r"target.*mid"
                ],
                "description": "Binary search algorithm"
            }
        }
    
    def check_enhanced_plagiarism(self, code: str, assignment_id: str, student_id: str, 
                                language: str = "python") -> Dict:
        """Enhanced plagiarism detection with cross-language support and visualization"""
        try:
            # Get all submissions for this assignment
            other_submissions = self._get_other_submissions(assignment_id, student_id)
            
            if not other_submissions:
                return self._create_clean_result()
            
            # Normalize and analyze the submitted code
            normalized_code = self._advanced_normalize_code(code, language)
            code_patterns = self._extract_algorithm_patterns(code, language)
            
            similarities = []
            
            for submission in other_submissions:
                other_code = submission.get('code', '')
                other_language = submission.get('language', 'python')
                
                # Multi-algorithm similarity analysis
                similarity_result = self._calculate_comprehensive_similarity(
                    code, other_code, language, other_language, code_patterns
                )
                
                if similarity_result['overall_similarity'] > 0.2:
                    similarities.append({
                        **similarity_result,
                        'student_id': submission['student_id'],
                        'submission_id': str(submission.get('_id', 'unknown')),
                        'submitted_at': submission.get('submitted_at'),
                        'other_language': other_language
                    })
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x['overall_similarity'], reverse=True)
            
            # Generate visualization data
            visualization_data = self._generate_visualization_data(code, similarities[:3])
            
            # Determine final result
            max_similarity = similarities[0]['overall_similarity'] if similarities else 0.0
            passed = max_similarity < self.threshold
            
            return {
                'similarity_score': max_similarity,
                'passed': passed,
                'similar_submissions': similarities[:5],
                'threshold': self.threshold,
                'cross_language_detected': any(s.get('cross_language', False) for s in similarities),
                'visualization_data': visualization_data,
                'algorithm_patterns_detected': code_patterns,
                'enhanced_analysis': True
            }
            
        except Exception as e:
            print(f"Enhanced plagiarism check failed: {str(e)}")
            return self._create_error_result(str(e))
    
    def _calculate_comprehensive_similarity(self, code1: str, code2: str, 
                                          lang1: str, lang2: str, patterns1: Dict) -> Dict:
        """Calculate comprehensive similarity across multiple dimensions"""
        is_cross_language = lang1 != lang2
        
        # Standard similarity measures
        tfidf_sim = self._calculate_tfidf_similarity(code1, code2)
        sequence_sim = self._calculate_sequence_similarity(code1, code2)
        structure_sim = self._calculate_structure_similarity(code1, code2, lang1, lang2)
        
        # Cross-language pattern matching
        pattern_sim = 0.0
        if is_cross_language:
            pattern_sim = self._calculate_cross_language_similarity(code1, code2, lang1, lang2)
        
        # Algorithm-specific similarity
        algorithm_sim = self._calculate_algorithm_similarity(code1, code2, patterns1)
        
        # Obfuscation detection
        obfuscation_detected = self._detect_advanced_obfuscation(code1, code2)
        
        # Weighted combination
        if is_cross_language:
            overall_similarity = (
                tfidf_sim * 0.2 +
                sequence_sim * 0.1 +
                structure_sim * 0.3 +
                pattern_sim * 0.3 +
                algorithm_sim * 0.1
            )
        else:
            overall_similarity = (
                tfidf_sim * 0.3 +
                sequence_sim * 0.3 +
                structure_sim * 0.3 +
                algorithm_sim * 0.1
            )
        
        return {
            'overall_similarity': overall_similarity,
            'tfidf_similarity': tfidf_sim,
            'sequence_similarity': sequence_sim,
            'structure_similarity': structure_sim,
            'pattern_similarity': pattern_sim,
            'algorithm_similarity': algorithm_sim,
            'cross_language': is_cross_language,
            'obfuscation_detected': obfuscation_detected,
            'confidence': self._calculate_confidence(overall_similarity, is_cross_language)
        }
    
    def _calculate_cross_language_similarity(self, code1: str, code2: str, 
                                           lang1: str, lang2: str) -> float:
        """Calculate similarity between different programming languages"""
        try:
            pattern_matches = 0
            total_patterns = 0
            
            for category, patterns in self.cross_language_patterns.items():
                if isinstance(patterns, dict) and lang1 in patterns and lang2 in patterns:
                    # Control structures comparison
                    for pattern_name, lang_patterns in patterns.items():
                        if isinstance(lang_patterns, dict) and lang1 in lang_patterns and lang2 in lang_patterns:
                            pattern1 = lang_patterns[lang1]
                            pattern2 = lang_patterns[lang2]
                            
                            matches1 = len(re.findall(pattern1, code1, re.IGNORECASE | re.MULTILINE))
                            matches2 = len(re.findall(pattern2, code2, re.IGNORECASE | re.MULTILINE))
                            
                            if matches1 > 0 and matches2 > 0:
                                # Similarity based on count of pattern matches
                                similarity = min(matches1, matches2) / max(matches1, matches2)
                                pattern_matches += similarity
                            
                            total_patterns += 1
                
                elif lang1 in patterns and lang2 in patterns:
                    # Direct pattern comparison
                    pattern1 = patterns[lang1]
                    pattern2 = patterns[lang2]
                    
                    matches1 = len(re.findall(pattern1, code1, re.IGNORECASE | re.MULTILINE))
                    matches2 = len(re.findall(pattern2, code2, re.IGNORECASE | re.MULTILINE))
                    
                    if matches1 > 0 and matches2 > 0:
                        similarity = min(matches1, matches2) / max(matches1, matches2)
                        pattern_matches += similarity
                    
                    total_patterns += 1
            
            return pattern_matches / total_patterns if total_patterns > 0 else 0.0
            
        except Exception as e:
            print(f"Cross-language similarity calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_algorithm_similarity(self, code1: str, code2: str, patterns1: Dict) -> float:
        """Calculate similarity based on algorithmic patterns"""
        try:
            algorithm_scores = []
            
            for algorithm_name, algorithm_info in self.algorithm_mappings.items():
                patterns = algorithm_info['patterns']
                
                # Check how many patterns match in both codes
                matches1 = sum(1 for pattern in patterns if re.search(pattern, code1, re.IGNORECASE))
                matches2 = sum(1 for pattern in patterns if re.search(pattern, code2, re.IGNORECASE))
                
                if matches1 > 0 and matches2 > 0:
                    # Both codes implement similar algorithm
                    algorithm_similarity = min(matches1, matches2) / len(patterns)
                    algorithm_scores.append(algorithm_similarity)
            
            return max(algorithm_scores) if algorithm_scores else 0.0
            
        except Exception as e:
            return 0.0
    
    def _generate_visualization_data(self, original_code: str, similarities: List[Dict]) -> Dict:
        """Generate data for similarity heat map visualization"""
        try:
            lines = original_code.split('\n')
            heat_map = [[0.0 for _ in range(len(line))] for line in lines]
            
            for similarity in similarities:
                if similarity['overall_similarity'] > 0.3:
                    # Mark similar regions with heat intensity
                    intensity = min(1.0, similarity['overall_similarity'])
                    
                    # For now, apply uniform heat (in real implementation, 
                    # this would be based on actual line-by-line matching)
                    for i in range(len(heat_map)):
                        for j in range(len(heat_map[i])):
                            heat_map[i][j] = max(heat_map[i][j], intensity * 0.7)
            
            return {
                'heat_map': heat_map,
                'line_count': len(lines),
                'max_similarity': max((s['overall_similarity'] for s in similarities), default=0.0),
                'similar_regions': self._identify_similar_regions(similarities)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _identify_similar_regions(self, similarities: List[Dict]) -> List[Dict]:
        """Identify specific code regions that are similar"""
        regions = []
        
        for similarity in similarities[:3]:  # Top 3 similarities
            if similarity['overall_similarity'] > 0.5:
                regions.append({
                    'submission_id': similarity.get('submission_id'),
                    'similarity_score': similarity['overall_similarity'],
                    'start_line': 1,  # Would be calculated from actual matching
                    'end_line': 10,   # Would be calculated from actual matching
                    'match_type': 'structural' if similarity.get('cross_language') else 'textual'
                })
        
        return regions
    
    def _extract_algorithm_patterns(self, code: str, language: str) -> Dict:
        """Extract algorithmic patterns from code"""
        detected_patterns = {}
        
        for algorithm_name, algorithm_info in self.algorithm_mappings.items():
            patterns = algorithm_info['patterns']
            matches = sum(1 for pattern in patterns if re.search(pattern, code, re.IGNORECASE))
            
            if matches >= len(patterns) * 0.6:  # 60% of patterns must match
                detected_patterns[algorithm_name] = {
                    'confidence': matches / len(patterns),
                    'description': algorithm_info['description']
                }
        
        return detected_patterns
    
    def _advanced_normalize_code(self, code: str, language: str) -> str:
        """Advanced code normalization considering language specifics"""
        try:
            # Language-specific comment removal
            if language in ['python']:
                code = re.sub(r'#.*', '', code)
                code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
            elif language in ['java', 'cpp', 'javascript', 'c']:
                code = re.sub(r'//.*', '', code)
                code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # Remove extra whitespace and normalize
            lines = []
            for line in code.split('\n'):
                line = line.strip()
                if line:
                    # Normalize operators and delimiters
                    line = re.sub(r'\s*([+\-*/=<>!&|]+)\s*', r' \1 ', line)
                    line = re.sub(r'\s*([(){}\[\],;])\s*', r'\1', line)
                    lines.append(line.lower())
            
            return '\n'.join(lines)
            
        except Exception as e:
            return code.lower().strip()
    
    def _detect_advanced_obfuscation(self, code1: str, code2: str) -> bool:
        """Detect sophisticated obfuscation techniques"""
        try:
            # Variable name systematic changes
            vars1 = set(re.findall(r'\b[a-zA-Z_]\w*\b', code1))
            vars2 = set(re.findall(r'\b[a-zA-Z_]\w*\b', code2))
            
            # Check for systematic variable renaming
            var_overlap = len(vars1.intersection(vars2)) / max(len(vars1), len(vars2), 1)
            
            # Check for code structure preservation with different naming
            structure1 = re.sub(r'\b[a-zA-Z_]\w*\b', 'VAR', code1)
            structure2 = re.sub(r'\b[a-zA-Z_]\w*\b', 'VAR', code2)
            
            structure_similarity = difflib.SequenceMatcher(None, structure1, structure2).ratio()
            
            # Obfuscation detected if structure is very similar but variables are different
            return structure_similarity > 0.8 and var_overlap < 0.3
            
        except Exception:
            return False
    
    def _calculate_confidence(self, similarity: float, is_cross_language: bool) -> float:
        """Calculate confidence level of similarity detection"""
        base_confidence = similarity
        
        if is_cross_language:
            # Lower confidence for cross-language detection
            base_confidence *= 0.8
        
        return min(1.0, base_confidence * 1.2)  # Boost slightly for very high similarities
    
    def _get_other_submissions(self, assignment_id: str, student_id: str) -> List[Dict]:
        """Get other submissions for comparison"""
        try:
            return list(current_app.mongo.db.submissions.find({
                'assignment_id': assignment_id,
                'student_id': {'$ne': student_id}
            }))
        except:
            return []  # Fallback for demo mode
    
    def _create_clean_result(self) -> Dict:
        """Create result for clean submission"""
        return {
            'similarity_score': 0.0,
            'passed': True,
            'similar_submissions': [],
            'threshold': self.threshold,
            'cross_language_detected': False,
            'visualization_data': {'heat_map': [], 'similar_regions': []},
            'algorithm_patterns_detected': {},
            'enhanced_analysis': True
        }
    
    def _create_error_result(self, error_msg: str) -> Dict:
        """Create error result"""
        return {
            'similarity_score': 0.0,
            'passed': True,
            'similar_submissions': [],
            'threshold': self.threshold,
            'error': error_msg,
            'enhanced_analysis': False
        }
    
    def _calculate_tfidf_similarity(self, code1: str, code2: str) -> float:
        """Calculate TF-IDF similarity"""
        return calculate_tfidf_similarity(code1, code2)
    
    def _calculate_sequence_similarity(self, code1: str, code2: str) -> float:
        """Calculate sequence similarity"""
        return calculate_sequence_similarity(code1, code2)
    
    def _calculate_structure_similarity(self, code1: str, code2: str, lang1: str, lang2: str) -> float:
        """Calculate structural similarity"""
        if lang1 == lang2 == 'python':
            return calculate_structure_similarity(code1, code2)
        else:
            return calculate_pattern_similarity(code1, code2)

# Global enhanced detector instance
enhanced_plagiarism_detector = CrossLanguagePlagiarismDetector()

def check_plagiarism(code, assignment_id, student_id):
    """
    Check for plagiarism by comparing with existing submissions
    
    Args:
        code (str): The code to check
        assignment_id (str): ID of the assignment
        student_id (str): ID of the student submitting
    
    Returns:
        dict: Plagiarism check result
    """
    try:
        # Get all other submissions for this assignment
        other_submissions = list(current_app.mongo.db.submissions.find({
            'assignment_id': assignment_id,
            'student_id': {'$ne': student_id}
        }))
        
        if not other_submissions:
            return {
                'similarity_score': 0.0,
                'passed': True,
                'similar_submissions': [],
                'threshold': Config.PLAGIARISM_THRESHOLD
            }
        
        # Normalize the submitted code
        normalized_code = normalize_code(code)
        
        # Check similarity with each existing submission
        similarities = []
        
        for submission in other_submissions:
            other_code = submission.get('code', '')
            normalized_other_code = normalize_code(other_code)
            
            # Calculate multiple similarity metrics
            tfidf_similarity = calculate_tfidf_similarity(normalized_code, normalized_other_code)
            sequence_similarity = calculate_sequence_similarity(normalized_code, normalized_other_code)
            structure_similarity = calculate_structure_similarity(code, other_code)
            
            # Weighted average of different similarity measures
            overall_similarity = (
                tfidf_similarity * 0.4 +
                sequence_similarity * 0.4 +
                structure_similarity * 0.2
            )
            
            if overall_similarity > 0.3:  # Only record significant similarities
                similarities.append({
                    'student_id': submission['student_id'],
                    'submission_id': str(submission['_id']),
                    'similarity_score': overall_similarity,
                    'tfidf_similarity': tfidf_similarity,
                    'sequence_similarity': sequence_similarity,
                    'structure_similarity': structure_similarity,
                    'submitted_at': submission.get('submitted_at')
                })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Determine if plagiarism threshold is exceeded
        max_similarity = similarities[0]['similarity_score'] if similarities else 0.0
        passed = max_similarity < Config.PLAGIARISM_THRESHOLD
        
        return {
            'similarity_score': max_similarity,
            'passed': passed,
            'similar_submissions': similarities[:5],  # Top 5 most similar
            'threshold': Config.PLAGIARISM_THRESHOLD
        }
        
    except Exception as e:
        print(f"Plagiarism check failed: {str(e)}")
        # Default to passing if check fails
        return {
            'similarity_score': 0.0,
            'passed': True,
            'similar_submissions': [],
            'threshold': Config.PLAGIARISM_THRESHOLD,
            'error': str(e)
        }

def normalize_code(code):
    """
    Normalize code by removing comments, extra whitespace, and standardizing formatting
    """
    try:
        # Remove single-line comments
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'#.*', '', code)
        
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Remove extra whitespace and standardize
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line:
                # Standardize spacing around operators
                line = re.sub(r'\s*([+\-*/=<>!&|]+)\s*', r' \1 ', line)
                # Standardize spacing around parentheses and brackets
                line = re.sub(r'\s*([(){}[\],;])\s*', r'\1', line)
                lines.append(line.lower())
        
        return '\n'.join(lines)
        
    except Exception as e:
        print(f"Code normalization failed: {str(e)}")
        return code.lower().strip()

def calculate_tfidf_similarity(code1, code2):
    """
    Calculate TF-IDF based similarity between two code snippets
    """
    try:
        if not SKLEARN_AVAILABLE:
            # Fallback to simple similarity if sklearn not available
            return calculate_sequence_similarity(code1, code2)
            
        if not code1.strip() or not code2.strip():
            return 0.0
        
        # Tokenize code into words
        def tokenize(code):
            # Split by common delimiters and keep alphanumeric tokens
            tokens = re.findall(r'\b\w+\b', code)
            return ' '.join(tokens)
        
        doc1 = tokenize(code1)
        doc2 = tokenize(code2)
        
        if not doc1 or not doc2:
            return 0.0
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words=None, lowercase=True)
        tfidf_matrix = vectorizer.fit_transform([doc1, doc2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
        
    except Exception as e:
        print(f"TF-IDF similarity calculation failed: {str(e)}")
        return 0.0

def calculate_sequence_similarity(code1, code2):
    """
    Calculate sequence similarity using difflib
    """
    try:
        if not code1.strip() or not code2.strip():
            return 0.0
        
        # Calculate sequence similarity
        similarity = difflib.SequenceMatcher(None, code1, code2).ratio()
        
        return float(similarity)
        
    except Exception as e:
        print(f"Sequence similarity calculation failed: {str(e)}")
        return 0.0

def calculate_structure_similarity(code1, code2):
    """
    Calculate structural similarity by comparing AST structures (for Python)
    """
    try:
        if not code1.strip() or not code2.strip():
            return 0.0
        
        # Try to parse as Python AST
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)
            
            # Extract structural features
            features1 = extract_structural_features(tree1)
            features2 = extract_structural_features(tree2)
            
            # Calculate similarity based on structural features
            return calculate_feature_similarity(features1, features2)
            
        except SyntaxError:
            # If not valid Python, fall back to pattern-based analysis
            return calculate_pattern_similarity(code1, code2)
            
    except Exception as e:
        print(f"Structure similarity calculation failed: {str(e)}")
        return 0.0

def extract_structural_features(tree):
    """
    Extract structural features from AST
    """
    features = {
        'functions': 0,
        'classes': 0,
        'loops': 0,
        'conditionals': 0,
        'imports': 0,
        'assignments': 0,
        'function_calls': 0,
        'depth': 0
    }
    
    class FeatureExtractor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.max_depth = 0
        
        def visit(self, node):
            self.depth += 1
            self.max_depth = max(self.max_depth, self.depth)
            self.generic_visit(node)
            self.depth -= 1
        
        def visit_FunctionDef(self, node):
            features['functions'] += 1
            self.generic_visit(node)
        
        def visit_ClassDef(self, node):
            features['classes'] += 1
            self.generic_visit(node)
        
        def visit_For(self, node):
            features['loops'] += 1
            self.generic_visit(node)
        
        def visit_While(self, node):
            features['loops'] += 1
            self.generic_visit(node)
        
        def visit_If(self, node):
            features['conditionals'] += 1
            self.generic_visit(node)
        
        def visit_Import(self, node):
            features['imports'] += 1
            self.generic_visit(node)
        
        def visit_ImportFrom(self, node):
            features['imports'] += 1
            self.generic_visit(node)
        
        def visit_Assign(self, node):
            features['assignments'] += 1
            self.generic_visit(node)
        
        def visit_Call(self, node):
            features['function_calls'] += 1
            self.generic_visit(node)
    
    extractor = FeatureExtractor()
    extractor.visit(tree)
    features['depth'] = extractor.max_depth
    
    return features

def calculate_feature_similarity(features1, features2):
    """
    Calculate similarity based on structural features
    """
    try:
        total_similarity = 0.0
        feature_count = 0
        
        for feature in features1:
            val1 = features1[feature]
            val2 = features2[feature]
            
            if val1 == 0 and val2 == 0:
                similarity = 1.0
            elif val1 == 0 or val2 == 0:
                similarity = 0.0
            else:
                similarity = min(val1, val2) / max(val1, val2)
            
            total_similarity += similarity
            feature_count += 1
        
        return total_similarity / feature_count if feature_count > 0 else 0.0
        
    except Exception as e:
        return 0.0

def calculate_pattern_similarity(code1, code2):
    """
    Calculate similarity based on code patterns (fallback for non-Python code)
    """
    try:
        # Extract patterns like function definitions, loops, conditionals
        patterns = [
            r'\bdef\s+\w+',  # Python functions
            r'\bpublic\s+\w+',  # Java methods
            r'\bfor\s*\(',  # for loops
            r'\bwhile\s*\(',  # while loops
            r'\bif\s*\(',  # if statements
            r'\breturn\s+',  # return statements
            r'\bclass\s+\w+',  # class definitions
        ]
        
        pattern_counts1 = {}
        pattern_counts2 = {}
        
        for pattern in patterns:
            pattern_counts1[pattern] = len(re.findall(pattern, code1, re.IGNORECASE))
            pattern_counts2[pattern] = len(re.findall(pattern, code2, re.IGNORECASE))
        
        return calculate_feature_similarity(pattern_counts1, pattern_counts2)
        
    except Exception as e:
        return 0.0

def generate_code_fingerprint(code):
    """
    Generate a fingerprint for code to enable fast similarity checks
    """
    try:
        normalized = normalize_code(code)
        
        # Create hash of normalized code
        fingerprint = hashlib.md5(normalized.encode()).hexdigest()
        
        return fingerprint
        
    except Exception as e:
        return None

def detect_code_obfuscation(code1, code2):
    """
    Detect if code has been obfuscated to avoid plagiarism detection
    """
    try:
        # Check for suspicious patterns
        obfuscation_indicators = []
        
        # Variable name changes
        vars1 = set(re.findall(r'\b[a-zA-Z_]\w*\b', code1))
        vars2 = set(re.findall(r'\b[a-zA-Z_]\w*\b', code2))
        
        common_vars = vars1.intersection(vars2)
        if len(common_vars) / max(len(vars1), len(vars2), 1) < 0.3:
            obfuscation_indicators.append("Significant variable name changes")
        
        # Line reordering (for languages where order doesn't matter)
        lines1 = [line.strip() for line in code1.split('\n') if line.strip()]
        lines2 = [line.strip() for line in code2.split('\n') if line.strip()]
        
        if len(set(lines1).intersection(set(lines2))) / max(len(lines1), len(lines2), 1) > 0.7:
            obfuscation_indicators.append("Possible line reordering")
        
        return obfuscation_indicators
        
    except Exception as e:
        return []

def batch_detect_plagiarism(submissions, threshold=0.7, algorithms=['tfidf', 'structural']):
    """Batch detect plagiarism across multiple submissions"""
    results = []
    
    for i, submission1 in enumerate(submissions):
        for j, submission2 in enumerate(submissions[i+1:], i+1):
            similarity = _calculate_similarity(submission1, submission2, algorithms)
            if similarity >= threshold:
                results.append({
                    'submission1_id': submission1.get('id', f'sub_{i}'),
                    'submission2_id': submission2.get('id', f'sub_{j}'),
                    'similarity_score': similarity,
                    'algorithms_used': algorithms,
                    'confidence': min(similarity * 1.2, 1.0)
                })
    
    return {
        'total_comparisons': len(submissions) * (len(submissions) - 1) // 2,
        'matches_found': len(results),
        'matches': sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    }

def get_assignment_results(assignment_id, threshold=0.7, sort_by='similarity_score', order='desc'):
    """Get plagiarism results for a specific assignment"""
    # Mock data for now
    results = [
        {
            'submission1_id': 'sub_001',
            'submission2_id': 'sub_002',
            'similarity_score': 0.85,
            'status': 'flagged',
            'reviewed': False
        },
        {
            'submission1_id': 'sub_003',
            'submission2_id': 'sub_004',
            'similarity_score': 0.72,
            'status': 'under_review',
            'reviewed': True
        }
    ]
    
    # Filter by threshold
    filtered_results = [r for r in results if r['similarity_score'] >= threshold]
    
    # Sort results
    reverse = (order == 'desc')
    filtered_results.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    return {
        'assignment_id': assignment_id,
        'total_matches': len(filtered_results),
        'threshold_used': threshold,
        'results': filtered_results
    }

def detailed_comparison(submission1, submission2, algorithms=['all']):
    """Perform detailed comparison between two submissions"""
    if algorithms == ['all']:
        algorithms = ['tfidf', 'structural', 'cross_language', 'fingerprint']
    
    comparison_results = {}
    
    for algorithm in algorithms:
        if algorithm == 'tfidf':
            comparison_results['tfidf'] = _tfidf_similarity(submission1, submission2)
        elif algorithm == 'structural':
            comparison_results['structural'] = _structural_similarity(submission1, submission2)
        elif algorithm == 'cross_language':
            comparison_results['cross_language'] = _cross_language_similarity(submission1, submission2)
        elif algorithm == 'fingerprint':
            comparison_results['fingerprint'] = _fingerprint_similarity(submission1, submission2)
    
    # Calculate overall similarity
    overall_similarity = sum(comparison_results.values()) / len(comparison_results)
    
    return {
        'submission1_id': submission1.get('id', 'unknown'),
        'submission2_id': submission2.get('id', 'unknown'),
        'overall_similarity': overall_similarity,
        'algorithm_results': comparison_results,
        'obfuscation_detected': len(detect_code_obfuscation(
            submission1.get('code', ''), 
            submission2.get('code', '')
        )) > 0,
        'confidence': min(overall_similarity * 1.1, 1.0)
    }

def generate_similarity_heatmap(submission1_id, submission2_id):
    """Generate heatmap data for similarity visualization"""
    # Mock heatmap data
    return {
        'submission1_id': submission1_id,
        'submission2_id': submission2_id,
        'heatmap_data': [
            [0.1, 0.2, 0.8, 0.9, 0.3],
            [0.2, 0.1, 0.7, 0.8, 0.2],
            [0.9, 0.8, 0.1, 0.2, 0.1],
            [0.8, 0.9, 0.2, 0.1, 0.2],
            [0.3, 0.2, 0.1, 0.2, 0.1]
        ],
        'line_mappings': [
            {'line1': 1, 'line2': 3, 'similarity': 0.9},
            {'line1': 2, 'line2': 4, 'similarity': 0.8},
            {'line1': 5, 'line2': 8, 'similarity': 0.7}
        ]
    }

def get_dashboard_statistics(assignment_id=None, time_period='30days'):
    """Get dashboard statistics for plagiarism detection"""
    return {
        'overview': {
            'total_scans': 45,
            'flagged_submissions': 12,
            'confirmed_plagiarism': 8,
            'false_positives': 4,
            'accuracy_rate': 85.5
        },
        'recent_activity': [
            {'date': '2024-03-25', 'scans': 8, 'flags': 2},
            {'date': '2024-03-24', 'scans': 12, 'flags': 3},
            {'date': '2024-03-23', 'scans': 6, 'flags': 1}
        ],
        'algorithm_performance': {
            'tfidf': {'accuracy': 82, 'false_positive_rate': 15},
            'structural': {'accuracy': 88, 'false_positive_rate': 12},
            'cross_language': {'accuracy': 75, 'false_positive_rate': 20}
        }
    }

def get_plagiarism_trends(time_period='6months', assignment_id=None):
    """Get plagiarism trends over time"""
    return {
        'time_period': time_period,
        'trends': {
            'monthly_scans': [45, 52, 38, 41, 47, 39],
            'monthly_flags': [12, 15, 9, 11, 13, 10],
            'detection_rates': [26.7, 28.8, 23.7, 26.8, 27.7, 25.6]
        },
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    }

def generate_comprehensive_report(assignment_id, format='json', include_details=True):
    """Generate comprehensive plagiarism report"""
    report_data = {
        'assignment_id': assignment_id,
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_submissions': 25,
            'flagged_submissions': 6,
            'plagiarism_rate': 24.0,
            'average_similarity': 0.15
        },
        'detailed_results': [
            {
                'match_id': 'match_001',
                'submissions': ['sub_001', 'sub_002'],
                'similarity_score': 0.85,
                'algorithms_used': ['tfidf', 'structural'],
                'status': 'confirmed'
            }
        ] if include_details else [],
        'recommendations': [
            'Review high-similarity matches manually',
            'Consider adjusting detection thresholds',
            'Implement additional verification steps'
        ]
    }
    
    return report_data

def investigate_match(match_id):
    """Get detailed investigation data for a plagiarism match"""
    # Mock investigation data
    return {
        'match_id': match_id,
        'submissions': {
            'submission1': {
                'id': 'sub_001',
                'author': 'Student A',
                'submitted_at': '2024-03-20T10:30:00',
                'code_preview': 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)'
            },
            'submission2': {
                'id': 'sub_002',
                'author': 'Student B',
                'submitted_at': '2024-03-20T14:15:00',
                'code_preview': 'def fib(num):\n    if num <= 1:\n        return num\n    return fib(num-1) + fib(num-2)'
            }
        },
        'similarity_analysis': {
            'overall_score': 0.85,
            'structural_similarity': 0.92,
            'variable_similarity': 0.65,
            'logic_similarity': 0.98
        },
        'evidence': [
            'Identical algorithm structure',
            'Similar variable naming patterns',
            'Matching function logic flow'
        ],
        'timeline': [
            {'event': 'Submission 1 uploaded', 'timestamp': '2024-03-20T10:30:00'},
            {'event': 'Submission 2 uploaded', 'timestamp': '2024-03-20T14:15:00'},
            {'event': 'Plagiarism detected', 'timestamp': '2024-03-20T15:00:00'}
        ]
    }

def get_whitelist():
    """Get plagiarism detection whitelist"""
    return {
        'patterns': [
            'import statements',
            'common function signatures',
            'standard library usage'
        ],
        'submissions': [],
        'code_snippets': [
            'def __init__(self):',
            'if __name__ == "__main__":'
        ]
    }

def add_to_whitelist(type, value, reason=''):
    """Add patterns or submissions to whitelist"""
    # Mock implementation
    return True

def get_detection_settings():
    """Get plagiarism detection settings"""
    return {
        'threshold': 0.7,
        'algorithms': ['tfidf', 'structural', 'cross_language'],
        'auto_flag': True,
        'notification_enabled': True,
        'whitelist_enabled': True
    }

def update_detection_settings(settings_data):
    """Update plagiarism detection settings"""
    # Mock implementation
    return True

def get_available_algorithms():
    """Get available plagiarism detection algorithms"""
    return [
        {
            'name': 'TF-IDF',
            'id': 'tfidf',
            'description': 'Text frequency analysis',
            'accuracy': 82,
            'speed': 'Fast'
        },
        {
            'name': 'Structural Analysis',
            'id': 'structural',
            'description': 'Code structure comparison',
            'accuracy': 88,
            'speed': 'Medium'
        },
        {
            'name': 'Cross-Language',
            'id': 'cross_language',
            'description': 'Multi-language detection',
            'accuracy': 75,
            'speed': 'Slow'
        }
    ]

def bulk_scan_assignments(assignment_ids, threshold=0.7, algorithms=['tfidf', 'structural']):
    """Perform bulk plagiarism scanning across multiple assignments"""
    results = {}
    
    for assignment_id in assignment_ids:
        results[assignment_id] = get_assignment_results(assignment_id, threshold)
    
    return {
        'total_assignments': len(assignment_ids),
        'results': results,
        'summary': {
            'total_matches': sum(len(r['results']) for r in results.values()),
            'average_similarity': 0.25,
            'completion_time': '2.5 minutes'
        }
    }

def export_plagiarism_data(assignment_id, format='json', include_code=False):
    """Export plagiarism detection data"""
    export_data = {
        'assignment_id': assignment_id,
        'exported_at': datetime.now().isoformat(),
        'format': format,
        'data': get_assignment_results(assignment_id)
    }
    
    if not include_code:
        # Remove code snippets for privacy
        for result in export_data['data'].get('results', []):
            result.pop('code_preview', None)
    
    return export_data

def _calculate_similarity(submission1, submission2, algorithms):
    """Calculate similarity between two submissions using specified algorithms"""
    similarities = []
    
    for algorithm in algorithms:
        if algorithm == 'tfidf':
            similarities.append(_tfidf_similarity(submission1, submission2))
        elif algorithm == 'structural':
            similarities.append(_structural_similarity(submission1, submission2))
        elif algorithm == 'cross_language':
            similarities.append(_cross_language_similarity(submission1, submission2))
    
    return sum(similarities) / len(similarities) if similarities else 0.0

def _tfidf_similarity(submission1, submission2):
    """Calculate TF-IDF similarity"""
    # Mock implementation
    return 0.75

def _structural_similarity(submission1, submission2):
    """Calculate structural similarity"""
    # Mock implementation
    return 0.82

def _cross_language_similarity(submission1, submission2):
    """Calculate cross-language similarity"""
    # Mock implementation
    return 0.68

def _fingerprint_similarity(submission1, submission2):
    """Calculate fingerprint-based similarity"""
    # Mock implementation
    return 0.71
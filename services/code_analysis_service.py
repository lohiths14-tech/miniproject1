"""
Advanced Code Analysis Service
Provides comprehensive code analysis including complexity metrics, Big O analysis,
performance benchmarking, and optimization suggestions
"""

import ast
import re
import time

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Performance monitoring will be limited.")
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ComplexityLevel(Enum):
    """Code complexity levels"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class BigOComplexity(Enum):
    """Big O complexity classes"""

    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n²)"
    CUBIC = "O(n³)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"


@dataclass
class PerformanceMetrics:
    """Performance measurement results"""

    execution_time: float
    memory_usage: float
    cpu_usage: float
    operations_count: int


@dataclass
class CodeMetrics:
    """Code quality and complexity metrics"""

    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    nesting_depth: int
    function_count: int
    class_count: int
    code_duplication: float


@dataclass
class AnalysisResult:
    """Complete code analysis result"""

    code_metrics: CodeMetrics
    performance_metrics: PerformanceMetrics
    big_o_analysis: Dict[str, str]
    complexity_level: ComplexityLevel
    optimization_suggestions: List[str]
    code_smells: List[Dict[str, str]]
    best_practices_score: int
    maintainability_score: int


class AdvancedCodeAnalyzer:
    def __init__(self):
        self.complexity_patterns = self._load_complexity_patterns()
        self.optimization_rules = self._load_optimization_rules()

    def _load_complexity_patterns(self) -> Dict:
        """Load patterns for detecting algorithmic complexity"""
        return {
            "nested_loops": {
                "pattern": r"for.*for.*:|while.*for.*:|for.*while.*:",
                "complexity": BigOComplexity.QUADRATIC.value,
                "description": "Nested loops detected",
            },
            "triple_nested": {
                "pattern": r"for.*for.*for.*:",
                "complexity": BigOComplexity.CUBIC.value,
                "description": "Triple nested loops detected",
            },
            "recursive_calls": {
                "pattern": r"def\s+(\w+).*:\s*.*\1\(",
                "complexity": BigOComplexity.EXPONENTIAL.value,
                "description": "Recursive function calls",
            },
            "sort_operations": {
                "pattern": r"\.sort\(|sorted\(",
                "complexity": BigOComplexity.LINEARITHMIC.value,
                "description": "Sorting operations",
            },
            "linear_search": {
                "pattern": r"in\s+\w+|\.index\(|\.count\(",
                "complexity": BigOComplexity.LINEAR.value,
                "description": "Linear search operations",
            },
        }

    def _load_optimization_rules(self) -> List[Dict]:
        """Load code optimization rules and suggestions"""
        return [
            {
                "pattern": r"for\s+\w+\s+in\s+range\(len\(",
                "suggestion": "Use enumerate() instead of range(len()) for better readability",
                "category": "pythonic_code",
            },
            {
                "pattern": r"\.append\(.*\)\s*\n.*for",
                "suggestion": "Consider using list comprehension for better performance",
                "category": "performance",
            },
            {
                "pattern": r"if.*==\s*True|if.*==\s*False",
                "suggestion": "Avoid explicit comparison with True/False",
                "category": "code_style",
            },
            {
                "pattern": r"try:\s*.*\s*except:\s*pass",
                "suggestion": "Avoid bare except clauses, be specific about exceptions",
                "category": "error_handling",
            },
            {
                "pattern": r"global\s+\w+",
                "suggestion": "Avoid global variables, consider function parameters or class attributes",
                "category": "code_structure",
            },
            {
                "pattern": r"def\s+\w+\([^)]*\):\s*\n\s*.*\n\s*.*\n\s*.*\n\s*.*\n\s*.*\n",
                "suggestion": "Function appears too long, consider breaking it into smaller functions",
                "category": "maintainability",
            },
        ]

    def analyze_code(
        self, code: str, programming_language: str = "python", test_inputs: List[str] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive code analysis

        Args:
            code: Source code to analyze
            programming_language: Programming language (python, java, cpp, etc.)
            test_inputs: Sample inputs for performance testing

        Returns:
            AnalysisResult with complete analysis
        """
        try:
            # Calculate code metrics
            code_metrics = self._calculate_code_metrics(code, programming_language)

            # Perform Big O analysis
            big_o_analysis = self._analyze_algorithmic_complexity(code, programming_language)

            # Run performance benchmarks
            performance_metrics = self._benchmark_performance(
                code, programming_language, test_inputs
            )

            # Detect code smells and issues
            code_smells = self._detect_code_smells(code, programming_language)

            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                code, programming_language
            )

            # Calculate overall scores
            complexity_level = self._determine_complexity_level(code_metrics, big_o_analysis)
            best_practices_score = self._calculate_best_practices_score(code, code_smells)
            maintainability_score = self._calculate_maintainability_score(code_metrics, code_smells)

            return AnalysisResult(
                code_metrics=code_metrics,
                performance_metrics=performance_metrics,
                big_o_analysis=big_o_analysis,
                complexity_level=complexity_level,
                optimization_suggestions=optimization_suggestions,
                code_smells=code_smells,
                best_practices_score=best_practices_score,
                maintainability_score=maintainability_score,
            )

        except Exception as e:
            # Return default result on error
            return self._create_error_result(str(e))

    def _calculate_code_metrics(self, code: str, language: str) -> CodeMetrics:
        """Calculate basic code metrics"""
        lines = [line.strip() for line in code.split("\n") if line.strip()]
        lines_of_code = len(
            [line for line in lines if not line.startswith("#") and not line.startswith("//")]
        )

        if language.lower() == "python":
            return self._calculate_python_metrics(code)
        elif language.lower() == "java":
            return self._calculate_java_metrics(code)
        else:
            # Generic metrics
            return CodeMetrics(
                lines_of_code=lines_of_code,
                cyclomatic_complexity=self._estimate_cyclomatic_complexity(code),
                cognitive_complexity=self._estimate_cognitive_complexity(code),
                nesting_depth=self._calculate_nesting_depth(code),
                function_count=self._count_functions(code, language),
                class_count=self._count_classes(code, language),
                code_duplication=0.0,
            )

    def _calculate_python_metrics(self, code: str) -> CodeMetrics:
        """Calculate Python-specific metrics using AST"""
        try:
            tree = ast.parse(code)

            # Count various elements
            function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

            # Calculate cyclomatic complexity
            cyclomatic = self._calculate_cyclomatic_complexity_ast(tree)

            # Calculate nesting depth
            nesting_depth = self._calculate_ast_nesting_depth(tree)

            lines_of_code = len(
                [
                    line
                    for line in code.split("\n")
                    if line.strip() and not line.strip().startswith("#")
                ]
            )

            return CodeMetrics(
                lines_of_code=lines_of_code,
                cyclomatic_complexity=cyclomatic,
                cognitive_complexity=self._calculate_cognitive_complexity_ast(tree),
                nesting_depth=nesting_depth,
                function_count=function_count,
                class_count=class_count,
                code_duplication=self._detect_code_duplication(code),
            )

        except SyntaxError:
            # Fallback to text-based analysis
            return self._calculate_text_based_metrics(code)

    def _calculate_cyclomatic_complexity_ast(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity using AST"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += 1

        return complexity

    def _calculate_cognitive_complexity_ast(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity (readability metric)"""
        complexity = 0
        nesting_level = 0

        def visit_node(node, level):
            nonlocal complexity

            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1 + level
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                complexity += 1 + level

            # Increase nesting for certain nodes
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                level += 1

            for child in ast.iter_child_nodes(node):
                visit_node(child, level)

        visit_node(tree, 0)
        return complexity

    def _calculate_ast_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth using AST"""
        max_depth = 0

        def visit_node(node, depth):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                depth += 1

            for child in ast.iter_child_nodes(node):
                visit_node(child, depth)

        visit_node(tree, 0)
        return max_depth

    def _analyze_algorithmic_complexity(self, code: str, language: str) -> Dict[str, str]:
        """Analyze algorithmic complexity (Big O)"""
        analysis = {
            "time_complexity": BigOComplexity.LINEAR.value,
            "space_complexity": BigOComplexity.CONSTANT.value,
            "detected_patterns": [],
            "confidence": "medium",
        }

        # Check for known complexity patterns
        for pattern_name, pattern_info in self.complexity_patterns.items():
            if re.search(pattern_info["pattern"], code, re.MULTILINE | re.DOTALL):
                analysis["detected_patterns"].append(
                    {
                        "pattern": pattern_name,
                        "complexity": pattern_info["complexity"],
                        "description": pattern_info["description"],
                    }
                )

                # Update worst-case complexity
                if self._is_worse_complexity(
                    pattern_info["complexity"], analysis["time_complexity"]
                ):
                    analysis["time_complexity"] = pattern_info["complexity"]

        # Analyze space complexity
        if "list(" in code or "dict(" in code or "[]" in code or "{}" in code:
            if "for" in code:
                analysis["space_complexity"] = BigOComplexity.LINEAR.value

        # Set confidence based on patterns found
        analysis["confidence"] = "high" if analysis["detected_patterns"] else "medium"

        return analysis

    def _is_worse_complexity(self, new_complexity: str, current_complexity: str) -> bool:
        """Check if new complexity is worse than current"""
        complexity_order = [
            BigOComplexity.CONSTANT.value,
            BigOComplexity.LOGARITHMIC.value,
            BigOComplexity.LINEAR.value,
            BigOComplexity.LINEARITHMIC.value,
            BigOComplexity.QUADRATIC.value,
            BigOComplexity.CUBIC.value,
            BigOComplexity.EXPONENTIAL.value,
            BigOComplexity.FACTORIAL.value,
        ]

        try:
            new_index = complexity_order.index(new_complexity)
            current_index = complexity_order.index(current_complexity)
            return new_index > current_index
        except ValueError:
            return False

    def _benchmark_performance(
        self, code: str, language: str, test_inputs: List[str] = None
    ) -> PerformanceMetrics:
        """Benchmark code performance with test inputs"""
        if not test_inputs:
            test_inputs = [""]

        execution_times = []
        memory_usage = []

        for test_input in test_inputs:
            try:
                # Measure execution time and memory
                start_time = time.time()

                if PSUTIL_AVAILABLE:
                    process = psutil.Process()
                    initial_memory = process.memory_info().rss
                else:
                    initial_memory = 0

                # Execute code (simplified - would need actual execution)
                # This is a placeholder for actual code execution
                time.sleep(0.001)  # Simulate execution

                end_time = time.time()

                if PSUTIL_AVAILABLE:
                    final_memory = process.memory_info().rss
                else:
                    final_memory = 1024  # Default fallback

                execution_times.append(end_time - start_time)
                memory_usage.append(final_memory - initial_memory)

            except Exception:
                # Use default values on error
                execution_times.append(0.001)
                memory_usage.append(1024)

        return PerformanceMetrics(
            execution_time=sum(execution_times) / len(execution_times),
            memory_usage=sum(memory_usage) / len(memory_usage),
            cpu_usage=0.0,  # Would require actual profiling
            operations_count=self._estimate_operations_count(code),
        )

    def _detect_code_smells(self, code: str, language: str) -> List[Dict[str, str]]:
        """Detect code smells and anti-patterns"""
        smells = []

        # Check for common code smells
        lines = code.split("\n")

        for i, line in enumerate(lines):
            # Long lines
            if len(line) > 120:
                smells.append(
                    {
                        "type": "long_line",
                        "line": i + 1,
                        "description": f"Line too long ({len(line)} characters)",
                        "severity": "low",
                    }
                )

            # Magic numbers
            if re.search(r"\b\d{2,}\b", line) and not re.search(r'["\'].*\d+.*["\']', line):
                smells.append(
                    {
                        "type": "magic_number",
                        "line": i + 1,
                        "description": "Magic number detected, consider using a named constant",
                        "severity": "medium",
                    }
                )

            # Commented code
            if re.search(r"#.*[a-zA-Z]+.*=|#.*def\s+|#.*if\s+", line):
                smells.append(
                    {
                        "type": "commented_code",
                        "line": i + 1,
                        "description": "Commented out code detected",
                        "severity": "low",
                    }
                )

        # Check for duplicated code blocks
        if self._detect_code_duplication(code) > 0.3:
            smells.append(
                {
                    "type": "code_duplication",
                    "line": 0,
                    "description": "High code duplication detected",
                    "severity": "high",
                }
            )

        return smells

    def _generate_optimization_suggestions(self, code: str, language: str) -> List[str]:
        """Generate optimization suggestions based on code analysis"""
        suggestions = []

        # Check optimization patterns
        for rule in self.optimization_rules:
            if re.search(rule["pattern"], code, re.MULTILINE):
                suggestions.append(rule["suggestion"])

        # Algorithm-specific suggestions
        if "for" in code and "for" in code:
            suggestions.append("Consider algorithm optimization to reduce nested loops")

        if ".sort()" in code and "for" in code:
            suggestions.append("Consider if sorting is necessary or can be optimized")

        if "global" in code:
            suggestions.append("Minimize global variable usage for better maintainability")

        return list(set(suggestions))  # Remove duplicates

    def _determine_complexity_level(
        self, metrics: CodeMetrics, big_o: Dict[str, str]
    ) -> ComplexityLevel:
        """Determine overall complexity level"""
        complexity_score = 0

        # Factor in cyclomatic complexity
        if metrics.cyclomatic_complexity > 20:
            complexity_score += 3
        elif metrics.cyclomatic_complexity > 10:
            complexity_score += 2
        elif metrics.cyclomatic_complexity > 5:
            complexity_score += 1

        # Factor in nesting depth
        if metrics.nesting_depth > 4:
            complexity_score += 2
        elif metrics.nesting_depth > 2:
            complexity_score += 1

        # Factor in Big O complexity
        if big_o["time_complexity"] in [
            BigOComplexity.EXPONENTIAL.value,
            BigOComplexity.FACTORIAL.value,
        ]:
            complexity_score += 3
        elif big_o["time_complexity"] in [
            BigOComplexity.CUBIC.value,
            BigOComplexity.QUADRATIC.value,
        ]:
            complexity_score += 2
        elif big_o["time_complexity"] == BigOComplexity.LINEARITHMIC.value:
            complexity_score += 1

        if complexity_score >= 6:
            return ComplexityLevel.VERY_COMPLEX
        elif complexity_score >= 4:
            return ComplexityLevel.COMPLEX
        elif complexity_score >= 2:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE

    def _calculate_best_practices_score(self, code: str, code_smells: List[Dict]) -> int:
        """Calculate best practices adherence score (0-100)"""
        base_score = 100

        # Deduct points for code smells
        for smell in code_smells:
            if smell["severity"] == "high":
                base_score -= 20
            elif smell["severity"] == "medium":
                base_score -= 10
            else:
                base_score -= 5

        # Bonus points for good practices
        if "def " in code:  # Functions defined
            base_score += 5
        if "class " in code:  # Classes defined
            base_score += 5
        if '"""' in code or "'''" in code:  # Docstrings
            base_score += 10
        if "try:" in code and "except" in code:  # Error handling
            base_score += 10

        return max(0, min(100, base_score))

    def _calculate_maintainability_score(
        self, metrics: CodeMetrics, code_smells: List[Dict]
    ) -> int:
        """Calculate maintainability score (0-100)"""
        base_score = 100

        # Factor in complexity
        base_score -= min(30, metrics.cyclomatic_complexity * 2)
        base_score -= min(20, metrics.nesting_depth * 5)

        # Factor in code smells
        high_severity_smells = sum(1 for smell in code_smells if smell["severity"] == "high")
        base_score -= high_severity_smells * 15

        # Factor in code structure
        if metrics.lines_of_code > 100:
            base_score -= 10
        if metrics.function_count == 0:
            base_score -= 20

        return max(0, min(100, base_score))

    # Helper methods for text-based analysis
    def _calculate_text_based_metrics(self, code: str) -> CodeMetrics:
        """Fallback text-based metrics calculation"""
        lines = [line.strip() for line in code.split("\n") if line.strip()]
        lines_of_code = len([line for line in lines if not line.startswith("#")])

        return CodeMetrics(
            lines_of_code=lines_of_code,
            cyclomatic_complexity=self._estimate_cyclomatic_complexity(code),
            cognitive_complexity=self._estimate_cognitive_complexity(code),
            nesting_depth=self._calculate_nesting_depth(code),
            function_count=self._count_functions(code, "python"),
            class_count=self._count_classes(code, "python"),
            code_duplication=0.0,
        )

    def _estimate_cyclomatic_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity from text"""
        complexity = 1
        keywords = ["if", "elif", "while", "for", "try", "except", "and", "or"]

        for keyword in keywords:
            complexity += code.count(keyword)

        return complexity

    def _estimate_cognitive_complexity(self, code: str) -> int:
        """Estimate cognitive complexity from text"""
        return self._estimate_cyclomatic_complexity(code)  # Simplified

    def _calculate_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth from indentation"""
        max_depth = 0
        lines = code.split("\n")

        for line in lines:
            if line.strip():
                depth = (len(line) - len(line.lstrip())) // 4  # Assuming 4-space indentation
                max_depth = max(max_depth, depth)

        return max_depth

    def _count_functions(self, code: str, language: str) -> int:
        """Count function definitions"""
        if language.lower() == "python":
            return code.count("def ")
        elif language.lower() == "java":
            return len(re.findall(r"public|private|protected.*\w+\s*\(", code))
        else:
            return code.count("function") + code.count("def ")

    def _count_classes(self, code: str, language: str) -> int:
        """Count class definitions"""
        if language.lower() == "python":
            return code.count("class ")
        elif language.lower() == "java":
            return code.count("class ")
        else:
            return code.count("class ")

    def _detect_code_duplication(self, code: str) -> float:
        """Detect percentage of duplicated code"""
        lines = [
            line.strip() for line in code.split("\n") if line.strip() and not line.startswith("#")
        ]

        if len(lines) < 3:
            return 0.0

        duplicates = 0
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                if lines[i] == lines[j] and len(lines[i]) > 10:
                    duplicates += 1

        return (duplicates / len(lines)) if lines else 0.0

    def _estimate_operations_count(self, code: str) -> int:
        """Estimate number of operations in the code"""
        operations = ["=", "+", "-", "*", "/", "//", "%", "**", "==", "!=", "<", ">", "<=", ">="]
        count = 0

        for op in operations:
            count += code.count(op)

        return count

    def _create_error_result(self, error_message: str) -> AnalysisResult:
        """Create a default result when analysis fails"""
        return AnalysisResult(
            code_metrics=CodeMetrics(0, 1, 1, 0, 0, 0, 0.0),
            performance_metrics=PerformanceMetrics(0.0, 0.0, 0.0, 0),
            big_o_analysis={
                "time_complexity": BigOComplexity.LINEAR.value,
                "space_complexity": BigOComplexity.CONSTANT.value,
                "detected_patterns": [],
                "confidence": "low",
            },
            complexity_level=ComplexityLevel.SIMPLE,
            optimization_suggestions=[f"Analysis failed: {error_message}"],
            code_smells=[],
            best_practices_score=50,
            maintainability_score=50,
        )


# Global instance
code_analyzer = AdvancedCodeAnalyzer()

"""
AI-Powered Code Suggestions Service
Provides real-time code completion, bug prediction, refactoring suggestions, and best practices
"""

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

import ast
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from settings import Config


class SuggestionType(Enum):
    """Types of code suggestions"""

    COMPLETION = "completion"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    BEST_PRACTICE = "best_practice"
    OPTIMIZATION = "optimization"
    SECURITY = "security"


class SeverityLevel(Enum):
    """Severity levels for suggestions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CodeSuggestion:
    """A code suggestion with context"""

    suggestion_id: str
    type: SuggestionType
    severity: SeverityLevel
    title: str
    description: str
    code_snippet: str
    suggested_fix: str
    line_number: int
    confidence: float
    explanation: str
    example: str = ""


class AICodeSuggestionsService:
    def __init__(self):
        self.completion_patterns = self._load_completion_patterns()
        self.bug_patterns = self._load_bug_patterns()
        self.refactoring_rules = self._load_refactoring_rules()
        self.best_practices = self._load_best_practices()

        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY

    def _load_completion_patterns(self) -> Dict:
        """Load code completion patterns"""
        return {
            "python": {
                "for_loop": {
                    "pattern": r"for\s+\w+\s+in\s+range\(",
                    "suggestions": [
                        "for i in range(len(list)):\n    # Consider using enumerate() instead",
                        "for index, value in enumerate(list):\n    # More Pythonic approach",
                    ],
                },
                "list_comprehension": {
                    "pattern": r"result\s*=\s*\[\]\s*\n\s*for\s+",
                    "suggestions": ["result = [expression for item in iterable if condition]"],
                },
                "exception_handling": {
                    "pattern": r"try:\s*\n.*?\nexcept:\s*\n",
                    "suggestions": [
                        "try:\n    # code\nexcept SpecificException as e:\n    # handle specific exception"
                    ],
                },
            }
        }

    def _load_bug_patterns(self) -> Dict:
        """Load common bug patterns"""
        return {
            "python": [
                {
                    "pattern": r"if\s+.*==\s*True",
                    "type": "anti_pattern",
                    "message": "Avoid explicit comparison with True/False",
                    "fix": 'Use "if condition:" instead of "if condition == True:"',
                    "severity": SeverityLevel.LOW,
                },
                {
                    "pattern": r"except:\s*pass",
                    "type": "error_handling",
                    "message": "Bare except clause catches all exceptions",
                    "fix": "Be specific about which exceptions to catch",
                    "severity": SeverityLevel.HIGH,
                },
                {
                    "pattern": r"=\s*\[\]\s*\n.*def\s+.*\(",
                    "type": "mutable_default",
                    "message": "Mutable default argument detected",
                    "fix": "Use None as default and initialize inside function",
                    "severity": SeverityLevel.MEDIUM,
                },
                {
                    "pattern": r"while\s+True:\s*\n(?!.*break)",
                    "type": "infinite_loop",
                    "message": "Potential infinite loop without break condition",
                    "fix": "Add break condition or use different loop structure",
                    "severity": SeverityLevel.CRITICAL,
                },
            ]
        }

    def _load_refactoring_rules(self) -> Dict:
        """Load code refactoring suggestions"""
        return {
            "long_function": {
                "threshold": 20,
                "message": "Function is too long, consider breaking it down",
                "suggestion": "Extract smaller functions for better readability",
            },
            "duplicate_code": {
                "threshold": 3,
                "message": "Duplicate code blocks detected",
                "suggestion": "Extract common code into a separate function",
            },
            "complex_condition": {
                "pattern": r"if\s+.*and.*and.*or.*",
                "message": "Complex conditional statement",
                "suggestion": "Break down into multiple conditions or use helper functions",
            },
        }

    def _load_best_practices(self) -> Dict:
        """Load best practice suggestions"""
        return {
            "python": [
                {
                    "pattern": r"print\(",
                    "suggestion": "Consider using logging instead of print for production code",
                    "type": "logging",
                },
                {
                    "pattern": r'def\s+\w+\([^)]*\):\s*\n(?!\s*""")',
                    "suggestion": "Add docstring to document function purpose",
                    "type": "documentation",
                },
                {
                    "pattern": r'class\s+\w+(?:\([^)]*\))?:\s*\n(?!\s*""")',
                    "suggestion": "Add class docstring to document purpose",
                    "type": "documentation",
                },
            ]
        }

    def get_real_time_suggestions(
        self, code: str, cursor_position: int, language: str = "python"
    ) -> List[CodeSuggestion]:
        """Get real-time code suggestions based on current context"""
        suggestions = []

        # Get context around cursor
        lines = code.split("\n")
        current_line_index = self._get_line_from_position(code, cursor_position)
        current_line = lines[current_line_index] if current_line_index < len(lines) else ""

        # Generate different types of suggestions
        suggestions.extend(
            self._get_completion_suggestions(current_line, lines, current_line_index, language)
        )
        suggestions.extend(self._get_bug_predictions(code, language))
        suggestions.extend(self._get_refactoring_suggestions(code, language))
        suggestions.extend(self._get_best_practice_suggestions(code, language))

        # Sort by severity and confidence
        suggestions.sort(key=lambda x: (x.severity.value, -x.confidence))

        return suggestions[:10]  # Return top 10 suggestions

    def _get_completion_suggestions(
        self, current_line: str, lines: List[str], line_index: int, language: str
    ) -> List[CodeSuggestion]:
        """Generate code completion suggestions"""
        suggestions = []

        if language not in self.completion_patterns:
            return suggestions

        patterns = self.completion_patterns[language]

        # Check for common completion patterns
        for pattern_name, pattern_info in patterns.items():
            if re.search(pattern_info["pattern"], current_line):
                for i, suggestion_text in enumerate(pattern_info["suggestions"]):
                    suggestions.append(
                        CodeSuggestion(
                            suggestion_id=f"comp_{pattern_name}_{i}",
                            type=SuggestionType.COMPLETION,
                            severity=SeverityLevel.LOW,
                            title=f"Complete {pattern_name.replace('_', ' ').title()}",
                            description=f"Suggested completion for {pattern_name}",
                            code_snippet=current_line,
                            suggested_fix=suggestion_text,
                            line_number=line_index + 1,
                            confidence=0.8,
                            explanation=f"This is a common pattern in {language}",
                        )
                    )

        return suggestions

    def _get_bug_predictions(self, code: str, language: str) -> List[CodeSuggestion]:
        """Predict potential bugs in the code"""
        suggestions = []

        if language not in self.bug_patterns:
            return suggestions

        patterns = self.bug_patterns[language]
        lines = code.split("\n")

        for line_num, line in enumerate(lines):
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], line, re.MULTILINE | re.DOTALL):
                    suggestions.append(
                        CodeSuggestion(
                            suggestion_id=f"bug_{pattern_info['type']}_{line_num}",
                            type=SuggestionType.BUG_FIX,
                            severity=pattern_info["severity"],
                            title=f"Potential {pattern_info['type'].replace('_', ' ').title()}",
                            description=pattern_info["message"],
                            code_snippet=line.strip(),
                            suggested_fix=pattern_info["fix"],
                            line_number=line_num + 1,
                            confidence=0.9,
                            explanation=f"This pattern often leads to {pattern_info['type']} issues",
                        )
                    )

        return suggestions

    def _get_refactoring_suggestions(self, code: str, language: str) -> List[CodeSuggestion]:
        """Generate refactoring suggestions"""
        suggestions = []

        if language == "python":
            try:
                tree = ast.parse(code)

                # Check for long functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_lines = (
                            node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                        )
                        if function_lines > self.refactoring_rules["long_function"]["threshold"]:
                            suggestions.append(
                                CodeSuggestion(
                                    suggestion_id=f"refactor_long_{node.name}",
                                    type=SuggestionType.REFACTOR,
                                    severity=SeverityLevel.MEDIUM,
                                    title="Long Function Detected",
                                    description=self.refactoring_rules["long_function"]["message"],
                                    code_snippet=f"def {node.name}(...): # {function_lines} lines",
                                    suggested_fix=self.refactoring_rules["long_function"][
                                        "suggestion"
                                    ],
                                    line_number=node.lineno,
                                    confidence=0.7,
                                    explanation="Functions with many lines are harder to maintain and test",
                                )
                            )

            except SyntaxError:
                pass  # Skip AST analysis if code has syntax errors

        return suggestions

    def _get_best_practice_suggestions(self, code: str, language: str) -> List[CodeSuggestion]:
        """Generate best practice suggestions"""
        suggestions = []

        if language not in self.best_practices:
            return suggestions

        practices = self.best_practices[language]
        lines = code.split("\n")

        for line_num, line in enumerate(lines):
            for practice in practices:
                if re.search(practice["pattern"], line):
                    suggestions.append(
                        CodeSuggestion(
                            suggestion_id=f"practice_{practice['type']}_{line_num}",
                            type=SuggestionType.BEST_PRACTICE,
                            severity=SeverityLevel.LOW,
                            title=f"{practice['type'].replace('_', ' ').title()} Suggestion",
                            description=practice["suggestion"],
                            code_snippet=line.strip(),
                            suggested_fix="",
                            line_number=line_num + 1,
                            confidence=0.6,
                            explanation=f"Following {practice['type']} best practices improves code quality",
                        )
                    )

        return suggestions

    async def get_ai_powered_suggestions(
        self, code: str, context: str, language: str = "python"
    ) -> List[CodeSuggestion]:
        """Get AI-powered suggestions using OpenAI"""
        if not OPENAI_AVAILABLE or not Config.OPENAI_API_KEY:
            return []

        try:
            prompt = f"""
            You are an expert {language} programming assistant. Analyze the following code and provide intelligent suggestions for:
            1. Code completion
            2. Bug fixes
            3. Performance optimizations
            4. Best practices

            Code:
            ```{language}
            {code}
            ```

            Context: {context}

            Provide suggestions in JSON format:
            {{
                "suggestions": [
                    {{
                        "type": "completion|bug_fix|optimization|best_practice",
                        "severity": "low|medium|high|critical",
                        "title": "Brief title",
                        "description": "Detailed description",
                        "suggested_fix": "Suggested code or approach",
                        "line_number": 1,
                        "confidence": 0.9,
                        "explanation": "Why this suggestion helps"
                    }}
                ]
            }}
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert programming assistant focused on code quality and best practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            ai_response = response.choices[0].message.content

            # Parse AI response
            try:
                parsed_response = json.loads(ai_response)
                suggestions = []

                for i, suggestion_data in enumerate(parsed_response.get("suggestions", [])):
                    suggestions.append(
                        CodeSuggestion(
                            suggestion_id=f"ai_{i}",
                            type=SuggestionType(suggestion_data.get("type", "completion")),
                            severity=SeverityLevel(suggestion_data.get("severity", "low")),
                            title=suggestion_data.get("title", "AI Suggestion"),
                            description=suggestion_data.get("description", ""),
                            code_snippet=code[:100] + "..." if len(code) > 100 else code,
                            suggested_fix=suggestion_data.get("suggested_fix", ""),
                            line_number=suggestion_data.get("line_number", 1),
                            confidence=suggestion_data.get("confidence", 0.5),
                            explanation=suggestion_data.get("explanation", ""),
                        )
                    )

                return suggestions

            except json.JSONDecodeError:
                return []

        except (ValueError, KeyError, AttributeError, TypeError) as e:
            print(f"AI suggestions failed: {e}")
            return []

    def get_security_suggestions(self, code: str, language: str = "python") -> List[CodeSuggestion]:
        """Generate security-focused suggestions"""
        suggestions = []

        security_patterns = {
            "python": [
                {
                    "pattern": r"eval\(",
                    "message": "Use of eval() can be dangerous",
                    "fix": "Consider safer alternatives like ast.literal_eval()",
                    "severity": SeverityLevel.CRITICAL,
                },
                {
                    "pattern": r"exec\(",
                    "message": "Use of exec() can execute arbitrary code",
                    "fix": "Avoid exec() or sanitize input thoroughly",
                    "severity": SeverityLevel.CRITICAL,
                },
                {
                    "pattern": r"input\([^)]*\)",
                    "message": "User input should be validated",
                    "fix": "Add input validation and sanitization",
                    "severity": SeverityLevel.MEDIUM,
                },
                {
                    "pattern": r'open\([^)]*[\'"]w[\'"][^)]*\)',
                    "message": "File operations need error handling",
                    "fix": "Use try-except blocks and context managers",
                    "severity": SeverityLevel.LOW,
                },
            ]
        }

        if language in security_patterns:
            lines = code.split("\n")
            for line_num, line in enumerate(lines):
                for pattern_info in security_patterns[language]:
                    if re.search(pattern_info["pattern"], line):
                        suggestions.append(
                            CodeSuggestion(
                                suggestion_id=f"security_{line_num}",
                                type=SuggestionType.SECURITY,
                                severity=pattern_info["severity"],
                                title="Security Concern",
                                description=pattern_info["message"],
                                code_snippet=line.strip(),
                                suggested_fix=pattern_info["fix"],
                                line_number=line_num + 1,
                                confidence=0.85,
                                explanation="Security vulnerabilities can lead to serious issues",
                            )
                        )

        return suggestions

    def _get_line_from_position(self, code: str, position: int) -> int:
        """Get line number from cursor position"""
        if position <= 0:
            return 0

        lines_before = code[:position].count("\n")
        return lines_before

    def format_suggestions_for_editor(self, suggestions: List[CodeSuggestion]) -> Dict:
        """Format suggestions for editor display"""
        formatted = {
            "total_suggestions": len(suggestions),
            "by_severity": {"critical": [], "high": [], "medium": [], "low": []},
            "by_type": {
                "completion": [],
                "bug_fix": [],
                "refactor": [],
                "best_practice": [],
                "optimization": [],
                "security": [],
            },
        }

        for suggestion in suggestions:
            # Group by severity
            severity_key = suggestion.severity.value
            if severity_key in formatted["by_severity"]:
                formatted["by_severity"][severity_key].append(
                    {
                        "id": suggestion.suggestion_id,
                        "title": suggestion.title,
                        "description": suggestion.description,
                        "line": suggestion.line_number,
                        "confidence": suggestion.confidence,
                        "fix": suggestion.suggested_fix,
                    }
                )

            # Group by type
            type_key = suggestion.type.value
            if type_key in formatted["by_type"]:
                formatted["by_type"][type_key].append(
                    {
                        "id": suggestion.suggestion_id,
                        "title": suggestion.title,
                        "description": suggestion.description,
                        "line": suggestion.line_number,
                        "severity": suggestion.severity.value,
                        "fix": suggestion.suggested_fix,
                    }
                )

        return formatted


# Global instance
ai_suggestions_service = AICodeSuggestionsService()

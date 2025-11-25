"""
Smart Assignment Generation Service
AI-powered adaptive problem generation based on student performance
"""

import random
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from services.code_analysis_service import code_analyzer

class DifficultyLevel(Enum):
    """Assignment difficulty levels"""
    BEGINNER = 1
    NOVICE = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

class ProblemCategory(Enum):
    """Problem categories for adaptive generation"""
    ARRAYS_STRINGS = "arrays_strings"
    LINKED_LISTS = "linked_lists"
    TREES_GRAPHS = "trees_graphs"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    SORTING_SEARCHING = "sorting_searching"
    RECURSION = "recursion"
    SYSTEM_DESIGN = "system_design"

@dataclass
class StudentProfile:
    """Student learning profile for adaptive generation"""
    student_id: str
    skill_levels: Dict[str, int]  # topic -> skill level (1-5)
    learning_pace: str  # "slow", "medium", "fast"
    preferred_difficulty: int
    weak_areas: List[str]
    strong_areas: List[str]
    recent_performance: List[Dict]

@dataclass
class GeneratedAssignment:
    """AI-generated assignment"""
    assignment_id: str
    title: str
    description: str
    category: ProblemCategory
    difficulty: DifficultyLevel
    learning_objectives: List[str]
    problem_statement: str
    starter_code: str
    test_cases: List[Dict]
    hints: List[str]
    solution_approach: str
    estimated_time: int  # minutes
    prerequisites: List[str]

class SmartAssignmentGenerator:
    def __init__(self):
        self.problem_templates = self._load_problem_templates()
        self.difficulty_algorithms = self._load_difficulty_algorithms()
        self.learning_paths = self._load_learning_paths()
        
    def _load_problem_templates(self) -> Dict:
        """Load base problem templates for different categories"""
        return {
            ProblemCategory.ARRAYS_STRINGS: {
                "two_sum": {
                    "base_problem": "Find two numbers in array that sum to target",
                    "variations": [
                        {"difficulty": 1, "constraint": "array sorted"},
                        {"difficulty": 2, "constraint": "return indices"},
                        {"difficulty": 3, "constraint": "multiple solutions"},
                        {"difficulty": 4, "constraint": "3-sum problem"},
                        {"difficulty": 5, "constraint": "k-sum general case"}
                    ],
                    "concepts": ["hash_maps", "two_pointers", "sorting"]
                },
                "string_manipulation": {
                    "base_problem": "Process and transform string data",
                    "variations": [
                        {"difficulty": 1, "constraint": "reverse string"},
                        {"difficulty": 2, "constraint": "check palindrome"},
                        {"difficulty": 3, "constraint": "anagram detection"},
                        {"difficulty": 4, "constraint": "longest substring"},
                        {"difficulty": 5, "constraint": "pattern matching"}
                    ],
                    "concepts": ["string_processing", "algorithms", "optimization"]
                }
            },
            ProblemCategory.LINKED_LISTS: {
                "list_operations": {
                    "base_problem": "Implement linked list operations",
                    "variations": [
                        {"difficulty": 1, "constraint": "basic insertion/deletion"},
                        {"difficulty": 2, "constraint": "reverse linked list"},
                        {"difficulty": 3, "constraint": "detect cycle"},
                        {"difficulty": 4, "constraint": "merge sorted lists"},
                        {"difficulty": 5, "constraint": "complex reordering"}
                    ],
                    "concepts": ["pointers", "data_structures", "algorithms"]
                }
            },
            ProblemCategory.DYNAMIC_PROGRAMMING: {
                "optimization": {
                    "base_problem": "Solve optimization problem using DP",
                    "variations": [
                        {"difficulty": 2, "constraint": "fibonacci sequence"},
                        {"difficulty": 3, "constraint": "coin change problem"},
                        {"difficulty": 4, "constraint": "knapsack problem"},
                        {"difficulty": 5, "constraint": "edit distance"}
                    ],
                    "concepts": ["memoization", "optimization", "recursion"]
                }
            }
        }
    
    def _load_difficulty_algorithms(self) -> Dict:
        """Load algorithms for difficulty adjustment"""
        return {
            "progression_rules": {
                "success_threshold": 0.8,  # 80% success rate to increase difficulty
                "struggle_threshold": 0.4,  # Below 40% to decrease difficulty
                "adaptation_rate": 0.2     # How much to adjust difficulty
            },
            "complexity_factors": {
                "input_size": {"small": 1, "medium": 1.2, "large": 1.5},
                "constraints": {"basic": 1, "moderate": 1.3, "complex": 1.6},
                "concepts": {"single": 1, "multiple": 1.4, "advanced": 1.8}
            }
        }
    
    def _load_learning_paths(self) -> Dict:
        """Load structured learning paths"""
        return {
            "fundamentals": [
                "basic_syntax", "variables", "conditionals", "loops", 
                "functions", "arrays", "strings"
            ],
            "data_structures": [
                "arrays", "linked_lists", "stacks", "queues", 
                "trees", "graphs", "hash_tables"
            ],
            "algorithms": [
                "searching", "sorting", "recursion", "dynamic_programming",
                "greedy", "graph_algorithms"
            ],
            "advanced": [
                "system_design", "optimization", "concurrent_programming",
                "advanced_algorithms"
            ]
        }
    
    def generate_adaptive_assignment(self, student_profile: StudentProfile,
                                   category: Optional[ProblemCategory] = None) -> GeneratedAssignment:
        """Generate assignment adapted to student's current level and needs"""
        
        # Determine focus area
        if category is None:
            category = self._select_optimal_category(student_profile)
        
        # Calculate appropriate difficulty
        target_difficulty = self._calculate_target_difficulty(student_profile, category)
        
        # Select problem template
        problem_template = self._select_problem_template(category, target_difficulty)
        
        # Generate specific assignment
        assignment = self._create_assignment_from_template(
            problem_template, target_difficulty, student_profile, category
        )
        
        return assignment
    
    def _select_optimal_category(self, profile: StudentProfile) -> ProblemCategory:
        """Select the best category for student improvement"""
        
        # Prioritize weak areas for improvement
        if profile.weak_areas:
            weak_area = random.choice(profile.weak_areas)
            category_mapping = {
                "arrays": ProblemCategory.ARRAYS_STRINGS,
                "strings": ProblemCategory.ARRAYS_STRINGS,
                "linked_lists": ProblemCategory.LINKED_LISTS,
                "trees": ProblemCategory.TREES_GRAPHS,
                "graphs": ProblemCategory.TREES_GRAPHS,
                "dynamic_programming": ProblemCategory.DYNAMIC_PROGRAMMING,
                "sorting": ProblemCategory.SORTING_SEARCHING,
                "recursion": ProblemCategory.RECURSION
            }
            
            for key, cat in category_mapping.items():
                if key in weak_area.lower():
                    return cat
        
        # Default selection based on learning path
        available_categories = list(ProblemCategory)
        return random.choice(available_categories)
    
    def _calculate_target_difficulty(self, profile: StudentProfile, 
                                   category: ProblemCategory) -> DifficultyLevel:
        """Calculate appropriate difficulty level"""
        
        # Get student's skill level in this category
        category_skill = profile.skill_levels.get(category.value, 2)
        
        # Analyze recent performance
        recent_success_rate = self._calculate_recent_success_rate(profile.recent_performance)
        
        # Adjust difficulty based on performance
        if recent_success_rate > 0.8:
            # Student is doing well, can handle slightly harder problems
            target_level = min(5, category_skill + 1)
        elif recent_success_rate < 0.4:
            # Student is struggling, provide easier problems
            target_level = max(1, category_skill - 1)
        else:
            # Maintain current level
            target_level = category_skill
        
        return DifficultyLevel(target_level)
    
    def _calculate_recent_success_rate(self, recent_performance: List[Dict]) -> float:
        """Calculate success rate from recent submissions"""
        if not recent_performance:
            return 0.6  # Default moderate performance
        
        # Take last 5 submissions
        recent = recent_performance[-5:]
        successes = sum(1 for perf in recent if perf.get('score', 0) >= 70)
        
        return successes / len(recent)
    
    def _select_problem_template(self, category: ProblemCategory, 
                               difficulty: DifficultyLevel) -> Dict:
        """Select appropriate problem template"""
        
        category_templates = self.problem_templates.get(category, {})
        
        if not category_templates:
            # Fallback to arrays/strings if category not found
            category_templates = self.problem_templates[ProblemCategory.ARRAYS_STRINGS]
        
        # Select template based on difficulty
        available_templates = list(category_templates.keys())
        selected_template_key = random.choice(available_templates)
        template = category_templates[selected_template_key]
        
        # Find appropriate variation for difficulty level
        suitable_variations = [
            var for var in template["variations"] 
            if var["difficulty"] == difficulty.value
        ]
        
        if not suitable_variations:
            # Use closest difficulty
            suitable_variations = template["variations"]
        
        selected_variation = random.choice(suitable_variations)
        
        return {
            "template_key": selected_template_key,
            "base_problem": template["base_problem"],
            "variation": selected_variation,
            "concepts": template["concepts"]
        }
    
    def _create_assignment_from_template(self, template: Dict, difficulty: DifficultyLevel,
                                       profile: StudentProfile, category: ProblemCategory) -> GeneratedAssignment:
        """Create full assignment from selected template"""
        
        assignment_id = f"gen_{int(datetime.utcnow().timestamp())}"
        
        # Generate problem-specific content
        problem_content = self._generate_problem_content(template, difficulty)
        
        # Create test cases
        test_cases = self._generate_test_cases(template, difficulty)
        
        # Generate hints based on student profile
        hints = self._generate_adaptive_hints(template, profile)
        
        return GeneratedAssignment(
            assignment_id=assignment_id,
            title=problem_content["title"],
            description=problem_content["description"],
            category=category,
            difficulty=difficulty,
            learning_objectives=problem_content["objectives"],
            problem_statement=problem_content["statement"],
            starter_code=problem_content["starter_code"],
            test_cases=test_cases,
            hints=hints,
            solution_approach=problem_content["approach"],
            estimated_time=self._estimate_completion_time(difficulty, profile),
            prerequisites=template["concepts"]
        )
    
    def _generate_problem_content(self, template: Dict, difficulty: DifficultyLevel) -> Dict:
        """Generate specific problem content"""
        
        base_problem = template["base_problem"]
        variation = template["variation"]
        template_key = template["template_key"]
        
        # Generate content based on template and difficulty
        if template_key == "two_sum":
            return self._generate_two_sum_content(variation, difficulty)
        elif template_key == "string_manipulation":
            return self._generate_string_content(variation, difficulty)
        elif template_key == "list_operations":
            return self._generate_list_content(variation, difficulty)
        else:
            # Generic problem generation
            return self._generate_generic_content(base_problem, variation, difficulty)
    
    def _generate_two_sum_content(self, variation: Dict, difficulty: DifficultyLevel) -> Dict:
        """Generate Two Sum problem variations"""
        
        if difficulty.value == 1:
            return {
                "title": "Two Sum - Sorted Array",
                "description": "Find two numbers in a sorted array that sum to a target value",
                "statement": """
Given a sorted array of integers and a target sum, find two numbers that add up to the target.
Return the indices of the two numbers.

Example:
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1] (because nums[0] + nums[1] = 2 + 7 = 9)
                """,
                "objectives": [
                    "Understand two-pointer technique",
                    "Work with sorted arrays",
                    "Implement efficient search"
                ],
                "starter_code": """def two_sum(nums, target):
    # Your code here
    pass

# Test your solution
nums = [2, 7, 11, 15]
target = 9
result = two_sum(nums, target)
print(result)""",
                "approach": "Use two pointers from start and end of array"
            }
        
        elif difficulty.value >= 3:
            return {
                "title": "Three Sum Problem",
                "description": "Find all unique triplets that sum to zero",
                "statement": """
Given an array of integers, find all unique triplets that sum to zero.

Example:
Input: nums = [-1, 0, 1, 2, -1, -4]
Output: [[-1, -1, 2], [-1, 0, 1]]
                """,
                "objectives": [
                    "Handle duplicate removal",
                    "Implement nested two-pointer technique",
                    "Optimize time complexity"
                ],
                "starter_code": """def three_sum(nums):
    # Your code here
    pass""",
                "approach": "Sort array, then use two-pointer for each element"
            }
        
        # Default two sum
        return {
            "title": "Two Sum",
            "description": "Find two numbers that sum to target",
            "statement": "Given an array and target, find two numbers that sum to target.",
            "objectives": ["Use hash maps", "Understand time/space tradeoffs"],
            "starter_code": "def two_sum(nums, target):\n    pass",
            "approach": "Use hash map for O(n) solution"
        }
    
    def _generate_string_content(self, variation: Dict, difficulty: DifficultyLevel) -> Dict:
        """Generate string manipulation problems"""
        constraint = variation["constraint"]
        
        if "reverse" in constraint:
            return {
                "title": "Reverse String",
                "description": "Reverse a string in-place",
                "statement": "Write a function to reverse a string in-place using O(1) extra space.",
                "objectives": ["Two-pointer technique", "In-place modification"],
                "starter_code": "def reverse_string(s):\n    pass",
                "approach": "Use two pointers from both ends"
            }
        elif "palindrome" in constraint:
            return {
                "title": "Valid Palindrome",
                "description": "Check if string is a palindrome",
                "statement": "Determine if a string is a valid palindrome, ignoring spaces and case.",
                "objectives": ["String processing", "Two-pointer technique"],
                "starter_code": "def is_palindrome(s):\n    pass",
                "approach": "Clean string then check with two pointers"
            }
        
        return {
            "title": "String Problem",
            "description": "String manipulation challenge",
            "statement": f"Solve string problem with constraint: {constraint}",
            "objectives": ["String processing"],
            "starter_code": "def solve_string(s):\n    pass",
            "approach": "Analyze string character by character"
        }
    
    def _generate_list_content(self, variation: Dict, difficulty: DifficultyLevel) -> Dict:
        """Generate linked list problems"""
        constraint = variation["constraint"]
        
        return {
            "title": f"Linked List - {constraint.title()}",
            "description": f"Implement linked list {constraint}",
            "statement": f"Create a solution for linked list {constraint} operation.",
            "objectives": ["Pointer manipulation", "Linked list traversal"],
            "starter_code": """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solve_linked_list(head):
    pass""",
            "approach": "Use pointer manipulation techniques"
        }
    
    def _generate_generic_content(self, base_problem: str, variation: Dict, 
                                difficulty: DifficultyLevel) -> Dict:
        """Generate generic problem content"""
        return {
            "title": f"{base_problem.title()} - Level {difficulty.value}",
            "description": f"{base_problem} with {variation['constraint']}",
            "statement": f"Solve: {base_problem}\nConstraint: {variation['constraint']}",
            "objectives": ["Problem solving", "Algorithm implementation"],
            "starter_code": "def solve_problem():\n    pass",
            "approach": "Break down the problem step by step"
        }
    
    def _generate_test_cases(self, template: Dict, difficulty: DifficultyLevel) -> List[Dict]:
        """Generate appropriate test cases"""
        
        # Base test cases
        test_cases = [
            {"input": "basic case", "expected": "expected output"},
            {"input": "edge case", "expected": "edge output"}
        ]
        
        # Add more complex cases for higher difficulty
        if difficulty.value >= 3:
            test_cases.extend([
                {"input": "complex case", "expected": "complex output"},
                {"input": "large input", "expected": "large output"}
            ])
        
        if difficulty.value >= 4:
            test_cases.append(
                {"input": "stress test", "expected": "stress output"}
            )
        
        return test_cases
    
    def _generate_adaptive_hints(self, template: Dict, profile: StudentProfile) -> List[str]:
        """Generate hints based on student profile"""
        
        hints = ["Think about the problem step by step"]
        
        # Add concept-specific hints
        concepts = template["concepts"]
        
        if "hash_maps" in concepts and "hash_maps" in profile.weak_areas:
            hints.append("Consider using a hash map to store seen values")
        
        if "two_pointers" in concepts:
            hints.append("Try using two pointers from different positions")
        
        if "recursion" in concepts and profile.learning_pace == "slow":
            hints.append("Start with the base case, then think about the recursive step")
        
        # Add difficulty-appropriate hints
        if any(skill < 3 for skill in profile.skill_levels.values()):
            hints.append("Break the problem into smaller sub-problems")
            hints.append("Test your solution with simple examples first")
        
        return hints
    
    def _estimate_completion_time(self, difficulty: DifficultyLevel, 
                                profile: StudentProfile) -> int:
        """Estimate time needed based on difficulty and student profile"""
        
        base_times = {
            DifficultyLevel.BEGINNER: 20,
            DifficultyLevel.NOVICE: 35,
            DifficultyLevel.INTERMEDIATE: 50,
            DifficultyLevel.ADVANCED: 75,
            DifficultyLevel.EXPERT: 120
        }
        
        base_time = base_times[difficulty]
        
        # Adjust based on learning pace
        pace_multipliers = {"slow": 1.5, "medium": 1.0, "fast": 0.7}
        multiplier = pace_multipliers.get(profile.learning_pace, 1.0)
        
        return int(base_time * multiplier)
    
    def analyze_assignment_effectiveness(self, assignment_id: str, 
                                       student_results: List[Dict]) -> Dict:
        """Analyze how effective the generated assignment was"""
        
        if not student_results:
            return {"effectiveness": "unknown", "needs_adjustment": True}
        
        avg_score = sum(result.get("score", 0) for result in student_results) / len(student_results)
        avg_time = sum(result.get("time_spent", 0) for result in student_results) / len(student_results)
        
        effectiveness = "high" if avg_score >= 80 else "medium" if avg_score >= 60 else "low"
        
        recommendations = []
        
        if avg_score < 50:
            recommendations.append("Reduce difficulty level")
        elif avg_score > 90:
            recommendations.append("Increase difficulty level")
        
        if avg_time > 120:  # Over 2 hours
            recommendations.append("Simplify problem or provide more hints")
        
        return {
            "effectiveness": effectiveness,
            "avg_score": avg_score,
            "avg_time": avg_time,
            "recommendations": recommendations,
            "needs_adjustment": bool(recommendations)
        }

# Global instance
smart_assignment_generator = SmartAssignmentGenerator()
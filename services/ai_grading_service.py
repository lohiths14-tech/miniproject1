from services.code_analysis_service import code_analyzer
from services.gamification_service import gamification_service
from typing import List, Dict, Tuple, Any
import logging
import subprocess
import tempfile
import os
import time
import json

try:
    import openai
    from config import Config
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    Config = None

logger = logging.getLogger(__name__)

def grade_submission(code, test_cases, programming_language, user_id=None):
    """
    Grade a code submission comprehensively.

    Args:
        code (str): The submitted code to grade
        test_cases (list): List of test cases with input and expected output
        programming_language (str): Programming language (python, java, cpp, etc.)
        user_id (str): User ID for gamification integration

    Returns:
        dict: Comprehensive grading result with score, feedback, analysis, and achievements
    """
    try:
        result = {
            'score': 0,
            'max_score': 100,
            'feedback': '',
            'test_results': [],
            'execution_time': 0,
            'memory_usage': 0
        }

        # First, run test cases to check correctness
        test_results = run_test_cases(code, test_cases, programming_language)
        result['test_results'] = test_results

        # Perform advanced code analysis
        analysis_result = code_analyzer.analyze_code(code, programming_language)
        result['code_analysis'] = {
            'complexity_level': analysis_result.complexity_level.value,
            'big_o_analysis': analysis_result.big_o_analysis,
            'performance_metrics': {
                'execution_time': analysis_result.performance_metrics.execution_time,
                'memory_usage': analysis_result.performance_metrics.memory_usage,
                'operations_count': analysis_result.performance_metrics.operations_count
            },
            'code_metrics': {
                'lines_of_code': analysis_result.code_metrics.lines_of_code,
                'cyclomatic_complexity': analysis_result.code_metrics.cyclomatic_complexity,
                'nesting_depth': analysis_result.code_metrics.nesting_depth,
                'function_count': analysis_result.code_metrics.function_count
            },
            'optimization_suggestions': analysis_result.optimization_suggestions,
            'code_smells': analysis_result.code_smells,
            'best_practices_score': analysis_result.best_practices_score,
            'maintainability_score': analysis_result.maintainability_score
        }

        # Calculate enhanced score based on multiple factors
        passed_tests = sum(1 for test in test_results if test['passed'])
        total_tests = len(test_results)

        if total_tests > 0:
            correctness_score = (passed_tests / total_tests) * 50  # 50% for correctness
        else:
            correctness_score = 0

        # Code quality score (30%)
        quality_score = (analysis_result.best_practices_score / 100) * 30

        # Performance and efficiency score (20%)
        efficiency_score = 20
        if analysis_result.big_o_analysis['time_complexity'] in ['O(n²)', 'O(n³)', 'O(2^n)', 'O(n!)']:
            efficiency_score = 10  # Poor efficiency
        elif analysis_result.big_o_analysis['time_complexity'] in ['O(n log n)']:
            efficiency_score = 15  # Good efficiency
        elif analysis_result.big_o_analysis['time_complexity'] in ['O(1)', 'O(log n)']:
            efficiency_score = 20  # Excellent efficiency

        # Combine all scores
        total_score = correctness_score + quality_score + efficiency_score
        result['score'] = min(100, int(total_score))

        # Enhanced scoring breakdown
        result['score_breakdown'] = {
            'correctness': int(correctness_score),
            'code_quality': int(quality_score),
            'efficiency': int(efficiency_score),
            'total': int(total_score)
        }

        # Use AI to evaluate code quality, efficiency, and style
        ai_feedback = get_ai_feedback(code, test_cases, programming_language, analysis_result)

        # Combine AI feedback with analysis results
        comprehensive_feedback = generate_comprehensive_feedback(ai_feedback, analysis_result, test_results)
        result['feedback'] = comprehensive_feedback

        # Award gamification points if user_id provided
        if user_id:
            gamification_result = gamification_service.award_points_and_badges(
                user_id,
                'submission',
                {
                    'score': result['score'],
                    'time_taken': analysis_result.performance_metrics.execution_time,
                    'complexity_level': analysis_result.complexity_level.value,
                    'perfect_score': result['score'] == 100,
                    'language': programming_language
                }
            )
            result['gamification'] = gamification_result

        # Calculate average execution time
        execution_times = [test.get('execution_time', 0) for test in test_results]
        result['execution_time'] = sum(execution_times) / len(execution_times) if execution_times else 0

        return result

    except Exception as e:
        return {
            'score': 0,
            'max_score': 100,
            'feedback': f'Grading failed: {str(e)}',
            'test_results': [],
            'execution_time': 0,
            'memory_usage': 0,
            'code_analysis': None,
            'score_breakdown': {'correctness': 0, 'code_quality': 0, 'efficiency': 0, 'total': 0},
            'gamification': None
        }

def run_test_cases(
    code: str,
    test_cases: List[Dict[str, str]],
    programming_language: str
) -> List[Dict[str, Any]]:
    """
    Run test cases against the submitted code
    """
    test_results = []

    for i, test_case in enumerate(test_cases):
        try:
            test_input = test_case.get('input', '')
            expected_output = test_case.get('expected_output', '').strip()

            # Execute the code with test input
            start_time = time.time()
            actual_output, error, success = execute_code(code, test_input, programming_language)
            execution_time = time.time() - start_time

            if not success:
                test_results.append({
                    'test_case': i + 1,
                    'input': test_input,
                    'expected_output': expected_output,
                    'actual_output': error,
                    'passed': False,
                    'execution_time': execution_time,
                    'error': error
                })
                continue

            # Compare outputs
            actual_output_clean = actual_output.strip()
            passed = actual_output_clean == expected_output

            test_results.append({
                'test_case': i + 1,
                'input': test_input,
                'expected_output': expected_output,
                'actual_output': actual_output_clean,
                'passed': passed,
                'execution_time': execution_time,
                'error': None
            })

        except Exception as e:
            test_results.append({
                'test_case': i + 1,
                'input': test_case.get('input', ''),
                'expected_output': test_case.get('expected_output', ''),
                'actual_output': str(e),
                'passed': False,
                'execution_time': 0,
                'error': str(e)
            })

    return test_results

def execute_code(
    code: str,
    test_input: str,
    programming_language: str
) -> Tuple[str, str, bool]:
    """
    Execute code with given input and return output
    """
    try:
        if programming_language.lower() == 'python':
            return execute_python_code(code, test_input)
        elif programming_language.lower() == 'java':
            return execute_java_code(code, test_input)
        elif programming_language.lower() in ['cpp', 'c++']:
            return execute_cpp_code(code, test_input)
        else:
            return '', f'Unsupported language: {programming_language}', False

    except Exception as e:
        return '', str(e), False

def execute_python_code(code, test_input):
    """
    Execute Python code safely
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            # Run the code with timeout
            process = subprocess.Popen(
                ['python', f.name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10  # 10 second timeout
            )

            try:
                output, error = process.communicate(input=test_input, timeout=10)

                if process.returncode == 0:
                    return output, '', True
                else:
                    return '', error, False

            except subprocess.TimeoutExpired:
                process.kill()
                return '', 'Execution timeout (10 seconds)', False

    except Exception as e:
        return '', str(e), False
    finally:
        try:
            os.unlink(f.name)
        except:
            pass

def execute_java_code(code, test_input):
    """
    Execute Java code safely
    """
    try:
        # Extract class name from code
        class_name = 'Main'
        if 'public class' in code:
            import re
            match = re.search(r'public class\s+(\w+)', code)
            if match:
                class_name = match.group(1)

        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, f'{class_name}.java')

            with open(java_file, 'w') as f:
                f.write(code)

            # Compile
            compile_process = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                timeout=15
            )

            if compile_process.returncode != 0:
                return '', compile_process.stderr, False

            # Run
            run_process = subprocess.Popen(
                ['java', '-cp', temp_dir, class_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )

            try:
                output, error = run_process.communicate(input=test_input, timeout=10)

                if run_process.returncode == 0:
                    return output, '', True
                else:
                    return '', error, False

            except subprocess.TimeoutExpired:
                run_process.kill()
                return '', 'Execution timeout (10 seconds)', False

    except Exception as e:
        return '', str(e), False

def execute_cpp_code(code, test_input):
    """
    Execute C++ code safely
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cpp_file = os.path.join(temp_dir, 'main.cpp')
            exe_file = os.path.join(temp_dir, 'main.exe' if os.name == 'nt' else 'main')

            with open(cpp_file, 'w') as f:
                f.write(code)

            # Compile
            compile_cmd = ['g++', cpp_file, '-o', exe_file]
            compile_process = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=15
            )

            if compile_process.returncode != 0:
                return '', compile_process.stderr, False

            # Run
            run_process = subprocess.Popen(
                [exe_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                output, error = run_process.communicate(input=test_input, timeout=10)

                if run_process.returncode == 0:
                    return output, '', True
                else:
                    return '', error, False

            except subprocess.TimeoutExpired:
                run_process.kill()
                return '', 'Execution timeout (10 seconds)', False

    except Exception as e:
        return '', str(e), False

def generate_comprehensive_feedback(ai_feedback, analysis_result, test_results):
    """
    Generate comprehensive feedback combining AI analysis and code metrics
    """
    feedback_sections = []

    # Test results summary
    passed_tests = sum(1 for test in test_results if test['passed'])
    total_tests = len(test_results)

    if total_tests > 0:
        feedback_sections.append(f"✅ Test Results: {passed_tests}/{total_tests} tests passed")

        if passed_tests < total_tests:
            failed_tests = [f"Test {test['test_case']}" for test in test_results if not test['passed']]
            feedback_sections.append(f"❌ Failed tests: {', '.join(failed_tests)}")

    # Code quality analysis
    feedback_sections.append(f"\n🔍 Code Quality Analysis:")
    feedback_sections.append(f"• Best Practices Score: {analysis_result.best_practices_score}/100")
    feedback_sections.append(f"• Maintainability Score: {analysis_result.maintainability_score}/100")
    feedback_sections.append(f"• Complexity Level: {analysis_result.complexity_level.value.title()}")

    # Algorithm efficiency
    feedback_sections.append(f"\n⚡ Algorithm Efficiency:")
    feedback_sections.append(f"• Time Complexity: {analysis_result.big_o_analysis['time_complexity']}")
    feedback_sections.append(f"• Space Complexity: {analysis_result.big_o_analysis['space_complexity']}")

    if analysis_result.big_o_analysis['detected_patterns']:
        patterns = [p['description'] for p in analysis_result.big_o_analysis['detected_patterns']]
        feedback_sections.append(f"• Detected Patterns: {', '.join(patterns)}")

    # Code metrics
    feedback_sections.append(f"\n📊 Code Metrics:")
    feedback_sections.append(f"• Lines of Code: {analysis_result.code_metrics.lines_of_code}")
    feedback_sections.append(f"• Cyclomatic Complexity: {analysis_result.code_metrics.cyclomatic_complexity}")
    feedback_sections.append(f"• Nesting Depth: {analysis_result.code_metrics.nesting_depth}")
    feedback_sections.append(f"• Functions: {analysis_result.code_metrics.function_count}")

    # Optimization suggestions
    if analysis_result.optimization_suggestions:
        feedback_sections.append(f"\n💡 Optimization Suggestions:")
        for suggestion in analysis_result.optimization_suggestions[:3]:  # Limit to top 3
            feedback_sections.append(f"• {suggestion}")

    # Code smells
    if analysis_result.code_smells:
        high_priority_smells = [smell for smell in analysis_result.code_smells if smell['severity'] in ['high', 'medium']]
        if high_priority_smells:
            feedback_sections.append(f"\n⚠️ Code Issues to Address:")
            for smell in high_priority_smells[:3]:  # Limit to top 3
                feedback_sections.append(f"• Line {smell.get('line', '?')}: {smell['description']}")

    # AI feedback if available
    if ai_feedback and ai_feedback.get('feedback'):
        feedback_sections.append(f"\n🤖 AI Analysis:")
        feedback_sections.append(ai_feedback['feedback'])

        if ai_feedback.get('strengths'):
            feedback_sections.append(f"\n✨ Strengths: {', '.join(ai_feedback['strengths'])}")

        if ai_feedback.get('improvements'):
            feedback_sections.append(f"\n🎯 Areas for Improvement: {', '.join(ai_feedback['improvements'])}")

    return '\n'.join(feedback_sections)

def get_ai_feedback(code, test_cases, programming_language, analysis_result=None):
    """
    Get AI feedback on code quality, efficiency, and style
    """
    try:
        # Enhanced prompt with analysis results
        analysis_context = ""
        if analysis_result:
            analysis_context = f"""

Advanced Analysis Results:
- Complexity Level: {analysis_result.complexity_level.value}
- Time Complexity: {analysis_result.big_o_analysis['time_complexity']}
- Best Practices Score: {analysis_result.best_practices_score}/100
- Maintainability Score: {analysis_result.maintainability_score}/100
- Code Smells Found: {len(analysis_result.code_smells)}
        """

        prompt = f"""
        You are an expert programming instructor evaluating student code submissions.

        Programming Language: {programming_language}

        Code to evaluate:
        ```{programming_language}
        {code}
        ```

        Test Cases:
        {json.dumps(test_cases, indent=2)}
        {analysis_context}

        Please provide advanced feedback focusing on:
        1. Code architecture and design patterns
        2. Error handling and edge cases
        3. Code readability and documentation
        4. Language-specific best practices
        5. Performance optimizations
        6. Maintainability and scalability

        Provide a quality score from 0-30 points and detailed constructive feedback.

        Respond in JSON format:
        {{
            "quality_score": <score_0_to_30>,
            "feedback": "<detailed_constructive_feedback>",
            "strengths": ["<strength1>", "<strength2>"],
            "improvements": ["<specific_improvement1>", "<specific_improvement2>"],
            "advanced_suggestions": ["<advanced_technique1>", "<advanced_technique2>"]
        }}
        """

        # Make API call to OpenAI
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != 'your_openai_api_key_here':
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert programming instructor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            ai_response = response.choices[0].message.content

            # Try to parse JSON response
            try:
                feedback_data = json.loads(ai_response)
                return feedback_data
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "quality_score": 20,
                    "feedback": ai_response,
                    "strengths": [],
                    "improvements": []
                }
        else:
            # Fallback when no OpenAI API key is configured
            return get_enhanced_rule_based_feedback(code, programming_language, analysis_result)

    except Exception as e:
        print(f"AI feedback failed: {str(e)}")
        return get_rule_based_feedback(code, programming_language)

def get_enhanced_rule_based_feedback(code, programming_language, analysis_result=None):
    """
    Provide enhanced rule-based feedback when AI is not available
    """
    quality_score = 20
    feedback_points = []
    strengths = []
    improvements = []

    # Integrate analysis results if available
    if analysis_result:
        if analysis_result.best_practices_score >= 80:
            quality_score += 5
            strengths.append("Excellent adherence to best practices")
        elif analysis_result.best_practices_score <= 60:
            quality_score -= 5
            improvements.append("Focus on following coding best practices")

        if analysis_result.complexity_level.value == 'simple':
            strengths.append("Clean and simple code structure")
        elif analysis_result.complexity_level.value in ['complex', 'very_complex']:
            improvements.append("Consider simplifying complex logic")
            quality_score -= 3

    # Basic code quality checks
    if len(code.strip()) < 10:
        quality_score -= 10
        improvements.append("Code appears incomplete or too short")

    if programming_language.lower() == 'python':
        # Python-specific enhanced checks
        if 'def ' in code:
            quality_score += 3
            strengths.append("Good use of functions for code organization")

        if any(keyword in code for keyword in ['try:', 'except:', 'finally:']):
            quality_score += 3
            strengths.append("Proper error handling implemented")

        if '"""' in code or "'''" in code:
            quality_score += 2
            strengths.append("Good documentation with docstrings")

        if 'import' in code:
            quality_score += 1
            strengths.append("Appropriate use of libraries")

        # Check for anti-patterns
        if 'global ' in code:
            quality_score -= 2
            improvements.append("Avoid global variables when possible")

        if code.count('for') > 2 and 'for' in code:
            improvements.append("Consider optimizing nested loops")

    # General programming practices
    if '#' in code or '//' in code or '/*' in code:
        quality_score += 2
        strengths.append("Well-commented code")

    # Check indentation consistency
    lines = code.split('\n')
    consistent_indentation = True
    for line in lines:
        if line.strip() and (line.startswith('\t') and '    ' in line[:10]):
            consistent_indentation = False
            break

    if consistent_indentation:
        strengths.append("Consistent code formatting")
    else:
        improvements.append("Use consistent indentation (tabs OR spaces)")
        quality_score -= 1

    # Generate comprehensive feedback
    feedback = "Enhanced automated code evaluation completed. "

    if strengths:
        feedback += f"\n\nStrengths identified: {'; '.join(strengths)}"

    if improvements:
        feedback += f"\n\nAreas for improvement: {'; '.join(improvements)}"

    if analysis_result and analysis_result.optimization_suggestions:
        feedback += f"\n\nOptimization suggestions: {'; '.join(analysis_result.optimization_suggestions[:2])}"

    return {
        "quality_score": min(30, max(0, quality_score)),
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements,
        "advanced_suggestions": []
    }

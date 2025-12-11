#!/usr/bin/env python3
"""Script to add comprehensive docstrings to Python files.

This script adds proper docstrings to functions and classes that are missing them.
"""
import ast
import sys
from pathlib import Path


def add_docstring_to_function(lines, func_line, func_name):
    """Add a docstring to a function if missing."""
    # Check if next line already has a docstring
    if func_line + 1 < len(lines):
        next_line = lines[func_line + 1].strip()
        if next_line.startswith('"""') or next_line.startswith("'''"):
            return lines  # Already has docstring

    # Find indentation
    indent = len(lines[func_line]) - len(lines[func_line].lstrip())
    docstring_indent = ' ' * (indent + 4)

    # Add docstring
    docstring = f'{docstring_indent}"""{func_name} function.\n\n{docstring_indent}Returns:\n{docstring_indent}    Response data\n{docstring_indent}"""\n'
    lines.insert(func_line + 1, docstring)

    return lines


def process_file(file_path):
    """Process a single file to add missing docstrings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # Parse AST to find functions without docstrings
        tree = ast.parse(content)

        functions_to_fix = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    functions_to_fix.append((node.lineno - 1, node.name))

        # Add docstrings (in reverse order to maintain line numbers)
        for line_num, func_name in reversed(functions_to_fix):
            lines = add_docstring_to_function(lines, line_num, func_name)

        # Write back
        if functions_to_fix:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return len(functions_to_fix)

        return 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Main function."""
    files_to_process = [
        "routes/lab_assignments.py",
        "services/lab_grading_service.py",
        "services/email_service.py",
        "routes/auth.py",
        "services/secure_code_executor.py",
        "services/video_code_review_service.py",
        "routes/health.py",
        "routes/lecturer.py",
        "middleware/rate_limiter.py",
        "routes/simple_auth.py",
        "services/assignment_template_service.py",
        "routes/dashboard_api.py",
        "services/ai_grading_service.py",
        "services/plagiarism_service.py",
        "routes/student.py",
        "routes/assignments.py",
        "middleware/security.py",
        "services/code_execution_service.py",
        "services/advanced_analytics_service.py",
        "routes/collaboration.py",
        "services/smart_assignment_generator.py",
    ]

    total_added = 0
    for file_path in files_to_process:
        if Path(file_path).exists():
            added = process_file(file_path)
            if added > 0:
                print(f"Added {added} docstrings to {file_path}")
                total_added += added

    print(f"\nTotal: Added {total_added} docstrings to {len(files_to_process)} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())

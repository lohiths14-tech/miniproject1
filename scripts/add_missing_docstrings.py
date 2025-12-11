#!/usr/bin/env python3
"""Script to add missing docstrings to Python files.

This script analyzes Python files and adds basic docstrings where missing.
"""
import ast
import sys
from pathlib import Path


def has_docstring(node):
    """Check if a node has a docstring."""
    return (
        isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    )


def analyze_file(file_path):
    """Analyze a Python file for missing docstrings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        issues = []

        # Check module docstring
        if not has_docstring(tree):
            issues.append(f"Module missing docstring")

        # Check classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not has_docstring(node):
                    issues.append(f"Class '{node.name}' missing docstring at line {node.lineno}")
            elif isinstance(node, ast.FunctionDef):
                # Skip private methods
                if not node.name.startswith('_') and not has_docstring(node):
                    issues.append(f"Function '{node.name}' missing docstring at line {node.lineno}")

        return issues
    except Exception as e:
        return [f"Error analyzing file: {e}"]


def main():
    """Main function to analyze all Python files."""
    project_root = Path(__file__).parent.parent

    dirs_to_check = ['services', 'routes', 'utils', 'middleware']

    print("Analyzing files for missing docstrings...")
    print("=" * 80)

    total_issues = 0
    files_with_issues = 0

    for dir_name in dirs_to_check:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue

            issues = analyze_file(py_file)

            if issues:
                files_with_issues += 1
                total_issues += len(issues)
                print(f"\n{py_file.relative_to(project_root)}:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"  - {issue}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")

    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Files with missing docstrings: {files_with_issues}")
    print(f"  Total missing docstrings: {total_issues}")
    print("\nRecommendation: Add docstrings to improve code quality scores")

    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

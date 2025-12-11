#!/usr/bin/env python3
"""Script to improve code quality across the project.

This script:
1. Runs pylint on all Python files
2. Identifies files with low scores
3. Generates a report of improvements needed
"""
import subprocess
import sys
from pathlib import Path


def run_pylint_on_file(file_path):
    """Run pylint on a single file and return the score."""
    try:
        result = subprocess.run(
            ['pylint', str(file_path), '--score=yes'],
            capture_output=True,
            text=True,
            check=False
        )

        # Extract score from output
        for line in result.stdout.split('\n'):
            if 'rated at' in line:
                score = float(line.split('rated at')[1].split('/')[0].strip())
                return score, result.stdout
        return 0.0, result.stdout
    except Exception as e:
        print(f"Error running pylint on {file_path}: {e}")
        return 0.0, str(e)


def main():
    """Main function to analyze code quality."""
    project_root = Path(__file__).parent.parent

    # Directories to analyze
    dirs_to_check = ['services', 'routes', 'models', 'utils', 'middleware']

    results = []

    print("Analyzing code quality...")
    print("=" * 80)

    for dir_name in dirs_to_check:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            continue

        print(f"\nAnalyzing {dir_name}/...")

        for py_file in dir_path.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue

            score, output = run_pylint_on_file(py_file)
            results.append({
                'file': str(py_file.relative_to(project_root)),
                'score': score
            })

            print(f"  {py_file.name}: {score:.2f}/10")

    # Sort by score
    results.sort(key=lambda x: x['score'])

    print("\n" + "=" * 80)
    print("SUMMARY - Files needing improvement (score < 9.0):")
    print("=" * 80)

    needs_improvement = [r for r in results if r['score'] < 9.0]

    if needs_improvement:
        for result in needs_improvement:
            print(f"{result['file']}: {result['score']:.2f}/10")
    else:
        print("All files have excellent code quality! 🎉")

    # Calculate average
    if results:
        avg_score = sum(r['score'] for r in results) / len(results)
        print(f"\nAverage pylint score: {avg_score:.2f}/10")

        if avg_score >= 9.0:
            print("✅ Project meets 9.0+ code quality target!")
            return 0
        else:
            print(f"❌ Project needs improvement to reach 9.0+ target")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())

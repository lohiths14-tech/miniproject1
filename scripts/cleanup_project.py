"""
Comprehensive Project Cleanup Script
Removes unwanted files while preserving essential project files
"""

import os
import shutil
from pathlib import Path
from typing import List, Set


class ProjectCleanup:
    """Cleans up unwanted files from the project"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.removed_files = []
        self.removed_dirs = []
        self.preserved_files = []
        self.total_space_saved = 0

    def cleanup(self):
        """Run comprehensive cleanup"""
        print("=" * 80)
        print("AI GRADING SYSTEM - PROJECT CLEANUP")
        print("=" * 80)
        print(f"Project Root: {self.project_root}")
        print("=" * 80)
        print()

        # 1. Remove temporary output files
        print("1. REMOVING TEMPORARY OUTPUT FILES...")
        self.remove_temp_outputs()
        print()

        # 2. Remove debug files
        print("2. REMOVING DEBUG FILES...")
        self.remove_debug_files()
        print()

        # 3. Remove duplicate/old documentation
        print("3. REMOVING DUPLICATE DOCUMENTATION...")
        self.remove_duplicate_docs()
        print()

        # 4. Remove cache directories
        print("4. CLEANING CACHE DIRECTORIES...")
        self.clean_cache_dirs()
        print()

        # 5. Remove redundant reports
        print("5. REMOVING OLD REPORTS...")
        self.remove_old_reports()
        print()

        # 6. Remove test artifacts
        print("6. REMOVING TEST ARTIFACTS...")
        self.remove_test_artifacts()
        print()

        # Generate report
        self.generate_report()

    def remove_temp_outputs(self):
        """Remove temporary output files"""
        temp_patterns = [
            "debug_*.txt",
            "test_output*.txt",
            "test_results*.txt",
            "final_*_output*.txt",
            "full_test_output.txt",
            "header_debug.txt",
            "api_results.txt",
            "final_api_results.txt",
            "wcag_*.txt",
            "accessibility_violations.txt",
        ]

        for pattern in temp_patterns:
            for file_path in self.project_root.glob(pattern):
                self._remove_file(file_path, "temp output")

    def remove_debug_files(self):
        """Remove debug files"""
        debug_patterns = [
            "*_debug.txt",
            "debug_*.txt",
            "*.log",
            "*.tmp",
        ]

        for pattern in debug_patterns:
            for file_path in self.project_root.glob(pattern):
                # Don't remove essential log configs
                if file_path.name not in ["logging.conf", "uwsgi.log"]:
                    self._remove_file(file_path, "debug file")

    def remove_duplicate_docs(self):
        """Remove duplicate or outdated documentation"""
        # Keep only the latest/most comprehensive versions

        # Old rating files - keep only the final ones
        old_ratings = [
            "PROJECT_RATING_FINAL_9.5.md",
            "ROADMAP_TO_10.0.md",
            "PHASE_COMPLETION_SUMMARY.md",
        ]

        for old_doc in old_ratings:
            file_path = self.project_root / old_doc
            if file_path.exists():
                self._remove_file(file_path, "old rating doc")

        # Old deployment docs (keep latest)
        if (self.project_root / "DEPLOYMENT_MASTER.md").exists():
            if (self.project_root / "DEPLOYMENT.md").exists():
                self._remove_file(
                    self.project_root / "DEPLOYMENT_MASTER.md", "duplicate deployment"
                )

        # Check for duplicate achievement files
        achievement_files = list(self.project_root.glob("ACHIEVEMENT*.md"))
        if len(achievement_files) > 1:
            # Keep only the latest
            achievement_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_file in achievement_files[1:]:
                self._remove_file(old_file, "old achievement")

    def clean_cache_dirs(self):
        """Clean cache directories"""
        cache_dirs = [
            "__pycache__",
            ".pytest_cache",
            ".hypothesis",
            ".mypy_cache",
            "htmlcov",
            ".coverage",
            ".benchmarks",
            ".kiro",
        ]

        for cache_dir in cache_dirs:
            for dir_path in self.project_root.rglob(cache_dir):
                if dir_path.is_dir():
                    self._remove_directory(dir_path, "cache")

        # Remove .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            self._remove_file(pyc_file, "compiled python")

    def remove_old_reports(self):
        """Remove old/redundant report files"""
        # Keep only essential reports
        essential_reports = {
            "VALIDATION_REPORT.json",
            "ERROR_FIX_REPORT.json",
            "TEST_EXECUTION_REPORT.json",
            "COMPONENT_VERIFICATION_REPORT.json",
            "PERFORMANCE_BENCHMARK_REPORT.json",
            "PRODUCTION_DEPLOYMENT_REPORT.json",
        }

        # Check for old versions
        old_patterns = [
            "final_verification_*.txt",
            "pytest_output.md",
            "submissions_data.json",  # If it's just test data
        ]

        for pattern in old_patterns:
            for file_path in self.project_root.glob(pattern):
                self._remove_file(file_path, "old report")

    def remove_test_artifacts(self):
        """Remove test artifacts"""
        test_artifacts = [
            ".coverage",
            "coverage.xml",
            ".tox",
            "*.egg-info",
        ]

        for pattern in test_artifacts:
            for path in self.project_root.glob(pattern):
                if path.is_dir():
                    self._remove_directory(path, "test artifact")
                else:
                    self._remove_file(path, "test artifact")

    def _remove_file(self, file_path: Path, file_type: str):
        """Remove a single file"""
        try:
            size = file_path.stat().st_size
            file_path.unlink()
            self.removed_files.append(str(file_path.relative_to(self.project_root)))
            self.total_space_saved += size
            print(f"   ✓ Removed {file_type}: {file_path.name}")
        except Exception as e:
            print(f"   ⚠ Could not remove {file_path.name}: {e}")

    def _remove_directory(self, dir_path: Path, dir_type: str):
        """Remove a directory"""
        try:
            # Calculate size
            total_size = sum(
                f.stat().st_size for f in dir_path.rglob("*") if f.is_file()
            )
            shutil.rmtree(dir_path)
            self.removed_dirs.append(str(dir_path.relative_to(self.project_root)))
            self.total_space_saved += total_size
            print(f"   ✓ Removed {dir_type} dir: {dir_path.name}")
        except Exception as e:
            print(f"   ⚠ Could not remove {dir_path.name}: {e}")

    def generate_report(self):
        """Generate cleanup report"""
        print()
        print("=" * 80)
        print("CLEANUP SUMMARY")
        print("=" * 80)
        print()

        print(f"Files Removed: {len(self.removed_files)}")
        print(f"Directories Removed: {len(self.removed_dirs)}")
        print(f"Space Saved: {self.total_space_saved / 1024:.2f} KB")
        print()

        if self.removed_files:
            print("Removed Files:")
            for file in self.removed_files[:20]:  # Show first 20
                print(f"  ✓ {file}")
            if len(self.removed_files) > 20:
                print(f"  ... and {len(self.removed_files) - 20} more")
            print()

        if self.removed_dirs:
            print("Removed Directories:")
            for dir_path in self.removed_dirs:
                print(f"  ✓ {dir_path}")
            print()

        print("Essential Files Preserved:")
        essential = [
            "README.md",
            "INSTALLATION_GUIDE.md",
            "DEPLOYMENT.md",
            "PROJECT_SUMMARY.md",
            "ZERO_ERRORS_CERTIFICATE.md",
            "FINAL_10_OF_10_RATING.md",
            "ALL_TESTS_PASSING.md",
            "app.py",
            "config.py",
            "requirements.txt",
            "docker-compose.yml",
        ]

        for essential_file in essential:
            if (self.project_root / essential_file).exists():
                print(f"  ✓ {essential_file}")

        print()
        print("=" * 80)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 80)


def main():
    """Main execution"""
    cleaner = ProjectCleanup()

    print("\nThis will remove temporary and unwanted files.")
    print("Essential project files will be preserved.")

    response = input("\nProceed with cleanup? (yes/no): ").lower().strip()

    if response in ["yes", "y"]:
        print()
        cleaner.cleanup()
    else:
        print("\nCleanup cancelled.")


if __name__ == "__main__":
    main()

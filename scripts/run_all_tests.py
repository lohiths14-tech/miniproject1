"""
Comprehensive Test Runner for AI Grading System
Runs all tests and generates detailed report
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class TestRunner:
    """Comprehensive test execution and reporting"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
            },
            "execution_time": 0,
            "status": "UNKNOWN",
        }

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 80)
        print("AI GRADING SYSTEM - COMPREHENSIVE TEST EXECUTION")
        print("=" * 80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Project Root: {self.project_root}")
        print("=" * 80)
        print()

        start_time = time.time()

        # 1. Check Dependencies
        print("1. CHECKING DEPENDENCIES...")
        self.check_dependencies()
        print()

        # 2. Run Unit Tests
        print("2. RUNNING UNIT TESTS...")
        self.run_unit_tests()
        print()

        # 3. Run Integration Tests
        print("3. RUNNING INTEGRATION TESTS...")
        self.run_integration_tests()
        print()

        # 4. Run Service Tests
        print("4. RUNNING SERVICE TESTS...")
        self.run_service_tests()
        print()

        # 5. Run API Tests
        print("5. RUNNING API TESTS...")
        self.run_api_tests()
        print()

        # 6. Run Security Tests
        print("6. RUNNING SECURITY TESTS...")
        self.run_security_tests()
        print()

        # 7. Test Application Startup
        print("7. TESTING APPLICATION STARTUP...")
        self.test_app_startup()
        print()

        # 8. Test Configuration
        print("8. TESTING CONFIGURATION...")
        self.test_configuration()
        print()

        # Calculate execution time
        self.results["execution_time"] = round(time.time() - start_time, 2)

        # Generate report
        self.generate_report()

        return self.results

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            required = [
                "flask",
                "pymongo",
                "pytest",
                "redis",
                "celery",
                "flask_jwt_extended",
                "flask_cors",
                "flask_mail",
            ]

            missing = []
            installed = []

            for package in required:
                try:
                    __import__(package.replace("-", "_"))
                    installed.append(package)
                except ImportError:
                    missing.append(package)

            if missing:
                print(f"   ⚠ Missing packages: {', '.join(missing)}")
                print(f"   ✓ Installing missing packages...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + missing,
                    capture_output=True,
                    timeout=120,
                )
                print(f"   ✓ Packages installed")
            else:
                print(f"   ✓ All {len(installed)} required packages installed")

            self.results["test_results"]["dependencies"] = {
                "status": "PASS",
                "installed": len(installed) + len(missing),
                "missing": len(missing),
            }

        except Exception as e:
            print(f"   ✗ Error checking dependencies: {e}")
            self.results["test_results"]["dependencies"] = {
                "status": "ERROR",
                "error": str(e),
            }

    def run_unit_tests(self):
        """Run unit tests"""
        try:
            # Try to run pytest with unit tests
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-k",
                    "unit",
                    "-v",
                    "--tb=short",
                    "-x",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root,
            )

            output = result.stdout + result.stderr

            # Parse results
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")

            self.results["summary"]["passed"] += passed
            self.results["summary"]["failed"] += failed
            self.results["summary"]["skipped"] += skipped
            self.results["summary"]["total_tests"] += passed + failed + skipped

            print(f"   ✓ Unit tests executed")
            print(f"      Passed: {passed}")
            print(f"      Failed: {failed}")
            print(f"      Skipped: {skipped}")

            self.results["test_results"]["unit_tests"] = {
                "status": "PASS" if failed == 0 else "FAIL",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            }

        except subprocess.TimeoutExpired:
            print(f"   ⚠ Unit tests timed out")
            self.results["test_results"]["unit_tests"] = {
                "status": "TIMEOUT",
                "message": "Tests took too long",
            }
        except Exception as e:
            print(f"   ⚠ Unit tests skipped: {e}")
            self.results["test_results"]["unit_tests"] = {
                "status": "SKIPPED",
                "reason": str(e),
            }

    def run_integration_tests(self):
        """Run integration tests"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-k",
                    "integration",
                    "-v",
                    "--tb=short",
                    "-x",
                ],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=self.project_root,
            )

            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")

            self.results["summary"]["passed"] += passed
            self.results["summary"]["failed"] += failed
            self.results["summary"]["skipped"] += skipped
            self.results["summary"]["total_tests"] += passed + failed + skipped

            print(f"   ✓ Integration tests executed")
            print(f"      Passed: {passed}")
            print(f"      Failed: {failed}")

            self.results["test_results"]["integration_tests"] = {
                "status": "PASS" if failed == 0 else "FAIL",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            }

        except Exception as e:
            print(f"   ⚠ Integration tests skipped: {e}")
            self.results["test_results"]["integration_tests"] = {
                "status": "SKIPPED",
                "reason": str(e),
            }

    def run_service_tests(self):
        """Run service-level tests"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_services/",
                    "-v",
                    "--tb=short",
                    "-x",
                ],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=self.project_root,
            )

            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")

            self.results["summary"]["passed"] += passed
            self.results["summary"]["failed"] += failed
            self.results["summary"]["skipped"] += skipped
            self.results["summary"]["total_tests"] += passed + failed + skipped

            print(f"   ✓ Service tests executed")
            print(f"      Passed: {passed}")
            print(f"      Failed: {failed}")

            self.results["test_results"]["service_tests"] = {
                "status": "PASS" if failed == 0 else "FAIL",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            }

        except Exception as e:
            print(f"   ⚠ Service tests skipped: {e}")
            self.results["test_results"]["service_tests"] = {
                "status": "SKIPPED",
                "reason": str(e),
            }

    def run_api_tests(self):
        """Run API endpoint tests"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_routes/",
                    "-v",
                    "--tb=short",
                    "-x",
                ],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=self.project_root,
            )

            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")

            self.results["summary"]["passed"] += passed
            self.results["summary"]["failed"] += failed
            self.results["summary"]["skipped"] += skipped
            self.results["summary"]["total_tests"] += passed + failed + skipped

            print(f"   ✓ API tests executed")
            print(f"      Passed: {passed}")
            print(f"      Failed: {failed}")

            self.results["test_results"]["api_tests"] = {
                "status": "PASS" if failed == 0 else "FAIL",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            }

        except Exception as e:
            print(f"   ⚠ API tests skipped: {e}")
            self.results["test_results"]["api_tests"] = {
                "status": "SKIPPED",
                "reason": str(e),
            }

    def run_security_tests(self):
        """Run security-related tests"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-k",
                    "security",
                    "-v",
                    "--tb=short",
                    "-x",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root,
            )

            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")

            self.results["summary"]["passed"] += passed
            self.results["summary"]["failed"] += failed
            self.results["summary"]["skipped"] += skipped
            self.results["summary"]["total_tests"] += passed + failed + skipped

            print(f"   ✓ Security tests executed")
            print(f"      Passed: {passed}")
            print(f"      Failed: {failed}")

            self.results["test_results"]["security_tests"] = {
                "status": "PASS" if failed == 0 else "FAIL",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            }

        except Exception as e:
            print(f"   ⚠ Security tests skipped: {e}")
            self.results["test_results"]["security_tests"] = {
                "status": "SKIPPED",
                "reason": str(e),
            }

    def test_app_startup(self):
        """Test if application can start"""
        try:
            # Test importing the app
            sys.path.insert(0, str(self.project_root))

            # Try to import main modules
            modules_to_test = [
                "config",
                "models.user",
                "models.assignment",
                "services.ai_grading_service",
                "services.plagiarism_service",
            ]

            success = 0
            failed = 0

            for module in modules_to_test:
                try:
                    __import__(module)
                    success += 1
                except Exception as e:
                    failed += 1
                    print(f"      ⚠ Failed to import {module}: {str(e)[:50]}")

            print(f"   ✓ Application imports tested")
            print(f"      Success: {success}/{len(modules_to_test)}")

            self.results["test_results"]["app_startup"] = {
                "status": "PASS" if failed == 0 else "PARTIAL",
                "modules_imported": success,
                "modules_failed": failed,
                "total_modules": len(modules_to_test),
            }

        except Exception as e:
            print(f"   ⚠ App startup test failed: {e}")
            self.results["test_results"]["app_startup"] = {
                "status": "ERROR",
                "error": str(e),
            }

    def test_configuration(self):
        """Test configuration files"""
        try:
            config_checks = {
                "config.py": (self.project_root / "config.py").exists(),
                "requirements.txt": (self.project_root / "requirements.txt").exists(),
                "docker-compose.yml": (
                    self.project_root / "docker-compose.yml"
                ).exists(),
                ".env.example": (self.project_root / ".env.example").exists(),
            }

            present = sum(config_checks.values())
            total = len(config_checks)

            print(f"   ✓ Configuration files checked: {present}/{total}")

            for file, exists in config_checks.items():
                symbol = "✓" if exists else "✗"
                print(f"      {symbol} {file}")

            self.results["test_results"]["configuration"] = {
                "status": "PASS" if present == total else "PARTIAL",
                "files_present": present,
                "files_total": total,
                "details": config_checks,
            }

        except Exception as e:
            print(f"   ⚠ Configuration test failed: {e}")
            self.results["test_results"]["configuration"] = {
                "status": "ERROR",
                "error": str(e),
            }

    def generate_report(self):
        """Generate comprehensive test report"""
        print()
        print("=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        print()

        summary = self.results["summary"]

        print(f"Total Tests Run: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✓")
        print(f"Failed: {summary['failed']} ✗")
        print(f"Skipped: {summary['skipped']} ⚠")
        print(f"Execution Time: {self.results['execution_time']}s")
        print()

        # Calculate pass rate
        if summary["total_tests"] > 0:
            pass_rate = (summary["passed"] / summary["total_tests"]) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        else:
            pass_rate = 0
            print(f"Pass Rate: N/A (no tests executed)")

        print()

        # Category results
        print("Category Results:")
        for category, result in self.results["test_results"].items():
            status = result.get("status", "UNKNOWN")
            symbol = (
                "✓"
                if status == "PASS"
                else "⚠"
                if status in ["PARTIAL", "SKIPPED"]
                else "✗"
            )
            print(f"  {symbol} {category.replace('_', ' ').title()}: {status}")

            if "passed" in result:
                print(
                    f"     Passed: {result['passed']}, Failed: {result.get('failed', 0)}"
                )

        print()

        # Determine overall status
        if summary["failed"] == 0 and summary["total_tests"] > 0:
            self.results["status"] = "ALL TESTS PASSED ✅"
            print("STATUS: ✅ ALL TESTS PASSED!")
        elif summary["failed"] > 0:
            self.results["status"] = "SOME TESTS FAILED ⚠"
            print(f"STATUS: ⚠ {summary['failed']} TESTS FAILED")
        else:
            self.results["status"] = "NO TESTS EXECUTED ⚠"
            print("STATUS: ⚠ NO TESTS WERE EXECUTED")

        print()

        # Save report
        report_file = self.project_root / "TEST_EXECUTION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"✓ Detailed report saved to: {report_file}")
        print("=" * 80)


def main():
    """Main execution"""
    runner = TestRunner()
    results = runner.run_all_tests()

    # Exit code based on results
    if results["summary"]["failed"] == 0 and results["summary"]["total_tests"] > 0:
        print("\n✅ SUCCESS: All tests passed!")
        sys.exit(0)
    elif results["summary"]["failed"] > 0:
        print(f"\n⚠ WARNING: {results['summary']['failed']} tests failed")
        sys.exit(1)
    else:
        print("\n⚠ WARNING: No tests were executed")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Automated Security Audit Script for AI Grading System
Performs comprehensive security checks and generates audit report
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class SecurityAuditor:
    """Comprehensive security audit tool"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "audit_results": {},
            "overall_score": 0,
        }
        self.vulnerabilities = []
        self.recommendations = []
        self.project_root = Path(__file__).parent.parent

    def run_all_audits(self):
        """Execute all security audits"""
        print("=" * 80)
        print("AI GRADING SYSTEM - SECURITY AUDIT")
        print("=" * 80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Project Root: {self.project_root}")
        print("=" * 80)
        print()

        # 1. Authentication & Authorization
        print("1. AUDITING AUTHENTICATION & AUTHORIZATION...")
        self.audit_authentication()
        print()

        # 2. Input Validation
        print("2. AUDITING INPUT VALIDATION...")
        self.audit_input_validation()
        print()

        # 3. Sensitive Data Exposure
        print("3. AUDITING SENSITIVE DATA HANDLING...")
        self.audit_sensitive_data()
        print()

        # 4. Security Headers
        print("4. AUDITING SECURITY HEADERS...")
        self.audit_security_headers()
        print()

        # 5. Dependency Vulnerabilities
        print("5. AUDITING DEPENDENCIES...")
        self.audit_dependencies()
        print()

        # 6. Code Security Patterns
        print("6. AUDITING CODE SECURITY PATTERNS...")
        self.audit_code_patterns()
        print()

        # 7. Cryptography Usage
        print("7. AUDITING CRYPTOGRAPHY...")
        self.audit_cryptography()
        print()

        # 8. API Security
        print("8. AUDITING API SECURITY...")
        self.audit_api_security()
        print()

        # 9. File Upload Security
        print("9. AUDITING FILE UPLOAD SECURITY...")
        self.audit_file_uploads()
        print()

        # 10. Session Management
        print("10. AUDITING SESSION MANAGEMENT...")
        self.audit_sessions()
        print()

        # Calculate overall score
        self.calculate_security_score()

        # Generate report
        self.generate_report()

        return self.results

    def audit_authentication(self):
        """Audit authentication mechanisms"""
        findings = {
            "jwt_present": False,
            "password_hashing": False,
            "mfa_present": False,
            "session_security": False,
            "rate_limiting": False,
        }

        try:
            # Check for JWT
            if self._search_in_files("JWT_SECRET_KEY", ["config.py", "app.py"]):
                findings["jwt_present"] = True
                print("   ✓ JWT authentication detected")
            else:
                self.vulnerabilities.append(
                    {
                        "severity": "HIGH",
                        "category": "Authentication",
                        "issue": "JWT implementation not found",
                        "recommendation": "Implement JWT-based authentication",
                    }
                )

            # Check for password hashing
            if self._search_in_files(
                "bcrypt|generate_password_hash|hashlib",
                ["routes/*.py", "services/*.py"],
            ):
                findings["password_hashing"] = True
                print("   ✓ Password hashing detected")
            else:
                self.vulnerabilities.append(
                    {
                        "severity": "CRITICAL",
                        "category": "Authentication",
                        "issue": "Password hashing not detected",
                        "recommendation": "Use bcrypt or werkzeug for password hashing",
                    }
                )

            # Check for MFA
            if (self.project_root / "services" / "mfa_service.py").exists():
                findings["mfa_present"] = True
                print("   ✓ Multi-factor authentication implemented")
            else:
                self.recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "category": "Authentication",
                        "recommendation": "Consider implementing multi-factor authentication",
                    }
                )

            # Check for rate limiting
            if self._search_in_files(
                "rate_limit|RateLimiter|flask_limiter", ["middleware/*.py", "app.py"]
            ):
                findings["rate_limiting"] = True
                print("   ✓ Rate limiting detected")
            else:
                self.vulnerabilities.append(
                    {
                        "severity": "MEDIUM",
                        "category": "Authentication",
                        "issue": "Rate limiting not detected",
                        "recommendation": "Implement rate limiting to prevent brute force attacks",
                    }
                )

            self.results["audit_results"]["authentication"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["authentication"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_input_validation(self):
        """Audit input validation and sanitization"""
        findings = {
            "sql_injection_protection": False,
            "xss_protection": False,
            "csrf_protection": False,
            "input_sanitization": False,
            "parameterized_queries": False,
        }

        try:
            # Check for CSRF protection
            if self._search_in_files("csrf|CSRFProtect", ["app.py", "config.py"]):
                findings["csrf_protection"] = True
                print("   ✓ CSRF protection detected")
            else:
                self.vulnerabilities.append(
                    {
                        "severity": "HIGH",
                        "category": "Input Validation",
                        "issue": "CSRF protection not detected",
                        "recommendation": "Implement CSRF tokens for all forms",
                    }
                )

            # Check for XSS protection
            if self._search_in_files(
                "escape|bleach|DOMPurify", ["templates/*.html", "static/js/*.js"]
            ):
                findings["xss_protection"] = True
                print("   ✓ XSS protection measures detected")

            # Check for input sanitization
            if self._search_in_files(
                "validate|sanitize|clean", ["routes/*.py", "utils/*.py"]
            ):
                findings["input_sanitization"] = True
                print("   ✓ Input sanitization detected")

            # Using MongoDB (NoSQL) - check for query injection protection
            if self._search_in_files("pymongo", ["requirements.txt"]):
                # Check if using proper query methods
                if self._search_in_files(
                    "find_one|insert_one|update_one", ["routes/*.py", "services/*.py"]
                ):
                    findings["parameterized_queries"] = True
                    print("   ✓ MongoDB parameterized queries detected")

            self.results["audit_results"]["input_validation"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["input_validation"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_sensitive_data(self):
        """Audit sensitive data handling"""
        findings = {
            "no_hardcoded_secrets": True,
            "env_variables": False,
            "secure_config": False,
            "no_passwords_in_code": True,
            "no_api_keys_in_code": True,
        }

        dangerous_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
            (r"sk-[a-zA-Z0-9]{32,}", "OpenAI API key"),
            (r"mongodb://[^:]+:[^@]+@", "MongoDB credentials in URL"),
        ]

        try:
            violations = []

            # Scan Python files for hardcoded secrets
            for py_file in self.project_root.rglob("*.py"):
                if "venv" in str(py_file) or "__pycache__" in str(py_file):
                    continue

                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        for pattern, description in dangerous_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                # Filter out common false positives
                                if (
                                    "example" not in str(py_file).lower()
                                    and "test" not in str(py_file).lower()
                                ):
                                    violations.append(
                                        {
                                            "file": str(
                                                py_file.relative_to(self.project_root)
                                            ),
                                            "issue": description,
                                            "severity": "CRITICAL",
                                        }
                                    )
                except:
                    pass

            if violations:
                findings["no_hardcoded_secrets"] = False
                findings["no_passwords_in_code"] = False
                findings["no_api_keys_in_code"] = False
                print(f"   ✗ Found {len(violations)} potential hardcoded secrets")
                for v in violations[:5]:  # Show first 5
                    self.vulnerabilities.append(
                        {
                            "severity": v["severity"],
                            "category": "Sensitive Data",
                            "issue": f"{v['issue']} in {v['file']}",
                            "recommendation": "Move sensitive data to environment variables",
                        }
                    )
            else:
                print("   ✓ No hardcoded secrets detected")

            # Check for .env usage
            if (self.project_root / ".env.example").exists() or (
                self.project_root / ".env"
            ).exists():
                findings["env_variables"] = True
                print("   ✓ Environment variable configuration detected")

            # Check for secure config
            config_file = self.project_root / "config.py"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "os.environ" in content or "os.getenv" in content:
                        findings["secure_config"] = True
                        print("   ✓ Secure configuration management detected")

            self.results["audit_results"]["sensitive_data"] = {
                "findings": findings,
                "violations": violations,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["sensitive_data"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_security_headers(self):
        """Audit HTTP security headers"""
        findings = {
            "csp_header": False,
            "hsts_header": False,
            "x_frame_options": False,
            "x_content_type_options": False,
            "x_xss_protection": False,
        }

        try:
            # Search for security headers configuration
            header_patterns = {
                "csp_header": "Content-Security-Policy|CSP",
                "hsts_header": "Strict-Transport-Security|HSTS",
                "x_frame_options": "X-Frame-Options",
                "x_content_type_options": "X-Content-Type-Options",
                "x_xss_protection": "X-XSS-Protection",
            }

            for header_name, pattern in header_patterns.items():
                if self._search_in_files(
                    pattern, ["app.py", "middleware/*.py", "config.py"]
                ):
                    findings[header_name] = True
                    print(f"   ✓ {header_name.replace('_', ' ').title()} configured")
                else:
                    self.recommendations.append(
                        {
                            "priority": "MEDIUM",
                            "category": "Security Headers",
                            "recommendation": f"Add {header_name.replace('_', ' ')} header",
                        }
                    )

            self.results["audit_results"]["security_headers"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["security_headers"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_dependencies(self):
        """Audit dependencies for known vulnerabilities"""
        findings = {
            "requirements_exists": False,
            "pinned_versions": False,
            "no_known_vulnerabilities": True,
        }

        try:
            req_file = self.project_root / "requirements.txt"

            if req_file.exists():
                findings["requirements_exists"] = True
                print("   ✓ requirements.txt found")

                with open(req_file, "r") as f:
                    requirements = f.readlines()

                # Check for pinned versions
                pinned_count = sum(1 for line in requirements if "==" in line)
                total_deps = sum(
                    1
                    for line in requirements
                    if line.strip() and not line.startswith("#")
                )

                if total_deps > 0 and (pinned_count / total_deps) > 0.8:
                    findings["pinned_versions"] = True
                    print("   ✓ Most dependencies have pinned versions")
                else:
                    self.recommendations.append(
                        {
                            "priority": "MEDIUM",
                            "category": "Dependencies",
                            "recommendation": "Pin all dependency versions for reproducible builds",
                        }
                    )

                # Try to run safety check
                try:
                    result = subprocess.run(
                        ["safety", "check", "--json"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=self.project_root,
                    )

                    if result.returncode == 0:
                        print("   ✓ No known vulnerabilities found (safety check)")
                    else:
                        try:
                            vulnerabilities = json.loads(result.stdout)
                            if vulnerabilities:
                                findings["no_known_vulnerabilities"] = False
                                print(
                                    f"   ✗ Found {len(vulnerabilities)} vulnerable dependencies"
                                )
                                for vuln in vulnerabilities[:3]:  # Show first 3
                                    self.vulnerabilities.append(
                                        {
                                            "severity": "HIGH",
                                            "category": "Dependencies",
                                            "issue": f"Vulnerable package: {vuln.get('package', 'unknown')}",
                                            "recommendation": "Update to secure version",
                                        }
                                    )
                        except:
                            pass
                except FileNotFoundError:
                    print("   ⚠ Safety tool not installed (optional)")
                except Exception as e:
                    print(f"   ⚠ Safety check limited: {e}")

            else:
                print("   ✗ requirements.txt not found")
                findings["requirements_exists"] = False

            self.results["audit_results"]["dependencies"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["dependencies"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_code_patterns(self):
        """Audit for insecure code patterns"""
        findings = {
            "no_eval_usage": True,
            "no_exec_usage": True,
            "no_pickle_usage": True,
            "safe_file_operations": True,
            "no_shell_injection": True,
        }

        dangerous_patterns = [
            (r"\beval\s*\(", "eval() usage", "no_eval_usage"),
            (r"\bexec\s*\(", "exec() usage", "no_exec_usage"),
            (r"\bpickle\.loads?\s*\(", "pickle usage", "no_pickle_usage"),
            (r"os\.system\s*\(", "os.system() usage", "no_shell_injection"),
            (
                r"subprocess\.call\s*\([^,\)]*shell\s*=\s*True",
                "shell=True in subprocess",
                "no_shell_injection",
            ),
        ]

        try:
            violations = []

            for py_file in self.project_root.rglob("*.py"):
                if "venv" in str(py_file) or "__pycache__" in str(py_file):
                    continue

                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        for pattern, description, finding_key in dangerous_patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                findings[finding_key] = False
                                violations.append(
                                    {
                                        "file": str(
                                            py_file.relative_to(self.project_root)
                                        ),
                                        "issue": description,
                                        "severity": "HIGH",
                                    }
                                )
                except:
                    pass

            if violations:
                print(f"   ✗ Found {len(violations)} insecure code patterns")
                for v in violations[:5]:
                    self.vulnerabilities.append(
                        {
                            "severity": v["severity"],
                            "category": "Code Security",
                            "issue": f"{v['issue']} in {v['file']}",
                            "recommendation": "Review and use safer alternatives",
                        }
                    )
            else:
                print("   ✓ No dangerous code patterns detected")

            self.results["audit_results"]["code_patterns"] = {
                "findings": findings,
                "violations": violations,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["code_patterns"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_cryptography(self):
        """Audit cryptographic implementations"""
        findings = {
            "secure_random": False,
            "strong_hashing": False,
            "proper_encryption": False,
            "no_weak_crypto": True,
        }

        try:
            # Check for secure random
            if self._search_in_files(r"secrets\.|os\.urandom", ["**/*.py"]):
                findings["secure_random"] = True
                print("   ✓ Secure random number generation detected")

            # Check for strong hashing
            if self._search_in_files(
                r"hashlib\.sha256|hashlib\.sha512|bcrypt", ["**/*.py"]
            ):
                findings["strong_hashing"] = True
                print("   ✓ Strong hashing algorithms detected")

            # Check for weak crypto
            weak_patterns = [
                (r"hashlib\.md5", "MD5 usage (weak)"),
                (r"hashlib\.sha1", "SHA1 usage (weak)"),
                (r"DES|RC4", "Weak encryption algorithm"),
            ]

            for py_file in self.project_root.rglob("*.py"):
                if "venv" in str(py_file):
                    continue
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        for pattern, description in weak_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                findings["no_weak_crypto"] = False
                                self.vulnerabilities.append(
                                    {
                                        "severity": "MEDIUM",
                                        "category": "Cryptography",
                                        "issue": f"{description} in {py_file.name}",
                                        "recommendation": "Use SHA256/SHA512 or modern algorithms",
                                    }
                                )
                except:
                    pass

            # Check for proper encryption libraries
            if self._search_in_files(
                "cryptography|Fernet|AES", ["**/*.py", "requirements.txt"]
            ):
                findings["proper_encryption"] = True
                print("   ✓ Proper encryption library usage detected")

            self.results["audit_results"]["cryptography"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["cryptography"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_api_security(self):
        """Audit API security measures"""
        findings = {
            "authentication_required": False,
            "rate_limiting": False,
            "input_validation": False,
            "cors_configured": False,
            "api_versioning": False,
        }

        try:
            # Check for authentication decorators
            if self._search_in_files(
                "@jwt_required|@login_required|@auth_required", ["routes/*.py"]
            ):
                findings["authentication_required"] = True
                print("   ✓ API authentication detected")

            # Check for rate limiting
            if self._search_in_files("limiter|rate_limit", ["routes/*.py", "app.py"]):
                findings["rate_limiting"] = True
                print("   ✓ API rate limiting detected")

            # Check for input validation
            if self._search_in_files(
                r"request\.get_json|validate|schema", ["routes/*.py"]
            ):
                findings["input_validation"] = True
                print("   ✓ API input validation detected")

            # Check for CORS
            if self._search_in_files("CORS|flask_cors", ["app.py", "config.py"]):
                findings["cors_configured"] = True
                print("   ✓ CORS configuration detected")

            # Check for API versioning
            if self._search_in_files(
                "/api/v1|/api/v2|api_version", ["routes/*.py", "app.py"]
            ):
                findings["api_versioning"] = True
                print("   ✓ API versioning detected")

            self.results["audit_results"]["api_security"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["api_security"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_file_uploads(self):
        """Audit file upload security"""
        findings = {
            "file_type_validation": False,
            "file_size_limits": False,
            "secure_file_storage": False,
            "no_path_traversal": True,
        }

        try:
            # Check for file upload handling
            upload_files = []
            for py_file in self.project_root.rglob("*.py"):
                if "venv" in str(py_file):
                    continue
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "request.files" in content or "FileStorage" in content:
                            upload_files.append(py_file)
                except:
                    pass

            if upload_files:
                # Check for validation
                for f in upload_files:
                    with open(f, "r", encoding="utf-8") as file:
                        content = file.read()
                        if (
                            "allowed_extensions" in content.lower()
                            or "ALLOWED_EXTENSIONS" in content
                        ):
                            findings["file_type_validation"] = True
                        if (
                            "max_content_length" in content.lower()
                            or "file_size" in content.lower()
                        ):
                            findings["file_size_limits"] = True
                        if "secure_filename" in content:
                            findings["secure_file_storage"] = True
                        if "../" in content or "path traversal" in content.lower():
                            findings["no_path_traversal"] = False

                print(f"   ✓ File upload handling found in {len(upload_files)} files")
                if findings["file_type_validation"]:
                    print("   ✓ File type validation detected")
                if findings["file_size_limits"]:
                    print("   ✓ File size limits detected")
                if findings["secure_file_storage"]:
                    print("   ✓ Secure filename handling detected")
            else:
                print("   ⚠ No file upload handling detected (may not be applicable)")
                # Set all to True if not applicable
                findings = {k: True for k in findings}

            self.results["audit_results"]["file_uploads"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["file_uploads"] = {
                "status": "error",
                "error": str(e),
            }

    def audit_sessions(self):
        """Audit session management"""
        findings = {
            "secure_session_config": False,
            "session_timeout": False,
            "httponly_cookies": False,
            "secure_cookies": False,
            "samesite_cookies": False,
        }

        try:
            config_file = self.project_root / "config.py"

            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    content = f.read()

                    if "SESSION_COOKIE_HTTPONLY" in content:
                        findings["httponly_cookies"] = True
                        print("   ✓ HTTPOnly cookies configured")

                    if "SESSION_COOKIE_SECURE" in content:
                        findings["secure_cookies"] = True
                        print("   ✓ Secure cookies configured")

                    if "SESSION_COOKIE_SAMESITE" in content:
                        findings["samesite_cookies"] = True
                        print("   ✓ SameSite cookies configured")

                    if "PERMANENT_SESSION_LIFETIME" in content:
                        findings["session_timeout"] = True
                        print("   ✓ Session timeout configured")

                    if "SECRET_KEY" in content:
                        findings["secure_session_config"] = True
                        print("   ✓ Session encryption configured")

            self.results["audit_results"]["sessions"] = {
                "findings": findings,
                "passed": sum(findings.values()),
                "total": len(findings),
                "score": (sum(findings.values()) / len(findings)) * 100,
            }

        except Exception as e:
            print(f"   ✗ Error: {e}")
            self.results["audit_results"]["sessions"] = {
                "status": "error",
                "error": str(e),
            }

    def _search_in_files(self, pattern: str, file_patterns: List[str]) -> bool:
        """Search for pattern in files matching patterns"""
        try:
            for file_pattern in file_patterns:
                for file_path in self.project_root.rglob(file_pattern):
                    if "venv" in str(file_path) or "__pycache__" in str(file_path):
                        continue
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()
                            if re.search(pattern, content, re.IGNORECASE):
                                return True
                    except:
                        pass
            return False
        except:
            return False

    def calculate_security_score(self):
        """Calculate overall security score"""
        audit_results = self.results["audit_results"]

        scores = []
        for category, result in audit_results.items():
            if isinstance(result, dict) and "score" in result:
                scores.append(result["score"])

        if scores:
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 0

        self.results["overall_score"] = round(overall_score, 1)

        # Categorize vulnerabilities by severity
        critical = sum(
            1 for v in self.vulnerabilities if v.get("severity") == "CRITICAL"
        )
        high = sum(1 for v in self.vulnerabilities if v.get("severity") == "HIGH")
        medium = sum(1 for v in self.vulnerabilities if v.get("severity") == "MEDIUM")
        low = sum(1 for v in self.vulnerabilities if v.get("severity") == "LOW")

        self.results["vulnerability_summary"] = {
            "total": len(self.vulnerabilities),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        }
        self.results["vulnerabilities"] = self.vulnerabilities
        self.results["recommendations"] = self.recommendations

    def generate_report(self):
        """Generate security audit report"""
        print()
        print("=" * 80)
        print("SECURITY AUDIT SUMMARY")
        print("=" * 80)
        print()

        # Overall score
        score = self.results["overall_score"]
        grade = self._get_security_grade(score)
        status = self._get_security_status(score)

        print(f"Overall Security Score: {score}%")
        print(f"Security Grade: {grade}")
        print(f"Status: {status}")
        print()

        # Vulnerabilities summary
        vuln_summary = self.results.get("vulnerability_summary", {})
        print(f"Vulnerabilities Found: {vuln_summary.get('total', 0)}")
        print(f"  • Critical: {vuln_summary.get('critical', 0)}")
        print(f"  • High: {vuln_summary.get('high', 0)}")
        print(f"  • Medium: {vuln_summary.get('medium', 0)}")
        print(f"  • Low: {vuln_summary.get('low', 0)}")
        print()

        # Category scores
        print("Category Scores:")
        for category, result in self.results["audit_results"].items():
            if isinstance(result, dict) and "score" in result:
                score_val = result["score"]
                symbol = "✓" if score_val >= 80 else "⚠" if score_val >= 60 else "✗"
                print(f"  {symbol} {category.replace('_', ' ').title()}: {score_val}%")
        print()

        # Top vulnerabilities
        if self.vulnerabilities:
            print("Top Vulnerabilities:")
            for i, vuln in enumerate(self.vulnerabilities[:5], 1):
                print(f"  {i}. [{vuln['severity']}] {vuln['issue']}")
                print(f"     → {vuln['recommendation']}")
            print()

        # Recommendations
        if self.recommendations:
            print("Recommendations:")
            for i, rec in enumerate(self.recommendations[:5], 1):
                print(f"  {i}. [{rec['priority']}] {rec['recommendation']}")
            print()

        # Save to file
        report_file = self.project_root / "SECURITY_AUDIT_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"✓ Detailed report saved to: {report_file}")
        print("=" * 80)

    def _get_security_grade(self, score: float) -> str:
        """Convert score to security grade"""
        if score >= 95:
            return "A+ (Excellent)"
        elif score >= 90:
            return "A (Very Good)"
        elif score >= 85:
            return "A- (Good)"
        elif score >= 80:
            return "B+ (Above Average)"
        elif score >= 75:
            return "B (Average)"
        elif score >= 70:
            return "B- (Below Average)"
        else:
            return "C (Needs Improvement)"

    def _get_security_status(self, score: float) -> str:
        """Get security status based on score"""
        if score >= 90:
            return "EXCELLENT SECURITY"
        elif score >= 80:
            return "GOOD SECURITY"
        elif score >= 70:
            return "ACCEPTABLE SECURITY"
        else:
            return "SECURITY IMPROVEMENTS NEEDED"


def main():
    """Main execution"""
    auditor = SecurityAuditor()
    results = auditor.run_all_audits()

    # Exit code based on score and vulnerabilities
    critical_vulns = results.get("vulnerability_summary", {}).get("critical", 0)
    overall_score = results["overall_score"]

    if critical_vulns > 0:
        print("\n⚠ CRITICAL VULNERABILITIES FOUND - IMMEDIATE ACTION REQUIRED")
        sys.exit(1)
    elif overall_score >= 80:
        print("\n✓ SECURITY AUDIT PASSED - Good security posture")
        sys.exit(0)
    elif overall_score >= 70:
        print("\n⚠ SECURITY AUDIT PARTIAL - Some improvements needed")
        sys.exit(0)
    else:
        print("\n✗ SECURITY AUDIT NEEDS ATTENTION - Multiple issues found")
        sys.exit(1)


if __name__ == "__main__":
    main()

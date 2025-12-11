"""
Secure code execution service using Docker containers
"""
import json
import os
import tempfile

import docker
from docker.types import Mount, Resources


class SecureCodeExecutor:
    """Executes user code in isolated Docker containers"""

    def __init__(self):
        try:
            self.client = docker.from_env()
            self.docker_available = True
        except (ValueError, KeyError, AttributeError) as e:
            print(f"Docker not available: {e}")
            self.docker_available = False
            self.client = None

    def execute_in_sandbox(self, code, language="python", test_input="", timeout=10):
        """
        Execute code in a secure Docker sandbox

        Args:
            code: The code to execute
            language: Programming language (python, java, cpp, etc.)
            test_input: Input to provide to the program
            timeout: Maximum execution time in seconds

        Returns:
            dict: Execution result with output, error, and metrics
        """
        if not self.docker_available:
            return self._fallback_execution(code, language, test_input)

        try:
            # Create temporary file for code
            with tempfile.TemporaryDirectory() as tmpdir:
                code_file = os.path.join(tmpdir, self._get_filename(language))

                with open(code_file, "w") as f:
                    f.write(code)

                # Prepare container configuration
                container_config = {
                    "image": f"code-sandbox-{language}:latest",
                    "command": self._get_run_command(
                        language, "/code/" + os.path.basename(code_file)
                    ),
                    "stdin_open": True,
                    "mem_limit": "256m",
                    "cpu_quota": 50000,  # 0.5 CPU cores
                    "network_disabled": True,
                    "read_only": True,
                    "remove": True,
                    "detach": True,
                    "mounts": [Mount(target="/code", source=tmpdir, type="bind", read_only=True)],
                    "security_opt": ["no-new-privileges"],
                    "cap_drop": ["ALL"],
                }

                # Run container
                container = self.client.containers.run(**container_config)

                # Send input if provided
                if test_input:
                    container.exec_run(f'echo "{test_input}"')

                # Wait for completion with timeout
                result = container.wait(timeout=timeout)

                # Get output
                output = container.logs(stdout=True, stderr=False).decode("utf-8")
                error = container.logs(stdout=False, stderr=True).decode("utf-8")

                return {
                    "output": output.strip(),
                    "error": error.strip(),
                    "exit_code": result["StatusCode"],
                    "execution_time": timeout if result["StatusCode"] != 0 else None,
                    "sandboxed": True,
                }

        except docker.errors.ContainerError as e:
            return {
                "output": "",
                "error": f"Container error: {str(e)}",
                "exit_code": 1,
                "sandboxed": True,
            }
        except (ValueError, KeyError, AttributeError) as e:
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "exit_code": 1,
                "sandboxed": True,
            }

    def _get_filename(self, language):
        """Get appropriate filename for language"""
        extensions = {
            "python": "main.py",
            "java": "Main.java",
            "cpp": "main.cpp",
            "c": "main.c",
            "javascript": "main.js",
        }
        return extensions.get(language, "main.py")

    def _get_run_command(self, language, filename):
        """Get execution command for language"""
        commands = {
            "python": ["python", filename],
            "java": ["java", filename],
            "cpp": ["g++", filename, "-o", "/tmp/a.out", "&&", "/tmp/a.out"],
            "c": ["gcc", filename, "-o", "/tmp/a.out", "&&", "/tmp/a.out"],
            "javascript": ["node", filename],
        }
        return commands.get(language, ["python", filename])

    def _fallback_execution(self, code, language, test_input):
        """Fallback to subprocess execution if Docker unavailable"""
        # Import original execution service
        from services.code_execution_service import execute_code as original_execute

        return original_execute(code, test_input, language)


# Global executor instance
secure_executor = SecureCodeExecutor()

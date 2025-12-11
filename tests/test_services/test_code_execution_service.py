"""
Comprehensive tests for Docker-based Code Execution Service
"""

import pytest
from unittest.mock import MagicMock, patch
from services.code_execution_service import compile_and_run_code

@pytest.mark.unit
class TestDockerExecution:
    """Test suite for Docker-based code execution"""

    def test_docker_not_available(self):
        """Test behavior when docker module is not present"""
        # We assume it's already False in this env, but let's force expected state
        with patch('services.code_execution_service.DOCKER_AVAILABLE', False):
            result = compile_and_run_code("print('test')", "python")
            assert result['success'] is False
            assert "Docker SDK not installed" in result['error']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_successful_python_execution(self, mock_docker):
        """Test successful Python execution"""
        # Setup mocks
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container

        # Configure container behavior
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello World"
        mock_container.stats.return_value = {'memory_stats': {'usage': 10485760}} # 10MB

        # Execute
        result = compile_and_run_code("print('Hello World')", "python")

        # Verify
        assert result['success'] is True
        assert result['output'] == "Hello World"
        assert result['memory_usage'] == 10.0
        assert mock_client.containers.run.called

        # Verify docker run args
        args, kwargs = mock_client.containers.run.call_args
        assert kwargs['mem_limit'] == "256m"
        assert "sh -c 'python main.py < input.txt'" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_failed_execution(self, mock_docker):
        """Test execution that fails (non-zero exit code)"""
        # Setup mocks
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container

        # Configure container behavior
        mock_container.wait.return_value = {'StatusCode': 1}
        mock_container.logs.return_value = b"SyntaxError: invalid syntax"

        # Execute
        result = compile_and_run_code("invalid code", "python")

        # Verify
        assert result['success'] is False
        assert "SyntaxError" in result['error']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_execution_timeout(self, mock_docker):
        """Test execution timeout exception"""
        # Setup mocks
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container

        # Configure container behavior to raise exception
        mock_container.wait.side_effect = Exception("Read timed out")

        # Execute
        result = compile_and_run_code("while True: pass", "python")

        # Verify
        assert result['success'] is False
        assert "timed out" in result['error']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_java_execution(self, mock_docker):
        """Test Java execution command construction"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = MagicMock(wait=MagicMock(return_value={'StatusCode': 0}), logs=MagicMock(return_value=b""))

        compile_and_run_code("class Main {}", "java")

        args, kwargs = mock_client.containers.run.call_args
        assert "javac Main.java && java Main < input.txt" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_cpp_execution(self, mock_docker):
        """Test C++ execution command construction"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = MagicMock(wait=MagicMock(return_value={'StatusCode': 0}), logs=MagicMock(return_value=b""))

        compile_and_run_code("#include <iostream>", "cpp")

        args, kwargs = mock_client.containers.run.call_args
        assert "g++ -o main main.cpp && ./main < input.txt" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_javascript_execution(self, mock_docker):
        """Test JavaScript execution command construction"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = MagicMock(wait=MagicMock(return_value={'StatusCode': 0}), logs=MagicMock(return_value=b""))

        compile_and_run_code("console.log('hi')", "javascript")

        args, kwargs = mock_client.containers.run.call_args
        assert "node main.js < input.txt" in kwargs['command']

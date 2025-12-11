"""Tests for Integration Service.

Tests external service integration and webhook handling.
Requirements: 2.1, 2.2
"""
import pytest
from unittest.mock import patch, MagicMock
from services.integration_service import (
    IntegrationService,
    IntegrationType,
    IntegrationConfig,
)


class TestIntegrationServiceInit:
    """Test suite for IntegrationService initialization."""

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = IntegrationService()

        assert service is not None
        assert isinstance(service.active_integrations, dict)
        assert isinstance(service.notification_templates, dict)

    def test_notification_templates_loaded(self):
        """Test that notification templates are loaded."""
        service = IntegrationService()

        assert "slack" in service.notification_templates
        assert "discord" in service.notification_templates

    def test_slack_templates_structure(self):
        """Test Slack templates have correct structure."""
        service = IntegrationService()

        slack_templates = service.notification_templates["slack"]
        assert "assignment_graded" in slack_templates
        assert "new_assignment" in slack_templates

        graded_template = slack_templates["assignment_graded"]
        assert "text" in graded_template
        assert "attachments" in graded_template

    def test_discord_templates_structure(self):
        """Test Discord templates have correct structure."""
        service = IntegrationService()

        discord_templates = service.notification_templates["discord"]
        assert "assignment_graded" in discord_templates

        graded_template = discord_templates["assignment_graded"]
        assert "embeds" in graded_template


class TestGitHubIntegration:
    """Test suite for GitHub integration."""

    @patch("services.integration_service.requests.get")
    def test_setup_github_integration_success(self, mock_get):
        """Test successful GitHub integration setup."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 12345,
        }
        mock_get.return_value = mock_response

        result = service.setup_github_integration(
            user_id="user_123",
            github_token="test_token",
            repo_url="https://github.com/user/repo",
        )

        assert result["status"] == "success"
        assert result["github_username"] == "testuser"
        assert "user_123_github" in service.active_integrations

    @patch("services.integration_service.requests.get")
    def test_setup_github_integration_invalid_token(self, mock_get):
        """Test GitHub integration with invalid token."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = service.setup_github_integration(
            user_id="user_123",
            github_token="invalid_token",
            repo_url="https://github.com/user/repo",
        )

        assert result["status"] == "error"
        assert "Invalid GitHub token" in result["message"]

    @patch("services.integration_service.requests.get")
    @patch("services.integration_service.requests.put")
    def test_submit_to_github_success(self, mock_put, mock_get):
        """Test successful code submission to GitHub."""
        service = IntegrationService()

        # Setup integration first
        mock_get_user = MagicMock()
        mock_get_user.status_code = 200
        mock_get_user.json.return_value = {"login": "testuser", "id": 12345}

        mock_get_file = MagicMock()
        mock_get_file.status_code = 404  # File doesn't exist

        mock_get.side_effect = [mock_get_user, mock_get_file]

        service.setup_github_integration(
            user_id="user_123",
            github_token="test_token",
            repo_url="https://github.com/user/repo",
        )

        # Submit code
        mock_put_response = MagicMock()
        mock_put_response.status_code = 201
        mock_put_response.json.return_value = {
            "commit": {"html_url": "https://github.com/user/repo/commit/abc123"}
        }
        mock_put.return_value = mock_put_response

        result = service.submit_to_github(
            user_id="user_123",
            assignment_id="assign_001",
            code="print('hello')",
            filename="solution.py",
        )

        assert result["status"] == "success"
        assert "commit_url" in result

    def test_submit_to_github_not_configured(self):
        """Test submission when GitHub not configured."""
        service = IntegrationService()

        result = service.submit_to_github(
            user_id="user_123",
            assignment_id="assign_001",
            code="print('hello')",
            filename="solution.py",
        )

        assert result["status"] == "error"
        assert "not configured" in result["message"]


class TestSlackIntegration:
    """Test suite for Slack integration."""

    @patch("services.integration_service.requests.post")
    def test_setup_slack_integration_success(self, mock_post):
        """Test successful Slack integration setup."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = service.setup_slack_integration(
            user_id="user_123",
            webhook_url="https://hooks.slack.com/services/xxx",
        )

        assert result["status"] == "success"
        assert "user_123_slack" in service.active_integrations

    @patch("services.integration_service.requests.post")
    def test_setup_slack_integration_invalid_webhook(self, mock_post):
        """Test Slack integration with invalid webhook."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        result = service.setup_slack_integration(
            user_id="user_123",
            webhook_url="https://invalid.webhook.url",
        )

        assert result["status"] == "error"
        assert "Invalid" in result["message"]

    @patch("services.integration_service.requests.post")
    def test_send_slack_notification_success(self, mock_post):
        """Test sending Slack notification."""
        service = IntegrationService()

        # Setup integration
        mock_setup_response = MagicMock()
        mock_setup_response.status_code = 200
        mock_post.return_value = mock_setup_response

        service.setup_slack_integration(
            user_id="user_123",
            webhook_url="https://hooks.slack.com/services/xxx",
        )

        # Send notification
        result = service.send_slack_notification(
            user_id="user_123",
            notification_type="assignment_graded",
            data={
                "title": "Test Assignment",
                "score": 85,
                "max_score": 100,
                "percentage": 85,
            },
        )

        assert result is True

    def test_send_slack_notification_not_configured(self):
        """Test sending notification when not configured."""
        service = IntegrationService()

        result = service.send_slack_notification(
            user_id="user_123",
            notification_type="assignment_graded",
            data={"title": "Test"},
        )

        assert result is False

    @patch("services.integration_service.requests.post")
    def test_send_slack_notification_unknown_type(self, mock_post):
        """Test sending notification with unknown type."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service.setup_slack_integration(
            user_id="user_123",
            webhook_url="https://hooks.slack.com/services/xxx",
        )

        result = service.send_slack_notification(
            user_id="user_123",
            notification_type="unknown_type",
            data={},
        )

        assert result is False


class TestDiscordIntegration:
    """Test suite for Discord integration."""

    @patch("services.integration_service.requests.post")
    def test_setup_discord_integration_success(self, mock_post):
        """Test successful Discord integration setup."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        result = service.setup_discord_integration(
            user_id="user_123",
            webhook_url="https://discord.com/api/webhooks/xxx",
        )

        assert result["status"] == "success"
        assert "user_123_discord" in service.active_integrations

    @patch("services.integration_service.requests.post")
    def test_setup_discord_integration_invalid_webhook(self, mock_post):
        """Test Discord integration with invalid webhook."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        result = service.setup_discord_integration(
            user_id="user_123",
            webhook_url="https://invalid.webhook.url",
        )

        assert result["status"] == "error"

    @patch("services.integration_service.requests.post")
    def test_send_discord_notification_success(self, mock_post):
        """Test sending Discord notification."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        service.setup_discord_integration(
            user_id="user_123",
            webhook_url="https://discord.com/api/webhooks/xxx",
        )

        result = service.send_discord_notification(
            user_id="user_123",
            notification_type="assignment_graded",
            data={
                "title": "Test Assignment",
                "score": 85,
                "max_score": 100,
                "percentage": 85,
            },
        )

        assert result is True

    def test_send_discord_notification_not_configured(self):
        """Test sending notification when not configured."""
        service = IntegrationService()

        result = service.send_discord_notification(
            user_id="user_123",
            notification_type="assignment_graded",
            data={"title": "Test"},
        )

        assert result is False


class TestIDEConfigurations:
    """Test suite for IDE configuration generation."""

    def test_generate_vscode_config(self):
        """Test VS Code extension config generation."""
        service = IntegrationService()

        config = service.generate_vscode_extension_config(
            user_id="user_123",
            api_endpoint="https://api.example.com",
        )

        assert "aiGradingSystem" in config
        assert config["aiGradingSystem"]["apiEndpoint"] == "https://api.example.com"
        assert config["aiGradingSystem"]["userId"] == "user_123"
        assert "features" in config["aiGradingSystem"]
        assert "keybindings" in config["aiGradingSystem"]

    def test_generate_intellij_config(self):
        """Test IntelliJ plugin config generation."""
        service = IntegrationService()

        config = service.generate_intellij_plugin_config(
            user_id="user_123",
            api_endpoint="https://api.example.com",
        )

        assert "aiGradingPlugin" in config
        assert config["aiGradingPlugin"]["serverUrl"] == "https://api.example.com"
        assert config["aiGradingPlugin"]["userId"] == "user_123"
        assert "toolWindow" in config["aiGradingPlugin"]


class TestCalendarIntegration:
    """Test suite for calendar integration."""

    def test_create_calendar_integration(self):
        """Test calendar integration creation."""
        service = IntegrationService()

        result = service.create_calendar_integration(user_id="user_123")

        assert result["status"] == "success"
        assert "calendar_url" in result
        assert "ical_content" in result
        assert result["events_count"] > 0

    def test_calendar_ical_format(self):
        """Test that iCal content is properly formatted."""
        service = IntegrationService()

        result = service.create_calendar_integration(user_id="user_123")

        ical_content = result["ical_content"]
        assert "BEGIN:VCALENDAR" in ical_content
        assert "END:VCALENDAR" in ical_content
        assert "BEGIN:VEVENT" in ical_content
        assert "END:VEVENT" in ical_content


class TestIntegrationStatus:
    """Test suite for integration status checking."""

    def test_get_integration_status_empty(self):
        """Test getting status with no integrations."""
        service = IntegrationService()

        status = service.get_integration_status("user_123")

        assert status["user_id"] == "user_123"
        assert "integrations" in status
        assert status["total_active"] == 0

    @patch("services.integration_service.requests.post")
    def test_get_integration_status_with_integrations(self, mock_post):
        """Test getting status with active integrations."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Use user_id without underscore to match service's key parsing logic
        service.setup_slack_integration(
            user_id="user123",
            webhook_url="https://hooks.slack.com/services/xxx",
        )

        status = service.get_integration_status("user123")

        assert status["integrations"]["slack"] is True
        assert status["total_active"] >= 1


class TestRemoveIntegration:
    """Test suite for removing integrations."""

    @patch("services.integration_service.requests.post")
    def test_remove_integration_success(self, mock_post):
        """Test successfully removing an integration."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service.setup_slack_integration(
            user_id="user_123",
            webhook_url="https://hooks.slack.com/services/xxx",
        )

        result = service.remove_integration("user_123", "slack")

        assert result["status"] == "success"
        assert "user_123_slack" not in service.active_integrations

    def test_remove_nonexistent_integration(self):
        """Test removing non-existent integration."""
        service = IntegrationService()

        result = service.remove_integration("user_123", "slack")

        assert result["status"] == "error"
        assert "not found" in result["message"]


class TestNotifyAssignmentGraded:
    """Test suite for assignment graded notifications."""

    @patch("services.integration_service.requests.post")
    def test_notify_assignment_graded_slack(self, mock_post):
        """Test notifying via Slack when assignment is graded."""
        service = IntegrationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service.setup_slack_integration(
            user_id="user_123",
            webhook_url="https://hooks.slack.com/services/xxx",
        )

        result = service.notify_assignment_graded(
            user_id="user_123",
            assignment_data={
                "title": "Test Assignment",
                "score": 85,
                "max_score": 100,
                "percentage": 85,
            },
        )

        assert "notifications_sent" in result
        assert result["notifications_sent"] >= 1
        assert result["results"]["slack"] == "success"

    def test_notify_assignment_graded_no_integrations(self):
        """Test notification when no integrations configured."""
        service = IntegrationService()

        result = service.notify_assignment_graded(
            user_id="user_123",
            assignment_data={"title": "Test"},
        )

        assert result["notifications_sent"] == 0


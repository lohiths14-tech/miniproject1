"""
Unit Tests for Email Service (Task 11)
Tests email generation and sending functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from threading import Thread


@pytest.mark.unit
class TestEmailGeneration:
    """Test suite for Email Generation (11.1)"""

    def test_welcome_email_generation_student(self):
        """Test welcome email generation for student role"""
        from services.email_service import send_welcome_email

        # Mock the send_email function to capture the template
        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            result = send_welcome_email('student@example.com', 'John Doe', 'student')

            # Verify send_email was called
            assert mock_send.called
            call_args = mock_send.call_args

            # Check subject
            subject = call_args[0][0]
            assert 'Welcome' in subject
            assert 'AI Grading System' in subject

            # Check recipient
            recipients = call_args[0][1]
            assert recipients == 'student@example.com'

            # Check template content
            template = call_args[0][2]
            assert 'John Doe' in template
            assert 'student' in template.lower()
            assert 'Browse assignments' in template
            assert '<html>' in template
            assert '</html>' in template

    def test_welcome_email_generation_lecturer(self):
        """Test welcome email generation for lecturer role"""
        from services.email_service import send_welcome_email

        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            result = send_welcome_email('lecturer@example.com', 'Dr. Smith', 'lecturer')

            assert mock_send.called
            call_args = mock_send.call_args
            template = call_args[0][2]

            # Lecturer-specific content
            assert 'Dr. Smith' in template
            assert 'Create and manage assignments' in template
            assert 'Monitor student submissions' in template

    def test_assignment_notification_email(self):
        """Test assignment notification email generation"""
        from services.email_service import send_assignment_notification

        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            deadline = datetime(2025, 12, 31, 23, 59)
            result = send_assignment_notification(
                'student@example.com',
                'Jane Doe',
                'Python Basics Assignment',
                deadline
            )

            assert mock_send.called
            call_args = mock_send.call_args

            # Check subject
            subject = call_args[0][0]
            assert 'New Assignment' in subject
            assert 'Python Basics Assignment' in subject

            # Check template content
            template = call_args[0][2]
            assert 'Jane Doe' in template
            assert 'Python Basics Assignment' in template
            assert 'December 31, 2025' in template
            assert '<html>' in template

    def test_submission_confirmation_email_with_score(self):
        """Test submission confirmation email with score"""
        from services.email_service import send_submission_confirmation

        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            result = send_submission_confirmation(
                'student@example.com',
                'Alice Johnson',
                'Data Structures Lab',
                score=95
            )

            assert mock_send.called
            call_args = mock_send.call_args

            # Check subject
            subject = call_args[0][0]
            assert 'Submission Received' in subject
            assert 'Data Structures Lab' in subject

            # Check template content
            template = call_args[0][2]
            assert 'Alice Johnson' in template
            assert 'Data Structures Lab' in template
            assert '95%' in template
            assert 'Your Score' in template

    def test_submission_confirmation_email_without_score(self):
        """Test submission confirmation email without score"""
        from services.email_service import send_submission_confirmation

        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            result = send_submission_confirmation(
                'student@example.com',
                'Bob Smith',
                'Algorithm Assignment',
                score=None
            )

            assert mock_send.called
            call_args = mock_send.call_args
            template = call_args[0][2]

            # Should not contain score section
            assert 'Bob Smith' in template
            assert 'Algorithm Assignment' in template
            # Score section should not be present
            assert 'Your Score' not in template or template.count('Your Score') == 0

    def test_password_reset_email(self):
        """Test password reset email generation"""
        from services.email_service import send_password_reset_email

        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            result = send_password_reset_email(
                'user@example.com',
                'Charlie Brown',
                'reset_token_abc123xyz'
            )

            assert mock_send.called
            call_args = mock_send.call_args

            # Check subject
            subject = call_args[0][0]
            assert 'Password Reset' in subject

            # Check template content
            template = call_args[0][2]
            assert 'Charlie Brown' in template
            assert 'reset_token_abc123xyz' in template
            assert 'http://localhost:5000/reset-password?token=reset_token_abc123xyz' in template
            assert '24 hours' in template

    def test_html_email_formatting(self):
        """Test HTML email formatting is valid"""
        from services.email_service import send_welcome_email

        with patch('services.email_service.send_email') as mock_send:
            mock_send.return_value = True

            send_welcome_email('test@example.com', 'Test User', 'student')

            call_args = mock_send.call_args
            template = call_args[0][2]

            # Verify HTML structure
            assert '<html>' in template
            assert '</html>' in template
            assert '<body' in template
            assert '</body>' in template
            assert '<h2' in template
            assert '<p>' in template

            # Verify styling
            assert 'font-family' in template
            assert 'color' in template


@pytest.mark.unit
class TestEmailSending:
    """Test suite for Email Sending (11.2)"""

    @patch('services.email_service.Thread')
    def test_async_email_sending(self, mock_thread, app):
        """Test async email sending with threading"""
        from services.email_service import send_email

        with app.app_context():
            # Setup mocks
            app.config['MAIL_USERNAME'] = 'noreply@example.com'
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            result = send_email(
                'Test Subject',
                'recipient@example.com',
                '<html><body>Test</body></html>'
            )

            # Verify thread was created and started
            assert mock_thread.called
            assert mock_thread_instance.start.called
            assert result is True

    @patch('services.email_service.Thread')
    def test_email_with_single_recipient(self, mock_thread, app):
        """Test email sending with single recipient string"""
        from services.email_service import send_email

        with app.app_context():
            app.config['MAIL_USERNAME'] = 'noreply@example.com'
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            result = send_email(
                'Test Subject',
                'single@example.com',  # Single string
                '<html><body>Test</body></html>'
            )

            assert result is True

    @patch('services.email_service.Thread')
    def test_email_with_multiple_recipients(self, mock_thread, app):
        """Test email sending with multiple recipients"""
        from services.email_service import send_email

        with app.app_context():
            app.config['MAIL_USERNAME'] = 'noreply@example.com'
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            result = send_email(
                'Test Subject',
                ['user1@example.com', 'user2@example.com'],  # List
                '<html><body>Test</body></html>'
            )

            assert result is True

    def test_smtp_error_handling_value_error(self, app):
        """Test SMTP error handling for ValueError"""
        from services.email_service import send_email

        with app.app_context():
            # Simulate ValueError by missing MAIL_USERNAME
            if 'MAIL_USERNAME' in app.config:
                del app.config['MAIL_USERNAME']

            result = send_email(
                'Test Subject',
                'test@example.com',
                '<html><body>Test</body></html>'
            )

            # Should return False on error
            assert result is False

    def test_smtp_error_handling_key_error(self, app):
        """Test SMTP error handling for KeyError"""
        from services.email_service import send_email

        with app.app_context():
            # Ensure MAIL_USERNAME is not in config
            app.config.pop('MAIL_USERNAME', None)

            result = send_email(
                'Test Subject',
                'test@example.com',
                '<html><body>Test</body></html>'
            )

            # Should return False on error
            assert result is False

    @patch('services.email_service.Message')
    def test_smtp_error_handling_attribute_error(self, mock_message, app):
        """Test SMTP error handling for AttributeError"""
        from services.email_service import send_email

        with app.app_context():
            app.config['MAIL_USERNAME'] = 'noreply@example.com'

            # Make Message constructor raise AttributeError
            mock_message.side_effect = AttributeError('Mock attribute error')

            result = send_email(
                'Test Subject',
                'test@example.com',
                '<html><body>Test</body></html>'
            )

            # Should return False on error
            assert result is False

    @patch('services.email_service.Thread')
    def test_email_queue_management(self, mock_thread, app):
        """Test email queue management through threading"""
        from services.email_service import send_email

        with app.app_context():
            app.config['MAIL_USERNAME'] = 'noreply@example.com'
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            # Send multiple emails
            result1 = send_email('Subject 1', 'user1@example.com', '<html>Body 1</html>')
            result2 = send_email('Subject 2', 'user2@example.com', '<html>Body 2</html>')
            result3 = send_email('Subject 3', 'user3@example.com', '<html>Body 3</html>')

            # All should succeed
            assert result1 is True
            assert result2 is True
            assert result3 is True

            # Verify threads were created for each
            assert mock_thread.call_count == 3

    def test_send_async_email_function(self, app):
        """Test the send_async_email helper function"""
        from services.email_service import send_async_email
        from flask_mail import Message

        with app.app_context():
            # Setup mock mail
            with patch.object(app, 'mail') as mock_mail:
                # Create a message
                msg = Message(
                    subject='Test',
                    recipients=['test@example.com'],
                    sender='noreply@example.com'
                )
                msg.html = '<html><body>Test</body></html>'

                # Call send_async_email
                send_async_email(app, msg)

                # Verify mail.send was called
                assert mock_mail.send.called


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=services.email_service", "--cov-report=term-missing"])


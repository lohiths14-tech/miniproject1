"""Tests for Video Code Review Service.

Tests video session management and recording functionality.
Requirements: 2.1, 2.2
"""
import pytest
import time
from services.video_code_review_service import (
    VideoCodeReviewService,
    ReviewType,
    ReviewStatus,
)


class TestVideoCodeReviewServiceInit:
    """Test suite for VideoCodeReviewService initialization."""

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = VideoCodeReviewService()

        assert service is not None
        assert isinstance(service.active_recordings, dict)
        assert isinstance(service.review_templates, dict)

    def test_review_templates_loaded(self):
        """Test that review templates are loaded."""
        service = VideoCodeReviewService()

        assert "algorithm_analysis" in service.review_templates
        assert "bug_analysis" in service.review_templates
        assert "code_quality_review" in service.review_templates

    def test_algorithm_template_structure(self):
        """Test algorithm analysis template structure."""
        service = VideoCodeReviewService()

        template = service.review_templates["algorithm_analysis"]
        assert "intro" in template
        assert "complexity_section" in template
        assert "optimization_section" in template
        assert "conclusion" in template

    def test_bug_analysis_template_structure(self):
        """Test bug analysis template structure."""
        service = VideoCodeReviewService()

        template = service.review_templates["bug_analysis"]
        assert "intro" in template
        assert "problem_identification" in template
        assert "solution_walkthrough" in template
        assert "verification" in template


class TestRecordingSession:
    """Test suite for recording session management."""

    def test_start_recording_session(self):
        """Test starting a recording session."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
            language="python",
        )

        assert session_id is not None
        assert session_id in service.active_recordings

    def test_start_recording_session_default_language(self):
        """Test starting session with default language."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        recording = service.active_recordings[session_id]
        assert recording["session"].language == "python"

    def test_recording_session_status(self):
        """Test that new recording has correct status."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        recording = service.active_recordings[session_id]
        assert recording["session"].status == ReviewStatus.RECORDING

    def test_recording_session_type(self):
        """Test that new recording has correct type."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        recording = service.active_recordings[session_id]
        assert recording["session"].review_type == ReviewType.SESSION_RECORDING


class TestStopRecording:
    """Test suite for stopping recording sessions."""

    def test_stop_recording_session(self):
        """Test stopping a recording session."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        result = service.stop_recording_session(session_id)

        assert "session_id" in result
        assert result["session_id"] == session_id
        assert "duration" in result
        assert "video_url" in result
        assert result["status"] == "completed"

    def test_stop_nonexistent_session(self):
        """Test stopping a non-existent session."""
        service = VideoCodeReviewService()

        result = service.stop_recording_session("nonexistent")

        assert "error" in result

    def test_stop_removes_from_active(self):
        """Test that stopping removes session from active recordings."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        service.stop_recording_session(session_id)

        assert session_id not in service.active_recordings


class TestRecordSessionEvent:
    """Test suite for recording session events."""

    def test_record_event_success(self):
        """Test recording an event during session."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        result = service.record_session_event(
            session_id=session_id,
            event_type="code_change",
            data={"description": "Added new function"},
        )

        assert result is True
        assert len(service.active_recordings[session_id]["events"]) > 0

    def test_record_event_nonexistent_session(self):
        """Test recording event for non-existent session."""
        service = VideoCodeReviewService()

        result = service.record_session_event(
            session_id="nonexistent",
            event_type="code_change",
            data={},
        )

        assert result is False

    def test_record_code_change_event(self):
        """Test that code change events are tracked separately."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        service.record_session_event(
            session_id=session_id,
            event_type="code_change",
            data={"description": "Modified code"},
        )

        recording = service.active_recordings[session_id]
        assert len(recording["code_changes"]) > 0


class TestPeerReview:
    """Test suite for peer review functionality."""

    def test_create_peer_review_session(self):
        """Test creating a peer review session."""
        service = VideoCodeReviewService()

        session_id = service.create_peer_review_session(
            reviewer_id="reviewer_123",
            code="def add(a, b): return a + b",
            author_id="author_456",
            title="Review my code",
        )

        assert session_id is not None

    def test_add_peer_comment(self):
        """Test adding a comment to peer review."""
        service = VideoCodeReviewService()

        session_id = service.create_peer_review_session(
            reviewer_id="reviewer_123",
            code="def add(a, b): return a + b",
            author_id="author_456",
            title="Review my code",
        )

        result = service.add_peer_comment(
            session_id=session_id,
            commenter_id="reviewer_123",
            comment="Consider adding type hints",
            line_number=1,
        )

        assert result is True

    def test_add_peer_comment_without_line(self):
        """Test adding a general comment without line number."""
        service = VideoCodeReviewService()

        session_id = service.create_peer_review_session(
            reviewer_id="reviewer_123",
            code="def add(a, b): return a + b",
            author_id="author_456",
            title="Review my code",
        )

        result = service.add_peer_comment(
            session_id=session_id,
            commenter_id="reviewer_123",
            comment="Overall good structure",
        )

        assert result is True


class TestGetReviewSession:
    """Test suite for getting review session details."""

    def test_get_review_session(self):
        """Test getting review session details."""
        service = VideoCodeReviewService()

        # The service returns sample data for any session_id
        result = service.get_review_session("any_session_id")

        assert result is not None
        assert "session_id" in result
        assert "title" in result
        assert "duration" in result
        assert "video_url" in result
        assert "status" in result
        assert "insights" in result

    def test_get_review_session_insights(self):
        """Test that review session includes insights."""
        service = VideoCodeReviewService()

        result = service.get_review_session("any_session_id")

        insights = result["insights"]
        assert "complexity" in insights
        assert "quality" in insights


class TestUserReviewHistory:
    """Test suite for user review history."""

    def test_get_user_review_history(self):
        """Test getting user's review history."""
        service = VideoCodeReviewService()

        history = service.get_user_review_history("user_123")

        assert isinstance(history, list)
        assert len(history) > 0

    def test_review_history_structure(self):
        """Test review history entry structure."""
        service = VideoCodeReviewService()

        history = service.get_user_review_history("user_123")

        entry = history[0]
        assert "session_id" in entry
        assert "title" in entry
        assert "date" in entry
        assert "duration" in entry
        assert "type" in entry
        assert "status" in entry


class TestTranscriptGeneration:
    """Test suite for transcript generation."""

    def test_generate_session_transcript(self):
        """Test generating transcript from session events."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        # Record some events
        service.record_session_event(
            session_id=session_id,
            event_type="code_change",
            data={"description": "Added function"},
        )

        service.record_session_event(
            session_id=session_id,
            event_type="comment",
            data={"text": "This is a comment"},
        )

        # Stop and get transcript
        result = service.stop_recording_session(session_id)

        # The transcript should be generated
        assert result["status"] == "completed"

    def test_empty_transcript(self):
        """Test transcript generation with no events."""
        service = VideoCodeReviewService()

        session_id = service.start_recording_session(
            user_id="user_123",
            title="Test Recording",
            code="print('hello')",
        )

        result = service.stop_recording_session(session_id)

        # Should still complete successfully
        assert result["status"] == "completed"


class TestComplexityExplanation:
    """Test suite for complexity explanation."""

    def test_explain_constant_complexity(self):
        """Test explanation for O(1) complexity."""
        service = VideoCodeReviewService()

        explanation = service._explain_complexity("O(1)")

        assert "constant" in explanation.lower()

    def test_explain_linear_complexity(self):
        """Test explanation for O(n) complexity."""
        service = VideoCodeReviewService()

        explanation = service._explain_complexity("O(n)")

        assert "linear" in explanation.lower()

    def test_explain_quadratic_complexity(self):
        """Test explanation for O(n²) complexity."""
        service = VideoCodeReviewService()

        explanation = service._explain_complexity("O(n²)")

        assert "quadratic" in explanation.lower()

    def test_explain_unknown_complexity(self):
        """Test explanation for unknown complexity."""
        service = VideoCodeReviewService()

        explanation = service._explain_complexity("O(unknown)")

        assert explanation is not None
        assert len(explanation) > 0


class TestWalkthroughDuration:
    """Test suite for walkthrough duration estimation."""

    def test_estimate_walkthrough_duration(self):
        """Test estimating walkthrough duration."""
        service = VideoCodeReviewService()

        script = {"total_duration": 180}
        duration = service._estimate_walkthrough_duration(script)

        assert duration == 180

    def test_estimate_walkthrough_duration_default(self):
        """Test default duration when not specified."""
        service = VideoCodeReviewService()

        script = {}
        duration = service._estimate_walkthrough_duration(script)

        assert duration == 120  # Default 2 minutes


class TestCompileTranscript:
    """Test suite for transcript compilation."""

    def test_compile_transcript(self):
        """Test compiling sections into transcript."""
        service = VideoCodeReviewService()

        sections = [
            {"section": "intro", "content": "Introduction text", "duration": 10},
            {"section": "analysis", "content": "Analysis text", "duration": 20},
        ]

        transcript = service._compile_transcript(sections)

        assert "Introduction text" in transcript
        assert "Analysis text" in transcript

    def test_compile_empty_transcript(self):
        """Test compiling empty sections."""
        service = VideoCodeReviewService()

        sections = []
        transcript = service._compile_transcript(sections)

        assert transcript == ""

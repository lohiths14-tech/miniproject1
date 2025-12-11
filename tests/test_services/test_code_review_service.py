"""Tests for Code Review Service.

Tests review generation, feedback formatting, and collaboration features.
Requirements: 2.1, 2.2
"""
import pytest
from services.code_review_service import CodeReviewService


class TestCodeReviewServiceInit:
    """Test suite for CodeReviewService initialization."""

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = CodeReviewService()

        assert service is not None
        assert isinstance(service.reviews, list)
        assert isinstance(service.review_requests, list)
        assert isinstance(service.comments, list)
        assert isinstance(service.review_templates, list)

    def test_review_templates_loaded(self):
        """Test that review templates are loaded."""
        service = CodeReviewService()

        assert len(service.review_templates) > 0

        # Check template structure
        template = service.review_templates[0]
        assert "id" in template
        assert "name" in template
        assert "criteria" in template
        assert "checklist" in template


class TestReviewDashboard:
    """Test suite for review dashboard functionality."""

    def test_get_review_dashboard_empty(self):
        """Test dashboard with no reviews."""
        service = CodeReviewService()
        user_id = "test_user_123"

        dashboard = service.get_review_dashboard(user_id)

        assert "summary" in dashboard
        assert "recent_activity" in dashboard
        assert "pending_actions" in dashboard
        assert "review_stats" in dashboard

    def test_dashboard_summary_structure(self):
        """Test dashboard summary has correct structure."""
        service = CodeReviewService()
        user_id = "test_user_123"

        dashboard = service.get_review_dashboard(user_id)
        summary = dashboard["summary"]

        assert "total_reviews" in summary
        assert "completed_reviews" in summary
        assert "pending_reviews" in summary
        assert "reviews_given" in summary
        assert "reviews_received" in summary


class TestReviewRequestCreation:
    """Test suite for review request creation."""

    def test_create_review_request_basic(self):
        """Test basic review request creation."""
        service = CodeReviewService()

        request_data = {
            "assignment_id": "assign_001",
            "author_id": "user_123",
            "author_name": "Test User",
            "title": "Review my sorting algorithm",
            "description": "Please review my bubble sort implementation",
            "language": "python",
        }

        result = service.create_review_request(request_data)

        assert result["success"] is True
        assert "request_id" in result
        assert result["request_id"].startswith("req_")

    def test_create_review_request_with_priority(self):
        """Test review request with priority setting."""
        service = CodeReviewService()

        request_data = {
            "assignment_id": "assign_002",
            "author_id": "user_456",
            "author_name": "Another User",
            "title": "Urgent review needed",
            "description": "Need quick feedback",
            "language": "java",
            "priority": "urgent",
        }

        result = service.create_review_request(request_data)

        assert result["success"] is True

        # Verify the request was added
        assert len(service.review_requests) > 0

    def test_create_review_request_with_tags(self):
        """Test review request with tags."""
        service = CodeReviewService()

        request_data = {
            "assignment_id": "assign_003",
            "author_id": "user_789",
            "author_name": "Tagged User",
            "title": "Algorithm review",
            "description": "Review my algorithm",
            "language": "python",
            "tags": ["algorithms", "optimization"],
        }

        result = service.create_review_request(request_data)

        assert result["success"] is True


class TestAvailableReviews:
    """Test suite for getting available reviews."""

    def test_get_available_reviews_empty(self):
        """Test getting available reviews when none exist."""
        service = CodeReviewService()
        reviewer_id = "reviewer_001"

        result = service.get_available_reviews(reviewer_id)

        assert "available_requests" in result
        assert "total_count" in result
        assert "filters" in result

    def test_get_available_reviews_excludes_own(self):
        """Test that reviewer's own requests are excluded."""
        service = CodeReviewService()
        author_id = "user_123"

        # Create a request
        service.create_review_request({
            "assignment_id": "assign_001",
            "author_id": author_id,
            "author_name": "Test User",
            "title": "My review",
            "description": "Review this",
            "language": "python",
        })

        # Get available reviews for the same user
        result = service.get_available_reviews(author_id)

        # Should not include own request
        own_requests = [r for r in result["available_requests"] if r["author_id"] == author_id]
        assert len(own_requests) == 0


class TestAcceptReviewRequest:
    """Test suite for accepting review requests."""

    def test_accept_review_request_success(self):
        """Test successfully accepting a review request."""
        service = CodeReviewService()

        # Create a request first
        create_result = service.create_review_request({
            "assignment_id": "assign_001",
            "author_id": "author_123",
            "author_name": "Author",
            "title": "Review needed",
            "description": "Please review",
            "language": "python",
        })

        request_id = create_result["request_id"]
        reviewer_id = "reviewer_456"

        result = service.accept_review_request(request_id, reviewer_id)

        assert result["success"] is True

    def test_accept_nonexistent_request(self):
        """Test accepting a non-existent request."""
        service = CodeReviewService()

        result = service.accept_review_request("nonexistent_id", "reviewer_123")

        assert "error" in result

    def test_accept_already_assigned_request(self):
        """Test accepting an already assigned request."""
        service = CodeReviewService()

        # Create and accept a request
        create_result = service.create_review_request({
            "assignment_id": "assign_001",
            "author_id": "author_123",
            "author_name": "Author",
            "title": "Review needed",
            "description": "Please review",
            "language": "python",
        })

        request_id = create_result["request_id"]
        service.accept_review_request(request_id, "reviewer_1")

        # Try to accept again
        result = service.accept_review_request(request_id, "reviewer_2")

        assert "error" in result


class TestSubmitReview:
    """Test suite for submitting reviews."""

    def test_submit_review_basic(self):
        """Test basic review submission."""
        service = CodeReviewService()

        review_data = {
            "title": "Code Review for Assignment 1",
            "assignment_id": "assign_001",
            "author_id": "author_123",
            "author_name": "Author Name",
            "reviewer_id": "reviewer_456",
            "reviewer_name": "Reviewer Name",
            "code_snapshot": "def add(a, b): return a + b",
            "review_data": {
                "overall_rating": 4,
                "criteria_scores": {"correctness": 5, "style": 4},
            },
            "feedback": "Good implementation!",
        }

        result = service.submit_review(review_data)

        assert result["success"] is True
        assert "review_id" in result
        assert result["review_id"].startswith("rev_")

    def test_submit_review_with_comments(self):
        """Test review submission with comments."""
        service = CodeReviewService()

        review_data = {
            "title": "Detailed Review",
            "assignment_id": "assign_002",
            "author_id": "author_789",
            "author_name": "Author",
            "reviewer_id": "reviewer_012",
            "reviewer_name": "Reviewer",
            "code_snapshot": "print('hello')",
            "review_data": {"overall_rating": 3},
            "feedback": "Needs improvement",
            "comments": [
                {"line": 1, "content": "Consider using f-strings"},
            ],
            "review_time": 45,
            "lines_reviewed": 10,
        }

        result = service.submit_review(review_data)

        assert result["success"] is True


class TestReviewDetails:
    """Test suite for getting review details."""

    def test_get_review_details_not_found(self):
        """Test getting details for non-existent review."""
        service = CodeReviewService()

        result = service.get_review_details("nonexistent_review")

        assert "error" in result

    def test_get_review_details_success(self):
        """Test getting details for existing review."""
        service = CodeReviewService()

        # Submit a review first
        submit_result = service.submit_review({
            "title": "Test Review",
            "assignment_id": "assign_001",
            "author_id": "author_123",
            "author_name": "Author",
            "reviewer_id": "reviewer_456",
            "reviewer_name": "Reviewer",
            "code_snapshot": "code here",
            "review_data": {"overall_rating": 5},
            "feedback": "Excellent!",
        })

        review_id = submit_result["review_id"]

        result = service.get_review_details(review_id)

        assert "error" not in result
        assert result["id"] == review_id
        assert "comments" in result
        assert "comment_stats" in result


class TestComments:
    """Test suite for comment functionality."""

    def test_add_comment_basic(self):
        """Test adding a basic comment."""
        service = CodeReviewService()

        # Submit a review first
        submit_result = service.submit_review({
            "title": "Test Review",
            "assignment_id": "assign_001",
            "author_id": "author_123",
            "author_name": "Author",
            "reviewer_id": "reviewer_456",
            "reviewer_name": "Reviewer",
            "code_snapshot": "code",
            "review_data": {"overall_rating": 4},
            "feedback": "Good",
        })

        review_id = submit_result["review_id"]

        comment_data = {
            "review_id": review_id,
            "author_id": "reviewer_456",
            "author_name": "Reviewer",
            "line_number": 5,
            "content": "Consider refactoring this function",
            "comment_type": "suggestion",
        }

        result = service.add_comment(comment_data)

        assert result["success"] is True
        assert "comment_id" in result

    def test_resolve_comment(self):
        """Test resolving a comment."""
        service = CodeReviewService()

        # Submit a review and add a comment
        submit_result = service.submit_review({
            "title": "Test Review",
            "assignment_id": "assign_001",
            "author_id": "author_123",
            "author_name": "Author",
            "reviewer_id": "reviewer_456",
            "reviewer_name": "Reviewer",
            "code_snapshot": "code",
            "review_data": {"overall_rating": 4},
            "feedback": "Good",
        })

        comment_result = service.add_comment({
            "review_id": submit_result["review_id"],
            "author_id": "reviewer_456",
            "author_name": "Reviewer",
            "line_number": 1,
            "content": "Fix this",
            "comment_type": "issue",
        })

        comment_id = comment_result["comment_id"]

        result = service.resolve_comment(comment_id, "author_123")

        assert result["success"] is True

    def test_resolve_nonexistent_comment(self):
        """Test resolving a non-existent comment."""
        service = CodeReviewService()

        result = service.resolve_comment("nonexistent_comment", "user_123")

        assert "error" in result


class TestReviewAnalytics:
    """Test suite for review analytics."""

    def test_get_analytics_empty(self):
        """Test analytics with no reviews."""
        service = CodeReviewService()

        result = service.get_review_analytics()

        assert "message" in result or "overview" in result

    def test_get_analytics_with_reviews(self):
        """Test analytics with existing reviews."""
        service = CodeReviewService()

        # Submit some reviews
        for i in range(3):
            service.submit_review({
                "title": f"Review {i}",
                "assignment_id": f"assign_{i}",
                "author_id": "author_123",
                "author_name": "Author",
                "reviewer_id": "reviewer_456",
                "reviewer_name": "Reviewer",
                "code_snapshot": "code",
                "review_data": {"overall_rating": 4},
                "feedback": "Good",
            })

        result = service.get_review_analytics()

        if "overview" in result:
            assert "total_reviews" in result["overview"]
            assert "average_rating" in result["overview"]

    def test_get_analytics_for_user(self):
        """Test analytics for specific user."""
        service = CodeReviewService()
        user_id = "user_123"

        # Submit a review for this user
        service.submit_review({
            "title": "User Review",
            "assignment_id": "assign_001",
            "author_id": user_id,
            "author_name": "User",
            "reviewer_id": "reviewer_456",
            "reviewer_name": "Reviewer",
            "code_snapshot": "code",
            "review_data": {"overall_rating": 5},
            "feedback": "Excellent",
        })

        result = service.get_review_analytics(user_id)

        # Should return analytics or message
        assert result is not None


class TestReviewTemplates:
    """Test suite for review templates."""

    def test_algorithm_template_exists(self):
        """Test that algorithm review template exists."""
        service = CodeReviewService()

        algorithm_templates = [
            t for t in service.review_templates
            if "algorithm" in t["name"].lower()
        ]

        assert len(algorithm_templates) > 0

    def test_template_has_criteria(self):
        """Test that templates have criteria defined."""
        service = CodeReviewService()

        for template in service.review_templates:
            assert "criteria" in template
            assert len(template["criteria"]) > 0

            for criterion in template["criteria"]:
                assert "name" in criterion
                assert "weight" in criterion

    def test_template_has_checklist(self):
        """Test that templates have checklists."""
        service = CodeReviewService()

        for template in service.review_templates:
            assert "checklist" in template
            assert len(template["checklist"]) > 0

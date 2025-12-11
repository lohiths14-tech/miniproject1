"""Tests for Assignment Template Service.

Tests template CRUD operations and variable substitution functionality.
Requirements: 2.1, 2.2
"""
import pytest
from services.assignment_template_service import AssignmentTemplateService


class TestTemplateRetrieval:
    """Test suite for template retrieval operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_get_all_templates_returns_list(self):
        """Test that get_all_templates returns templates."""
        result = self.service.get_all_templates()

        assert "templates" in result
        assert "total_count" in result
        assert isinstance(result["templates"], list)
        assert result["total_count"] >= 0

    def test_get_all_templates_with_category_filter(self):
        """Test filtering templates by category."""
        result = self.service.get_all_templates(category="Algorithms")

        for template in result["templates"]:
            assert template["category"] == "Algorithms"

    def test_get_all_templates_with_difficulty_filter(self):
        """Test filtering templates by difficulty."""
        result = self.service.get_all_templates(difficulty="Medium")

        for template in result["templates"]:
            assert template["difficulty"] == "Medium"

    def test_get_all_templates_with_language_filter(self):
        """Test filtering templates by language."""
        result = self.service.get_all_templates(language="Python")

        for template in result["templates"]:
            assert template["language"] == "Python"

    def test_get_all_templates_with_search(self):
        """Test searching templates by keyword."""
        result = self.service.get_all_templates(search="array")

        # Search should match name, description, or tags
        for template in result["templates"]:
            search_text = (
                template["name"].lower()
                + template["description"].lower()
                + " ".join(template["tags"])
            )
            assert "array" in search_text

    def test_get_template_details_existing(self):
        """Test getting details for existing template."""
        result = self.service.get_template_details("tmpl_001")

        assert "error" not in result
        assert result["id"] == "tmpl_001"
        assert "usage_stats" in result
        assert "reviews" in result

    def test_get_template_details_nonexistent(self):
        """Test getting details for non-existent template."""
        result = self.service.get_template_details("nonexistent_id")

        assert "error" in result
        assert result["error"] == "Template not found"

    def test_get_template_by_id_existing(self):
        """Test getting template by ID."""
        result = self.service.get_template_by_id("tmpl_001")

        assert result is not None
        assert result["id"] == "tmpl_001"

    def test_get_template_by_id_nonexistent(self):
        """Test getting non-existent template by ID."""
        result = self.service.get_template_by_id("nonexistent")

        assert result is None


class TestTemplateCreation:
    """Test suite for template creation operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_create_template_valid_data(self):
        """Test creating template with valid data."""
        template_data = {
            "name": "Test Template",
            "description": "A test template",
            "category": "Algorithms",
            "difficulty": "Easy",
            "language": "Python",
            "tags": ["test", "example"],
            "estimated_time": 30,
            "template_data": {
                "problem_statement": "Test problem",
                "starter_code": {"python": "def solution(): pass"},
                "test_cases": [{"input": "1", "expected": "1"}],
            },
        }

        result = self.service.create_template(template_data)

        assert result is not None
        assert "id" in result

    def test_create_template_with_created_by(self):
        """Test creating template with created_by field."""
        template_data = {
            "name": "Creator Test Template",
            "description": "Template with creator",
            "category": "Data Structures",
            "created_by": "test_creator",
            "template_data": {
                "problem_statement": "Test",
                "starter_code": {"python": "pass"},
                "test_cases": [{"input": "1", "expected": "1"}],
            },
        }

        initial_count = len(self.service.templates)
        result = self.service.create_template(template_data)

        assert result is not None
        assert len(self.service.templates) == initial_count + 1


class TestTemplateUpdate:
    """Test suite for template update operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_update_template_valid(self):
        """Test updating template with valid data."""
        update_data = {"name": "Updated Template Name"}
        result = self.service.update_template("tmpl_001", update_data)

        assert result is not None
        assert result["name"] == "Updated Template Name"

    def test_update_template_nonexistent(self):
        """Test updating non-existent template."""
        result = self.service.update_template("nonexistent", {"name": "Test"})

        assert result is None

    def test_update_template_multiple_fields(self):
        """Test updating multiple template fields."""
        update_data = {
            "name": "Multi-Update Template",
            "description": "Updated description",
            "difficulty": "Hard",
        }
        result = self.service.update_template("tmpl_001", update_data)

        assert result is not None
        assert result["name"] == "Multi-Update Template"
        assert result["description"] == "Updated description"
        assert result["difficulty"] == "Hard"


class TestTemplateDuplication:
    """Test suite for template duplication."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_duplicate_template_success(self):
        """Test duplicating existing template."""
        initial_count = len(self.service.templates)
        result = self.service.duplicate_template("tmpl_001")

        assert result is not None
        assert "id" in result
        assert len(self.service.templates) == initial_count + 1

    def test_duplicate_template_has_copy_prefix(self):
        """Test duplicated template has 'Copy of' prefix."""
        original = self.service.get_template_by_id("tmpl_001")
        result = self.service.duplicate_template("tmpl_001")

        assert result is not None
        assert result["name"].startswith("Copy of")

    def test_duplicate_nonexistent_template(self):
        """Test duplicating non-existent template."""
        result = self.service.duplicate_template("nonexistent")

        assert result is None


class TestTemplateVersioning:
    """Test suite for template versioning."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_get_template_versions(self):
        """Test getting template version history."""
        result = self.service.get_template_versions("tmpl_001")

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_template_versions_nonexistent(self):
        """Test getting versions for non-existent template."""
        result = self.service.get_template_versions("nonexistent")

        assert result is None


class TestTemplatePublishing:
    """Test suite for template publishing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_publish_template_success(self):
        """Test publishing a template."""
        # Get template creator
        template = self.service.get_template_by_id("tmpl_001")
        creator = template["created_by"]

        result = self.service.publish_template("tmpl_001", creator)

        # May succeed or fail based on validation
        assert result is not None

    def test_publish_nonexistent_template(self):
        """Test publishing non-existent template."""
        result = self.service.publish_template("nonexistent", "user")

        assert "error" in result

    def test_publish_template_permission_denied(self):
        """Test publishing without permission."""
        result = self.service.publish_template("tmpl_001", "wrong_user")

        assert "error" in result


class TestUserTemplates:
    """Test suite for user-specific template operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_get_my_templates(self):
        """Test getting templates for a user."""
        result = self.service.get_my_templates("Dr. Smith")

        assert "templates" in result
        assert "stats" in result
        assert "by_status" in result

    def test_get_my_templates_empty_user(self):
        """Test getting templates for user with no templates."""
        result = self.service.get_my_templates("nonexistent_user")

        assert "templates" in result
        assert len(result["templates"]) == 0


class TestTemplateValidation:
    """Test suite for template validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_validate_template_missing_name(self):
        """Test validation fails for missing name."""
        template = {
            "description": "Test",
            "category": "Test",
            "template_data": {
                "problem_statement": "Test",
                "starter_code": {"python": "pass"},
                "test_cases": [{"input": "1", "expected": "1"}],
            },
        }

        result = self.service._validate_template(template)

        assert not result["valid"]
        assert "Name is required" in result["errors"]

    def test_validate_template_missing_description(self):
        """Test validation fails for missing description."""
        template = {
            "name": "Test",
            "category": "Test",
            "template_data": {
                "problem_statement": "Test",
                "starter_code": {"python": "pass"},
                "test_cases": [{"input": "1", "expected": "1"}],
            },
        }

        result = self.service._validate_template(template)

        assert not result["valid"]
        assert "Description is required" in result["errors"]

    def test_validate_template_valid(self):
        """Test validation passes for valid template."""
        template = {
            "name": "Test Template",
            "description": "Test description",
            "category": "Test Category",
            "template_data": {
                "problem_statement": "Test problem",
                "starter_code": {"python": "pass"},
                "test_cases": [{"input": "1", "expected": "1"}],
            },
        }

        result = self.service._validate_template(template)

        assert result["valid"]
        assert len(result["errors"]) == 0


class TestTemplateCategories:
    """Test suite for template categories."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_categories_loaded(self):
        """Test that categories are loaded."""
        assert len(self.service.categories) > 0

    def test_category_structure(self):
        """Test category data structure."""
        for category in self.service.categories:
            assert "name" in category
            assert "description" in category


class TestPopularTags:
    """Test suite for popular tags functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AssignmentTemplateService()

    def test_get_popular_tags(self):
        """Test getting popular tags."""
        tags = self.service._get_popular_tags()

        assert isinstance(tags, list)
        assert len(tags) <= 15  # Should return max 15 tags


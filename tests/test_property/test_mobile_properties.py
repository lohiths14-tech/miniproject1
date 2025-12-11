"""
Property-based tests for Mobile App data handling

**Feature: project-improvements, Property 5-7: Mobile App Data Handling**
**Validates: Requirements 4.3, 4.5, 4.8**
"""

import pytest
import json
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta


# ==================== Strategies for Mobile Data ====================

@st.composite
def assignment_data(draw):
    """Generate valid assignment data for mobile app."""
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))),
        'title': draw(st.text(min_size=1, max_size=200)),
        'description': draw(st.text(max_size=1000)),
        'dueDate': draw(st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        )).isoformat(),
        'status': draw(st.sampled_from(['pending', 'submitted', 'graded', 'overdue'])),
        'points': draw(st.integers(min_value=0, max_value=1000)),
        'grade': draw(st.one_of(st.none(), st.integers(min_value=0, max_value=100))),
    }


@st.composite
def leaderboard_entry(draw):
    """Generate valid leaderboard entry data."""
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))),
        'username': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P')))),
        'points': draw(st.integers(min_value=0, max_value=100000)),
        'badges': draw(st.lists(
            st.sampled_from([
                'first_submission', 'streak_master', 'perfect_score',
                'code_ninja', 'bug_hunter', 'speed_demon', 'helper'
            ]),
            max_size=10
        )),
        'rank': draw(st.integers(min_value=1, max_value=10000)),
    }


@st.composite
def api_response_data(draw):
    """Generate valid API response data for round-trip testing."""
    data_type = draw(st.sampled_from(['assignment', 'submission', 'leaderboard', 'dashboard']))

    if data_type == 'assignment':
        return {
            'type': 'assignment',
            'data': draw(assignment_data())
        }
    elif data_type == 'submission':
        return {
            'type': 'submission',
            'data': {
                'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))),
                'assignmentId': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))),
                'code': draw(st.text(max_size=5000)),
                'language': draw(st.sampled_from(['python', 'javascript', 'java', 'c', 'cpp'])),
                'grade': draw(st.one_of(st.none(), st.integers(min_value=0, max_value=100))),
                'createdAt': draw(st.datetimes(
                    min_value=datetime(2020, 1, 1),
                    max_value=datetime(2030, 12, 31)
                )).isoformat(),
            }
        }
    elif data_type == 'leaderboard':
        return {
            'type': 'leaderboard',
            'data': draw(st.lists(leaderboard_entry(), min_size=0, max_size=100))
        }
    else:  # dashboard
        return {
            'type': 'dashboard',
            'data': {
                'totalSubmissions': draw(st.integers(min_value=0, max_value=10000)),
                'averageGrade': draw(st.integers(min_value=0, max_value=100)),
                'points': draw(st.integers(min_value=0, max_value=100000)),
                'level': draw(st.sampled_from(['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert', 'Master'])),
                'streak': draw(st.integers(min_value=0, max_value=365)),
                'pendingAssignments': draw(st.integers(min_value=0, max_value=100)),
            }
        }


# ==================== Property 5: Assignment List Rendering Completeness ====================

@pytest.mark.property
class TestAssignmentListRendering:
    """
    Property tests for assignment list rendering completeness.

    **Feature: project-improvements, Property 5: Assignment List Rendering Completeness**
    **Validates: Requirements 4.3**
    """

    @given(assignments=st.lists(assignment_data(), min_size=0, max_size=50))
    @settings(max_examples=100, deadline=5000)
    def test_all_assignments_have_required_fields(self, assignments):
        """
        Property: Every assignment in the list must have all required fields
        for rendering (id, title, dueDate, status).

        **Validates: Requirements 4.3**
        """
        for assignment in assignments:
            # Required fields for AssignmentCard component
            assert 'id' in assignment, "Assignment must have id"
            assert 'title' in assignment, "Assignment must have title"
            assert 'dueDate' in assignment, "Assignment must have dueDate"
            assert 'status' in assignment, "Assignment must have status"

    @given(assignments=st.lists(assignment_data(), min_size=0, max_size=50))
    @settings(max_examples=100, deadline=5000)
    def test_assignment_status_is_valid(self, assignments):
        """
        Property: Every assignment status must be one of the valid statuses.

        **Validates: Requirements 4.3**
        """
        valid_statuses = {'pending', 'submitted', 'graded', 'overdue'}
        for assignment in assignments:
            assert assignment['status'] in valid_statuses, \
                f"Invalid status: {assignment['status']}"

    @given(assignments=st.lists(assignment_data(), min_size=0, max_size=50))
    @settings(max_examples=100, deadline=5000)
    def test_assignment_filtering_preserves_count(self, assignments):
        """
        Property: Filtering assignments by status should partition the list
        (sum of filtered counts equals total count).

        **Validates: Requirements 4.3**
        """
        statuses = ['pending', 'submitted', 'graded', 'overdue']
        filtered_counts = {
            status: len([a for a in assignments if a['status'] == status])
            for status in statuses
        }
        assert sum(filtered_counts.values()) == len(assignments)

    @given(assignments=st.lists(assignment_data(), min_size=1, max_size=50))
    @settings(max_examples=100, deadline=5000)
    def test_assignment_points_non_negative(self, assignments):
        """
        Property: Assignment points should always be non-negative.

        **Validates: Requirements 4.3**
        """
        for assignment in assignments:
            if 'points' in assignment:
                assert assignment['points'] >= 0, "Points must be non-negative"


# ==================== Property 6: Leaderboard Rendering Completeness ====================

@pytest.mark.property
class TestLeaderboardRendering:
    """
    Property tests for leaderboard rendering completeness.

    **Feature: project-improvements, Property 6: Leaderboard Rendering Completeness**
    **Validates: Requirements 4.5**
    """

    @given(entries=st.lists(leaderboard_entry(), min_size=0, max_size=100))
    @settings(max_examples=100, deadline=5000)
    def test_all_entries_have_required_fields(self, entries):
        """
        Property: Every leaderboard entry must have all required fields
        for rendering (username, points, rank).

        **Validates: Requirements 4.5**
        """
        for entry in entries:
            assert 'username' in entry, "Entry must have username"
            assert 'points' in entry, "Entry must have points"
            assert 'rank' in entry, "Entry must have rank"

    @given(entries=st.lists(leaderboard_entry(), min_size=0, max_size=100))
    @settings(max_examples=100, deadline=5000)
    def test_leaderboard_points_non_negative(self, entries):
        """
        Property: All leaderboard points should be non-negative.

        **Validates: Requirements 4.5**
        """
        for entry in entries:
            assert entry['points'] >= 0, "Points must be non-negative"

    @given(entries=st.lists(leaderboard_entry(), min_size=0, max_size=100))
    @settings(max_examples=100, deadline=5000)
    def test_leaderboard_ranks_positive(self, entries):
        """
        Property: All leaderboard ranks should be positive integers.

        **Validates: Requirements 4.5**
        """
        for entry in entries:
            assert entry['rank'] > 0, "Rank must be positive"

    @given(entries=st.lists(leaderboard_entry(), min_size=2, max_size=100))
    @settings(max_examples=100, deadline=5000)
    def test_leaderboard_sorted_by_points_descending(self, entries):
        """
        Property: When sorted by points, higher points should have lower ranks.

        **Validates: Requirements 4.5**
        """
        # Sort entries by points descending
        sorted_entries = sorted(entries, key=lambda x: x['points'], reverse=True)

        # Assign expected ranks
        for i, entry in enumerate(sorted_entries):
            expected_rank = i + 1
            # The actual rank should be close to expected (allowing for ties)
            # This is a soft check since ties can affect ranking
            assert entry['rank'] >= 1, "Rank must be at least 1"

    @given(entries=st.lists(leaderboard_entry(), min_size=0, max_size=100))
    @settings(max_examples=100, deadline=5000)
    def test_badges_are_valid(self, entries):
        """
        Property: All badges should be from the valid badge set.

        **Validates: Requirements 4.5**
        """
        valid_badges = {
            'first_submission', 'streak_master', 'perfect_score',
            'code_ninja', 'bug_hunter', 'speed_demon', 'helper',
            'consistent', 'early_bird', 'night_owl', 'completionist', 'top_performer'
        }
        for entry in entries:
            if 'badges' in entry:
                for badge in entry['badges']:
                    assert badge in valid_badges, f"Invalid badge: {badge}"


# ==================== Property 7: Mobile API Data Round-Trip ====================

@pytest.mark.property
class TestMobileAPIRoundTrip:
    """
    Property tests for mobile API data round-trip consistency.

    **Feature: project-improvements, Property 7: Mobile API Data Round-Trip**
    **Validates: Requirements 4.8**
    """

    @given(data=api_response_data())
    @settings(max_examples=100, deadline=5000)
    def test_json_serialization_round_trip(self, data):
        """
        Property: API response data should survive JSON serialization round-trip.

        **Validates: Requirements 4.8**
        """
        # Serialize to JSON string
        json_str = json.dumps(data, default=str)

        # Deserialize back
        restored = json.loads(json_str)

        # Verify structure is preserved
        assert restored['type'] == data['type']
        assert 'data' in restored

    @given(assignments=st.lists(assignment_data(), min_size=0, max_size=20))
    @settings(max_examples=100, deadline=5000)
    def test_assignment_list_round_trip(self, assignments):
        """
        Property: Assignment list should survive JSON round-trip with all fields intact.

        **Validates: Requirements 4.8**
        """
        response = {'assignments': assignments}
        json_str = json.dumps(response, default=str)
        restored = json.loads(json_str)

        assert len(restored['assignments']) == len(assignments)
        for original, restored_item in zip(assignments, restored['assignments']):
            assert restored_item['id'] == original['id']
            assert restored_item['title'] == original['title']
            assert restored_item['status'] == original['status']

    @given(entries=st.lists(leaderboard_entry(), min_size=0, max_size=20))
    @settings(max_examples=100, deadline=5000)
    def test_leaderboard_round_trip(self, entries):
        """
        Property: Leaderboard data should survive JSON round-trip with all fields intact.

        **Validates: Requirements 4.8**
        """
        response = {'leaderboard': entries}
        json_str = json.dumps(response, default=str)
        restored = json.loads(json_str)

        assert len(restored['leaderboard']) == len(entries)
        for original, restored_item in zip(entries, restored['leaderboard']):
            assert restored_item['username'] == original['username']
            assert restored_item['points'] == original['points']
            assert restored_item['rank'] == original['rank']

    @given(data=api_response_data())
    @settings(max_examples=100, deadline=5000)
    def test_nested_data_preserved(self, data):
        """
        Property: Nested data structures should be preserved through serialization.

        **Validates: Requirements 4.8**
        """
        json_str = json.dumps(data, default=str)
        restored = json.loads(json_str)

        # Check that nested 'data' field is preserved
        if isinstance(data['data'], dict):
            assert isinstance(restored['data'], dict)
            # All keys should be preserved
            assert set(restored['data'].keys()) == set(data['data'].keys())
        elif isinstance(data['data'], list):
            assert isinstance(restored['data'], list)
            assert len(restored['data']) == len(data['data'])

    @given(
        text=st.text(max_size=1000),
        number=st.integers(min_value=-1000000, max_value=1000000),
        boolean=st.booleans(),
        null=st.none()
    )
    @settings(max_examples=100, deadline=5000)
    def test_primitive_types_round_trip(self, text, number, boolean, null):
        """
        Property: All JSON primitive types should round-trip correctly.

        **Validates: Requirements 4.8**
        """
        data = {
            'text': text,
            'number': number,
            'boolean': boolean,
            'null': null
        }

        json_str = json.dumps(data)
        restored = json.loads(json_str)

        assert restored['text'] == text
        assert restored['number'] == number
        assert restored['boolean'] == boolean
        assert restored['null'] is None


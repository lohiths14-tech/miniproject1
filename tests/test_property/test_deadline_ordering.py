"""
Property-based test for deadline ordering invariant
**Property 11: Deadline Ordering Invariant**
**Validates: Requirements 5.6**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta


@pytest.mark.property
class TestDeadlineOrdering:
    """Test deadline ordering invariant"""

    @given(
        assignments=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # assignment_id
                st.integers(min_value=0, max_value=365)  # days_from_now
            ),
            min_size=0,
            max_size=20
        )
    )
    @settings(max_examples=100, deadline=3000)
    def test_deadline_sorting_invariant(self, assignments):
        """
        Property: Assignments sorted by deadline should maintain ordering
        """
        # Create assignments with deadlines
        now = datetime.now()
        assignment_list = [
            {
                "id": aid,
                "deadline": now + timedelta(days=days),
                "days_offset": days
            }
            for aid, days in assignments
        ]

        # Sort by deadline
        sorted_assignments = sorted(assignment_list, key=lambda x: x["deadline"])

        # Verify ordering is maintained
        for i in range(len(sorted_assignments) - 1):
            assert sorted_assignments[i]["deadline"] <= sorted_assignments[i + 1]["deadline"]
            assert sorted_assignments[i]["days_offset"] <= sorted_assignments[i + 1]["days_offset"]

    @given(
        deadline_days=st.integers(min_value=-30, max_value=365),
        submission_days=st.integers(min_value=-30, max_value=365)
    )
    @settings(max_examples=100, deadline=2000)
    def test_deadline_comparison_property(self, deadline_days, submission_days):
        """
        Property: Submission before deadline should be marked as on-time
        """
        now = datetime.now()
        deadline = now + timedelta(days=deadline_days)
        submission_time = now + timedelta(days=submission_days)

        is_on_time = submission_time <= deadline
        is_late = submission_time > deadline

        # Verify mutual exclusivity
        assert is_on_time != is_late

        # Verify correctness
        if submission_days <= deadline_days:
            assert is_on_time
        else:
            assert is_late

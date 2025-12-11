"""
Property-based test for JSON serialization round-trip
**Property 7: Serialization Round-Trip Consistency**
**Validates: Requirements 5.2**
"""

import pytest
import json
from hypothesis import given, strategies as st, settings
from datetime import datetime


@pytest.mark.property
class TestSerializationRoundTrip:
    """Test JSON serialization round-trip consistency"""

    @given(
        data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
            values=st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(max_size=100),
                st.booleans(),
                st.none()
            ),
            min_size=0,
            max_size=10
        )
    )
    @settings(max_examples=100, deadline=2000)
    def test_dict_serialization_round_trip(self, data):
        """
        Property: Serializing and deserializing should preserve data
        """
        # Serialize
        serialized = json.dumps(data)

        # Deserialize
        deserialized = json.loads(serialized)

        # Verify round-trip
        assert deserialized == data
        assert type(deserialized) == type(data)

    @given(
        score=st.integers(min_value=0, max_value=100),
        feedback=st.text(max_size=200),
        test_results=st.lists(st.booleans(), min_size=0, max_size=10)
    )
    @settings(max_examples=100, deadline=2000)
    def test_grading_result_serialization(self, score, feedback, test_results):
        """
        Property: Grading results should serialize/deserialize correctly
        """
        result = {
            "score": score,
            "feedback": feedback,
            "test_results": test_results,
            "passed": all(test_results) if test_results else False
        }

        # Round-trip
        serialized = json.dumps(result)
        deserialized = json.loads(serialized)

        assert deserialized == result
        assert deserialized["score"] == score
        assert deserialized["feedback"] == feedback

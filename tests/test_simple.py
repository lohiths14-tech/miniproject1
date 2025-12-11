"""
Simple test file to verify pytest is working correctly
"""
import pytest


def test_basic_math():
    """Test that basic mathematics work"""
    assert 1 + 1 == 2
    assert 5 * 2 == 10
    assert 10 / 2 == 5


def test_string_operations():
    """Test basic string operations"""
    assert "hello" + " " + "world" == "hello world"
    assert "test".upper() == "TEST"
    assert len("pytest") == 6


def test_list_operations():
    """Test basic list operations"""
    test_list = [1, 2, 3]
    test_list.append(4)
    assert len(test_list) == 4
    assert test_list[-1] == 4


@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square(input, expected):
    """Test squaring numbers"""
    assert input * input == expected

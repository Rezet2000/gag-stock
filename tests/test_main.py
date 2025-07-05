import pytest
from unittest.mock import patch
from main import get_remaining_time

def test_get_remaining_time_is_integer():
    remaining_time = get_remaining_time()
    assert isinstance(remaining_time, int)

def test_get_remaining_time_is_positive():
    remaining_time = get_remaining_time()
    assert remaining_time >= 0

def test_remaining_time_is_less_than_or_equal_to_300():
    remaining_time = get_remaining_time()
    assert remaining_time <= 300


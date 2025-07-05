import pytest
from fixtures import stock_schema
from src.main import get_remaining_time, extract_data

# Remaining time tests

def test_get_remaining_time_is_integer():
    remaining_time = get_remaining_time()
    assert isinstance(remaining_time, int)

def test_get_remaining_time_is_positive():
    remaining_time = get_remaining_time()
    assert remaining_time >= 0

def test_remaining_time_is_less_than_or_equal_to_300_seconds():
    """
        300 seconds is 5 minutes, remaining time cant exceed this boundary because 
        gag stock cycle updates every 5 minutes on the dot
    """
    remaining_time = get_remaining_time()
    assert remaining_time <= 300

# Extract data tests

def test_discord_invite_not_in_data():
    data = extract_data(stock_schema)
    assert 'discord_invite' not in data
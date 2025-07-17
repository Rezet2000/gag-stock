import pytest
from fixtures import stock_schema
from src.main import get_remaining_time, extract_data, Config

# Test config
def test_supported_stock_keys():
    assert Config.SUPPORTED_STOCK_KEYS == ['seed_stock', 'gear_stock', 'egg_stock']

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

def test_extracted_data_contains_supported_keys():
    data = extract_data(stock_schema)
    for key in Config.SUPPORTED_STOCK_KEYS:
        assert key in data

def test_extracted_data_does_not_contain_unsupported_keys():
    data = extract_data(stock_schema)
    unsupported_keys = ['cosmetic_stock', 'eventshop_stock', 'travelingmerchant_stock', 'notification']
    for key in unsupported_keys:
        assert key not in data

def test_extracted_data_structure():
    data = extract_data(stock_schema)
    assert isinstance(data, dict)
    for key in data:
        assert isinstance(data[key], list)
        for item in data[key]:
            assert isinstance(item, dict)
            assert 'item_id' in item
            assert 'display_name' in item
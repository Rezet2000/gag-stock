import requests
import os
import time
import json
from datetime import datetime
from src.constants.item_rarity import item_rarity

MINIMUM_RARITY: int = 2 # Rare or higher

skipped_items = [
    'harvest_tool',
    'favorite_tool',
    'cleaning_spray',
]

def get_remaining_time() -> int:
    # TODO use response end time to calculate the remaining time
    """ Calculate the remaining time until the next 5-minute interval with seconds precision """
    minutes = datetime.now().minute
    delay = (((minutes // 5 + 1) * 5 - minutes) - 1) * 60 + (60 - datetime.now().second)
    return delay

def fetch_data() -> dict:
    result = requests.get('https://api.joshlei.com/v2/growagarden/stock')
    if result.status_code == 200:
        result = json.loads(result.text)
        return result
    else:
        raise Exception(f"Failed to fetch data: {result.status_code}")

def extract_data(data: dict) -> dict:
    del data['discord_invite'] # Remove empty value key existing in the response
    keys_to_extract = ["seed_stock", "gear_stock", "egg_stock"]
    # Extract data for only those keys
    data = {key: data[key] for key in keys_to_extract if key in data}
    return data

def display_data(data) -> None:
    for key in data.keys():
        for fruit in data[key]:
            item = item_rarity.get(fruit['item_id'])
            if item and item['ranking'] > MINIMUM_RARITY and fruit['item_id'] not in skipped_items:
                print(fruit['display_name'], " - ", item['rarity'])

def main() -> None:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Remaining time until next update: {get_remaining_time()} seconds")
        try:
            data = fetch_data()
            result = extract_data(data)
            display_data(result)
        except Exception as e:
            print(f"Error fetching data: {e}")
        time.sleep(get_remaining_time())

if __name__ == "__main__":
    main()
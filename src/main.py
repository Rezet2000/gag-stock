import requests
import os
import time
import json
from datetime import datetime
from constants.item_rarity import item_rarity


class Config:
    MINIMUM_RARITY: int = 2  # Rare or higher
    SUPPORTED_STOCK_KEYS = ['seed_stock', 'gear_stock', 'egg_stock']
    FETCH_TIMEOUT: int = 10 # Seconds
    SKIP_ITEMS = [
        'harvest_tool',
        'favorite_tool',
        'cleaning_spray',
    ]


def get_remaining_time() -> int:
    # TODO use response end time to calculate the remaining time
    """ Calculate the remaining time until the next 5-minute interval with seconds precision """
    minutes = datetime.now().minute
    delay = (((minutes // 5 + 1) * 5 - minutes) - 1) * \
        60 + (60 - datetime.now().second)
    return delay


def fetch_data(previous_data: dict = None) -> dict:
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    params = {'_t': int(time.time())}

    result = requests.get('https://api.joshlei.com/v2/growagarden/stock',
                          headers=headers, params=params, timeout=Config.FETCH_TIMEOUT)

    if result.status_code == 200:
        current_data = json.loads(result.text)

        if previous_data is not None and current_data == previous_data:
            print("Data unchanged, retrying in 1 second...")
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            return fetch_data(previous_data)

        return current_data
    else:
        raise Exception(f"Failed to fetch data: {result.status_code}")


def extract_data(data: dict) -> dict:
    if data.get('discord_invite'):
        # Remove empty value key existing in the response
        del data['discord_invite']
    # Extract data for only those keys
    data = {key: data[key]
            for key in Config.SUPPORTED_STOCK_KEYS if key in data}
    return data


def display_data(data) -> None:
    for key in data.keys():
        for fruit in data[key]:
            item = item_rarity.get(fruit['item_id'])
            if item and item['ranking'] > Config.MINIMUM_RARITY and fruit['item_id'] not in Config.SKIP_ITEMS:
                print(fruit['display_name'], " - ", item['rarity'])


def main() -> None:
    previous_data = None

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(
            f"Remaining time until next update: {get_remaining_time()} seconds")
        try:
            data = fetch_data(previous_data)
            previous_data = data.copy()
            result = extract_data(data)
            display_data(result)
        except Exception as e:
            print(f"Error fetching data: {e}")
        time.sleep(get_remaining_time())


if __name__ == "__main__":
    main()

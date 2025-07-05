import requests
import os
import time
import json
from datetime import datetime
from info.item_rarity import item_rarity

MINIMUM_RARITY: int = 3 # Legendary or higher

skipped_items = [
    'harvest_tool',
    'favorite_tool',
    'cleaning_spray',
]

def get_remaining_time() -> int:
    minutes = datetime.now().minute
    delay = (((minutes // 5 + 1) * 5 - minutes) - 1) * 60 + (60 - datetime.now().second) # Calculate remaining time until next 5-minute interval
    return delay

def display_data() -> None:
    result = requests.get('https://api.joshlei.com/v2/growagarden/stock')
    result_set: dict = json.loads(result.text)
    del result_set['discord_invite']

    for key in result_set.keys():
        for fruit in result_set[str(key)]:
            item = item_rarity.get(fruit['item_id'])
            if item and item.get('ranking') > MINIMUM_RARITY and fruit['item_id'] not in skipped_items:
                print(fruit['display_name'], " - ", item.get('rarity'))

def main() -> None:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Remaining time until next update: {get_remaining_time()} seconds")
        display_data()
        time.sleep(get_remaining_time())

if __name__ == "__main__":
    main()
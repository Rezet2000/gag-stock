import requests
import json
from info.item_rarity import item_rarity

result = requests.get('https://api.joshlei.com/v2/growagarden/stock')
result_set = json.loads(result.text)

skipped_items = [
    'harvest_tool',
    'favorite_tool',
    'cleaning_spary',
]

for key in result_set.keys():
    if key != 'discord_invite':
        for fruit in result_set[str(key)]:
            item = item_rarity.get(fruit['item_id'])
            if item and item.get('ranking') > 3 and fruit['item_id'] not in skipped_items:
                print(fruit['display_name'], " - ", item.get('rarity'))
import requests
import os
import time
import json
import curses
from datetime import datetime
from constants.item_rarity import item_rarity

class Config:
    MINIMUM_RARITY: int = 2  # Rare or higher
    SUPPORTED_STOCK_KEYS = ['seed_stock', 'gear_stock', 'egg_stock']
    REMAINING_TIME_DELAY_SECONDS: int = 2
    SKIP_ITEMS = [
        'harvest_tool',
        'favorite_tool',
        'cleaning_spray',
    ]

# Color mappings for rarity
RARITY_COLORS = {
    'Common': 1,      # gray
    'Uncommon': 2,    # green
    'Rare': 3,        # blue
    'Legendary': 4,   # yellow
    'Mythical': 5,    # purple
    'Divine': 6,      # pink
    'Prismatic': 7    # red
}

def init_colors():
    """Initialize color pairs for curses"""
    curses.start_color()
    curses.use_default_colors()
    
    # Define color pairs (foreground, background)
    curses.init_pair(1, curses.COLOR_WHITE, -1)    # Common: gray (white on default)
    curses.init_pair(2, curses.COLOR_GREEN, -1)    # Uncommon: green
    curses.init_pair(3, curses.COLOR_BLUE, -1)     # Rare: blue
    curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Legendary: yellow
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Mythical: purple
    curses.init_pair(6, curses.COLOR_CYAN, -1)     # Divine: pink (cyan as closest)
    curses.init_pair(7, curses.COLOR_RED, -1)      # Prismatic: red

def get_remaining_time() -> int:
    # TODO use response end time to calculate the remaining time
    """ Calculate the remaining time until the next 5-minute interval with seconds precision """
    minutes = datetime.now().minute
    delay = (((minutes // 5 + 1) * 5 - minutes) - 1) * \
        60 + (60 - datetime.now().second)
    return delay + Config.REMAINING_TIME_DELAY_SECONDS

def fetch_data(previous_data: dict = None) -> dict:
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    result = requests.get('https://api.joshlei.com/v2/growagarden/stock',
                          headers=headers)
    if result.status_code == 200:
        current_data = json.loads(result.text)
        if previous_data is not None and current_data == previous_data:
            time.sleep(1)
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

def display_data(stdscr, data, next_update_time=None, error_msg=None) -> None:
    # Clear the screen
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    current_line = 0
    
    # Display next update time if available
    if next_update_time:
        remaining = max(0, int(next_update_time - time.time()))
        next_str = f"Next update in: {remaining} seconds"
        stdscr.addstr(current_line, 0, next_str[:width-1])
        current_line += 1
    
    # Display error message if any
    if error_msg:
        stdscr.addstr(current_line, 0, f"Error: {error_msg}"[:width-1])
        current_line += 1
    
    current_line += 1  # Add blank line
    
    # Process and display data
    clean_data = []
    if data:
        for key in data.keys():
            for fruit in data[key]:
                item = item_rarity.get(fruit['item_id'])
                if item and item['ranking'] > Config.MINIMUM_RARITY and fruit['item_id'] not in Config.SKIP_ITEMS:
                    clean_data.append({
                        'text': f"{fruit['display_name']} - {item['rarity']}",
                        'rarity': item['rarity']
                    })
    
    # Display the processed data with colors
    for i, item_data in enumerate(clean_data):
        if current_line + i < height - 2:  # Leave space for bottom info
            # Split the text into item name and rarity parts
            parts = item_data['text'].split(' - ')
            if len(parts) == 2:
                item_name = parts[0]
                rarity = parts[1]
                
                # Get the color for this rarity
                color_pair = RARITY_COLORS.get(item_data['rarity'], 1)  # Default to gray
                
                # Display item name in default color, then rarity in colored
                try:
                    # Check if we have enough space for the full text
                    full_text = f"{item_name} - {rarity}"
                    if len(full_text) <= width - 1:
                        stdscr.addstr(current_line + i, 0, f"{item_name} - ")
                        stdscr.addstr(current_line + i, len(f"{item_name} - "), 
                                    rarity, curses.color_pair(color_pair))
                    else:
                        # Truncate if too long
                        stdscr.addstr(current_line + i, 0, full_text[:width-1])
                except curses.error:
                    # Fallback to no color if there's an issue
                    stdscr.addstr(current_line + i, 0, item_data['text'][:width-1])
            else:
                # Fallback if splitting doesn't work as expected
                stdscr.addstr(current_line + i, 0, item_data['text'][:width-1])
    
    # Refresh the screen to show changes
    stdscr.refresh()

def main_loop(stdscr):
    # Initialize colors
    init_colors()
    
    # Configure curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(100)  # 100ms timeout for getch()
    
    previous_data = None
    current_data = None
    next_update_time = None
    error_msg = None
    
    while True:
        current_time = time.time()
        
        # Check if it's time to fetch new data
        if next_update_time is None or current_time >= next_update_time:
            try:
                data = fetch_data(previous_data)
                previous_data = data.copy()
                current_data = extract_data(data)
                next_update_time = current_time + get_remaining_time()
                error_msg = None  # Clear any previous error
            except Exception as e:
                error_msg = str(e)
                next_update_time = current_time + 10  # Retry in 10 seconds on error
        
        # Display the data
        display_data(stdscr, current_data, next_update_time, error_msg)
        
        # Small delay to prevent excessive CPU usage
        time.sleep(0.1)

def main() -> None:
    try:
        curses.wrapper(main_loop)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
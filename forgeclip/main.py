import pyperclip
import keyboard
import json
import time
import os
import sys

HISTORY_FILE = 'history.json'
CLIPBOARD_HISTORY = []
LAST_CLIPBOARD_CONTENT = ""

def load_history():
    """Loads clipboard history from the JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                # Load history, ensuring it's a list
                history = json.load(f)
                if not isinstance(history, list):
                    print(f"Warning: History file {HISTORY_FILE} is corrupted. Starting with empty history.")
                    return []
                return history
            except json.JSONDecodeError:
                print(f"Warning: History file {HISTORY_FILE} is empty or invalid JSON. Starting with empty history.")
                return []
    return []

def save_history():
    """Saves current clipboard history to the JSON file."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(CLIPBOARD_HISTORY, f, indent=4)

def add_to_history(content):
    """Adds new content to the history if it's not the same as the last entry."""
    global CLIPBOARD_HISTORY
    # Avoid adding duplicate consecutive entries
    if not CLIPBOARD_HISTORY or CLIPBOARD_HISTORY[-1] != content:
        CLIPBOARD_HISTORY.append(content)
        print(f"Added to history: {content[:50]}...") # Print snippet for confirmation
        save_history()

def monitor_clipboard():
    """Monitors the clipboard for changes and adds new content to history."""
    global LAST_CLIPBOARD_CONTENT
    print("forgeclip started. Monitoring clipboard...")
    try:
        # Initialize LAST_CLIPBOARD_CONTENT with current clipboard content
        LAST_CLIPBOARD_CONTENT = pyperclip.paste()
        while True:
            current_content = pyperclip.paste()
            if current_content != LAST_CLIPBOARD_CONTENT:
                LAST_CLIPBOARD_CONTENT = current_content
                if current_content.strip(): # Only add non-empty content
                    add_to_history(current_content)
            time.sleep(0.1) # Check every 100ms
    except KeyboardInterrupt:
        print("forgeclip stopped.")
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")

def search_history(query):
    """Searches the clipboard history for the given query and prints matches."""
    print(f"Searching history for: '{query}'")
    matches = [(i, entry) for i, entry in enumerate(CLIPBOARD_HISTORY) if query.lower() in entry.lower()]
    if matches:
        print("Found matches:")
        for i, entry in matches:
            print(f"[{i}] {entry[:100]}...") # Print index and snippet
    else:
        print("No matches found.")

def paste_history_item(index):
    """Copies the history item at the given index back to the clipboard."""
    try:
        index = int(index)
        if 0 <= index < len(CLIPBOARD_HISTORY):
            content = CLIPBOARD_HISTORY[index]
            pyperclip.copy(content)
            print(f"Copied history item [{index}] to clipboard.")
        else:
            print(f"Error: Index {index} is out of range.")
    except ValueError:
        print(f"Error: Invalid index '{index}'. Please provide a number.")
    except Exception as e:
        print(f"An error occurred while pasting: {e}")


if __name__ == "__main__":
    CLIPBOARD_HISTORY = load_history()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "search":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                search_history(query)
            else:
                print("Usage: python main.py search <query>")
        elif command == "paste":
            if len(sys.argv) > 2:
                index = sys.argv[2]
                paste_history_item(index)
            else:
                print("Usage: python main.py paste <index>")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: search, paste")
    else:
        # No arguments, run the monitoring loop
        monitor_clipboard()

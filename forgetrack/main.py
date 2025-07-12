import win32gui
import time
import json
import os

LOG_FILE = 'usage_log.json'
USAGE_DATA = {}
LAST_ACTIVE_WINDOW = None
START_TIME = time.time()

def get_active_window_title():
    """Gets the title of the currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        return title
    except Exception as e:
        # Handle potential errors, e.g., window handle no longer valid
        # print(f"Error getting window title: {e}") # Optional: for debugging
        return None

def load_usage_data():
    """Loads usage data from the JSON file."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    print(f"Warning: Log file {LOG_FILE} is corrupted. Starting with empty data.")
                    return {}
                return data
            except json.JSONDecodeError:
                print(f"Warning: Log file {LOG_FILE} is empty or invalid JSON. Starting with empty data.")
                return {}
    return {}

def save_usage_data():
    """Saves current usage data to the JSON file."""
    with open(LOG_FILE, 'w') as f:
        json.dump(USAGE_DATA, f, indent=4)

def track_usage():
    """Monitors active window and tracks usage time."""
    global LAST_ACTIVE_WINDOW, START_TIME, USAGE_DATA
    print("forgetrack started. Tracking application usage...")

    try:
        while True:
            current_window = get_active_window_title()

            if current_window and current_window != LAST_ACTIVE_WINDOW:
                # Calculate time spent on the previous window
                if LAST_ACTIVE_WINDOW:
                    end_time = time.time()
                    duration = end_time - START_TIME
                    if LAST_ACTIVE_WINDOW not in USAGE_DATA:
                        USAGE_DATA[LAST_ACTIVE_WINDOW] = 0
                    USAGE_DATA[LAST_ACTIVE_WINDOW] += duration
                    # print(f"Spent {duration:.2f} seconds on '{LAST_ACTIVE_WINDOW}'") # Optional: for debugging

                # Start tracking for the new window
                LAST_ACTIVE_WINDOW = current_window
                START_TIME = time.time()
                # print(f"Switched to: '{LAST_ACTIVE_WINDOW}'") # Optional: for debugging

            # Save data periodically (e.g., every 60 seconds) or on switch
            # For simplicity, saving on every switch for now.
            # A more robust version might save less frequently or use a separate thread.
            save_usage_data()

            time.sleep(1) # Check every 1 second

    except KeyboardInterrupt:
        print("\nforgetrack stopped.")
        # Calculate time for the last active window before exiting
        if LAST_ACTIVE_WINDOW:
            end_time = time.time()
            duration = end_time - START_TIME
            if LAST_ACTIVE_WINDOW not in USAGE_DATA:
                USAGE_DATA[LAST_ACTIVE_WINDOW] = 0
            USAGE_DATA[LAST_ACTIVE_WINDOW] += duration
            # print(f"Spent {duration:.2f} seconds on '{LAST_ACTIVE_WINDOW}' before stopping.") # Optional: for debugging
        save_usage_data()
        print("Usage data saved.")
    except Exception as e:
        print(f"\nAn error occurred during tracking: {e}")
        # Attempt to save data even if an error occurs
        save_usage_data()


if __name__ == "__main__":
    USAGE_DATA = load_usage_data()
    track_usage()

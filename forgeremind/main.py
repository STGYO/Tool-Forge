import tkinter as tk
from tkinter import messagebox
import json
import time
from datetime import datetime
import threading
import os
import sys

REMINDERS_FILE = 'reminders.json'
REMINDERS = []

def load_reminders():
    """Loads reminders from the JSON file."""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            try:
                reminders = json.load(f)
                # Convert timestamp strings back to datetime objects
                for r in reminders:
                    if 'timestamp' in r and isinstance(r['timestamp'], str):
                        try:
                            r['timestamp'] = datetime.fromisoformat(r['timestamp'])
                        except ValueError:
                            print(f"Warning: Invalid timestamp format in reminder: {r}")
                            r['timestamp'] = None # Mark as invalid
                # Filter out invalid reminders
                return [r for r in reminders if r.get('timestamp') is not None]
            except json.JSONDecodeError:
                print(f"Warning: Reminders file {REMINDERS_FILE} is empty or invalid JSON. Starting with empty reminders.")
                return []
    return []

def save_reminders():
    """Saves current reminders to the JSON file."""
    # Convert datetime objects to ISO format strings for JSON serialization
    reminders_to_save = []
    for r in REMINDERS:
        r_copy = r.copy()
        if isinstance(r_copy.get('timestamp'), datetime):
            r_copy['timestamp'] = r_copy['timestamp'].isoformat()
        reminders_to_save.append(r_copy)

    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders_to_save, f, indent=4)

def show_reminder_popup(message):
    """Displays a reminder message in a Tkinter pop-up window."""
    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showinfo("Reminder", message)
    root.destroy()

def reminder_checker():
    """Thread function to check for upcoming reminders."""
    global REMINDERS
    print("Reminder checker started.")
    while True:
        now = datetime.now()
        reminders_to_trigger = []
        remaining_reminders = []

        for reminder in REMINDERS:
            if reminder['timestamp'] <= now:
                reminders_to_trigger.append(reminder)
            else:
                remaining_reminders.append(reminder)

        # Trigger reminders
        for reminder in reminders_to_trigger:
            print(f"Triggering reminder: {reminder['message']}")
            # Run the popup in the main thread using after() or similar if needed,
            # but for simplicity, we'll call it directly. Tkinter might complain
            # about being called from a non-main thread in complex scenarios.
            # A more robust solution would use a queue and root.after().
            show_reminder_popup(reminder['message'])

        # Update the reminders list (remove triggered one-time reminders)
        REMINDERS = remaining_reminders
        if reminders_to_trigger:
            save_reminders() # Save after triggering and removing

        time.sleep(10) # Check every 10 seconds

def add_reminder_cli():
    """Command-line interface for adding a reminder."""
    print("Enter reminder details:")
    message = input("Message: ")
    year = int(input("Year (YYYY): "))
    month = int(input("Month (MM): "))
    day = int(input("Day (DD): "))
    hour = int(input("Hour (HH, 24-hour format): "))
    minute = int(input("Minute (MM): "))

    try:
        reminder_time = datetime(year, month, day, hour, minute)
        if reminder_time <= datetime.now():
            print("Error: Cannot set a reminder in the past.")
            return

        REMINDERS.append({"message": message, "timestamp": reminder_time})
        save_reminders()
        print("Reminder added successfully.")
    except ValueError as e:
        print(f"Error: Invalid date or time input. {e}")
    except Exception as e:
        print(f"An error occurred while adding reminder: {e}")


if __name__ == "__main__":
    REMINDERS = load_reminders()

    if len(sys.argv) > 1 and sys.argv[1].lower() == "add":
        add_reminder_cli()
    else:
        # Run the reminder checker in a separate thread
        checker_thread = threading.Thread(target=reminder_checker, daemon=True)
        checker_thread.start()

        print("forge remind started. Use 'python main.py add' to add a reminder.")
        print("Press Ctrl+C to stop.")

        # Keep the main thread alive (e.g., for potential future GUI or just to prevent exit)
        # In a GUI version, root.mainloop() would handle this.
        # For this CLI version, a simple loop or join might be needed if not daemon thread.
        # With daemon=True, the thread will exit when the main program exits.
        # A simple input loop can keep the main thread alive and allow adding reminders.
        while True:
            try:
                # This loop keeps the main thread alive.
                # In a real CLI tool, you might use a command interpreter here.
                # For now, just waiting for Ctrl+C.
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nforge remind stopped.")
                sys.exit(0)
            except Exception as e:
                print(f"An error in main loop: {e}")
                time.sleep(1) # Prevent rapid error printing

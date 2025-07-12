# forgeremind

A command-line and basic Tkinter GUI tool for setting local reminders with pop-up notifications.

## Features

- Set one-time reminders.
- Set recurring reminders (future feature).
- Display reminders as pop-up windows using Tkinter.
- Store reminders in a local file (e.g., `reminders.json`).

## Requirements

- Python 3.x
- tkinter (built-in)
- json (built-in)
- time (built-in)
- datetime (built-in)
- threading (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgeremind` directory.
3. No external dependencies are required.

## Usage

Run the `main.py` script to start the reminder service.

```bash
python main.py
```

The script will run in the background and check for reminders.

To add a reminder, you can potentially use command-line arguments (future feature) or a simple input mechanism within the running script (for this basic version).

*(Note: The basic version will likely require manual editing of the `reminders.json` file or a simple command-line interface to add reminders initially. A proper GUI for adding/managing reminders is a future enhancement.)*
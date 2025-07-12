# forgeclip

A simple command-line clipboard manager that stores text clipboard history, allows searching, and reusing entries.

## Features

- Stores text copied to the clipboard.
- Saves history locally in `history.json`.
- Future versions will include a GUI.

## Requirements

- Python 3.x
- pyperclip
- keyboard
- json (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgeclip` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the `main.py` script to start the clipboard manager. It will run in the background and capture clipboard changes.

```bash
python main.py
```

*(Note: Specific commands for searching and reusing history will be implemented in `main.py`.)*
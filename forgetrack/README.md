# forgetrack

A command-line tool to track application usage by logging the active window and time spent per application on Windows.

## Features

- Logs the title of the active window.
- Records the time spent on each application.
- Stores usage data in a local JSON file.

## Requirements

- Python 3.x
- pywin32
- json (built-in)
- time (built-in)
- os (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgetrack` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the `main.py` script to start tracking application usage. The script will run in the background and log data.

```bash
python main.py
```

Press `Ctrl+C` to stop the tracker. The usage data will be saved to `usage_log.json`.

*(Note: Future versions may include options for viewing reports or specifying log file location.)*
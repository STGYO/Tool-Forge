# forgespeed

A command-line tool to log internet speed (download, upload, and ping) over time using the `speedtest-cli` library.

## Features

- Measure internet speed (download, upload, ping).
- Log speed data with timestamps.
- Store logs in a local JSON file (`speed_log.json`).
- Run tests at a specified interval.

## Requirements

- Python 3.x
- speedtest-cli
- json (built-in)
- time (built-in)
- datetime (built-in)
- threading (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgespeed` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the `main.py` script to start logging internet speed.

```bash
python main.py [interval_seconds]
```

- `[interval_seconds]`: Optional. The interval in seconds between speed tests. Defaults to 600 seconds (10 minutes) if not specified.

The script will run in the background, perform speed tests at the specified interval, and save the results to `speed_log.json`.

Press `Ctrl+C` to stop the logger.

*(Note: Running speed tests frequently can consume bandwidth. Choose an appropriate interval.)*
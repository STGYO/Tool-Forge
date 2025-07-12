import speedtest
import json
import time
from datetime import datetime
import threading
import sys
import os

LOG_FILE = 'speed_log.json'
DEFAULT_INTERVAL = 600 # 10 minutes

def load_log_data():
    """Loads existing speed log data from the JSON file."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"Warning: Log file {LOG_FILE} is corrupted. Starting with empty data.")
                    return []
                return data
            except json.JSONDecodeError:
                print(f"Warning: Log file {LOG_FILE} is empty or invalid JSON. Starting with empty data.")
                return []
    return []

def save_log_data(log_data):
    """Saves speed log data to the JSON file."""
    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=4)

def run_speed_test():
    """Runs a speed test and returns download, upload (in Mbps), and ping (in ms)."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        ping = st.results.ping

        # Convert speeds from bits/sec to Mbits/sec
        download_mbps = download_speed / (10**6)
        upload_mbps = upload_speed / (10**6)

        return {
            "timestamp": datetime.now().isoformat(),
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps,
            "ping_ms": ping
        }
    except speedtest.SpeedtestException as e:
        print(f"Speed test failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during speed test: {e}")
        return None

def speed_logger(interval):
    """Runs speed tests periodically and logs the results."""
    log_data = load_log_data()
    print(f"Speed logger started. Running tests every {interval} seconds.")
    print(f"Logging to: {LOG_FILE}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            print(f"\nRunning speed test at {datetime.now().isoformat()}...")
            result = run_speed_test()
            if result:
                log_data.append(result)
                save_log_data(log_data)
                print("Speed test completed and logged.")
            else:
                print("Speed test failed, not logging.")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nSpeed logger stopped.")
        # No need to save here, as data is saved after each successful test
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred in logger: {e}")
        sys.exit(1)


if __name__ == "__main__":
    interval = DEFAULT_INTERVAL

    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            if interval <= 0:
                print("Error: Interval must be a positive number. Using default.")
                interval = DEFAULT_INTERVAL
        except ValueError:
            print(f"Error: Invalid interval '{sys.argv[1]}'. Using default.")
            interval = DEFAULT_INTERVAL

    # Run the logger in the main thread for simplicity in this basic version.
    # For a true background service, a more robust approach (e.g., using schedule library
    # or a dedicated service framework) would be needed.
    speed_logger(interval)

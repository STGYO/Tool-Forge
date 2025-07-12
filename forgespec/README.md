# forgespec

A command-line tool to generate a snapshot of system information, including CPU, RAM, disk, operating system, and basic GPU details.

## Features

- Collects system information.
- Reports CPU details (cores, usage).
- Reports RAM usage.
- Reports disk usage.
- Reports operating system information.
- Attempts to report basic GPU information (platform dependent).
- Uses `platform`, `psutil`, and `subprocess`.

## Requirements

- Python 3.x
- psutil
- platform (built-in)
- subprocess (built-in)
- os (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgespec` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the `main.py` script to display the system information snapshot.

```bash
python main.py
```

The script will print the collected system details to the console.

*(Note: GPU information retrieval can be complex and platform-specific. The basic implementation might only provide limited details or require additional system tools to be installed.)*
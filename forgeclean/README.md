# forgeclean

A command-line disk space analyzer that walks through a selected directory and shows folder sizes, highlighting the top space-consuming directories.

## Features

- Analyze disk usage of folders within a specified directory.
- Display folder sizes in MB.
- List the top 10 largest folders.

## Requirements

- Python 3.x
- `os` (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgeclean` directory.
3. No external dependencies are required.

## Usage

Run the `main.py` script with the directory path you want to analyze.

```bash
python main.py <directory_path>
```

The script will output the size of each subdirectory and list the top 10 largest ones.
# forgesort

A command-line tool to automatically organize files in a specified directory by moving them into subfolders based on file type or modified date.

## Features

- Organize files in a source directory.
- Sort files into subfolders based on file extension (type).
- Sort files into subfolders based on modified date (Year/Month).
- Uses `shutil` for file operations.

## Requirements

- Python 3.x
- `os` (built-in)
- `shutil` (built-in)
- `datetime` (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgesort` directory.
3. No external dependencies are required.

## Usage

Run the `main.py` script with the source directory path and the desired sorting method.

```bash
python main.py <source_directory> [--method <type|date>]
```

### Options:

- `<source_directory>`: The path to the directory containing the files to sort.
- `--method <type|date>`: The sorting method to use.
    - `type`: Sorts files into folders based on their file extension (e.g., `Documents`, `Images`, `Videos`).
    - `date`: Sorts files into folders based on their modified date (e.g., `2023/01`, `2024/05`).
    - Defaults to `type` if not specified.

### Examples:

- Sort files in `./Downloads` by type:
  ```bash
  python main.py ./Downloads --method type
  ```
- Sort files in `./Desktop` by modified date:
  ```bash
  python main.py ./Desktop --method date
  ```
- Sort files in `./Downloads` by type (default method):
  ```bash
  python main.py ./Downloads
  ```

*(Note: The script will create destination folders within the source directory if they don't exist. Be cautious when running this tool, especially with the `--method date` option, as it can create many subdirectories.)*
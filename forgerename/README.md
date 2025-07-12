# forgerename

A command-line tool for bulk renaming files in a specified directory. Supports adding prefixes, suffixes, and using regular expressions for renaming.

## Features

- Rename multiple files in a directory.
- Add prefixes or suffixes to filenames.
- Use regular expressions for advanced renaming patterns.
- Preview changes before applying them.

## Requirements

- Python 3.x
- `os` (built-in)
- `re` (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgerename` directory.
3. No external dependencies are required.

## Usage

Run the `main.py` script with the desired options.

```bash
python main.py <directory_path> [options]
```

### Options:

- `--prefix <text>`: Add a prefix to each filename.
- `--suffix <text>`: Add a suffix to each filename.
- `--regex <pattern> <replacement>`: Use a regular expression pattern to find and replace parts of the filename.
- `--preview`: Show the proposed changes without actually renaming files.

### Examples:

- Add prefix "new_" to all files in `./my_folder`:
  ```bash
  python main.py ./my_folder --prefix new_
  ```
- Add suffix "_old" to all files in `./my_folder`:
  ```bash
  python main.py ./my_folder --suffix _old
  ```
- Replace spaces with underscores in filenames in `./my_folder`:
  ```bash
  python main.py ./my_folder --regex " " "_"
  ```
- Preview adding prefix "report_" to files in `./data`:
  ```bash
  python main.py ./data --prefix report_ --preview
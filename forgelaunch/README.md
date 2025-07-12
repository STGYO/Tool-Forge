# forgelaunch

A portable application launcher with a basic Tkinter GUI. Allows users to define shortcuts for applications, scripts, and folders and launch them quickly with search and filter capabilities.

## Features

- Define shortcuts with a name and path.
- Store shortcuts in a local JSON file (`shortcuts.json`).
- Basic Tkinter GUI for managing and launching shortcuts.
- Search and filter shortcuts by name.
- Launch applications, scripts, or open folders.

## Requirements

- Python 3.x
- tkinter (built-in)
- json (built-in)
- os (built-in)
- subprocess (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgelaunch` directory.
3. No external dependencies are required.

## Usage

Run the `main.py` script to launch the GUI.

```bash
python main.py
```

- Use the input fields to add new shortcuts (Name and Path).
- Click "Add Shortcut" to save the new entry.
- Use the "Search" field to filter the list of shortcuts.
- Select a shortcut from the list and click "Launch Selected" to open the associated application, script, or folder.

*(Note: The initial version will have basic functionality. Advanced features like editing/deleting shortcuts, different launch options, or more sophisticated filtering can be added later.)*
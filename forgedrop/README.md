# forgedrop

A command-line tool that sets up a simple local HTTP server to facilitate file transfer between devices on the same Wi-Fi network.

## Features

- Host files for download on the local network.
- Provide a simple interface for uploading files (future feature).
- Uses Python's built-in `http.server`.

## Requirements

- Python 3.x
- `http.server` (built-in)
- `os` (built-in)
- `socketserver` (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgedrop` directory.
3. No external dependencies are required.

## Usage

Run the `main.py` script to start the HTTP server in the current directory.

```bash
python main.py [port]
```

- `[port]`: Optional. The port number to run the server on. Defaults to 8000 if not specified.

Once the server is running, other devices on the same network can access files in the directory where the script was run by navigating to `http://<your_local_ip>:<port>` in a web browser.

*(Note: This basic version only serves files for download. Upload functionality and a more user-friendly interface are future enhancements.)*
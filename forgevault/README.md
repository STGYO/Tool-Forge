# forgevault

An offline password vault tool that encrypts and decrypts passwords stored in a local file. Includes a basic Tkinter GUI for adding and retrieving passwords.

## Features

- Securely store passwords locally.
- Encrypt and decrypt passwords using `cryptography`.
- Basic GUI for adding new password entries.
- Basic GUI for looking up and retrieving stored passwords.

## Requirements

- Python 3.x
- cryptography
- tkinter (built-in)
- json (built-in)
- os (built-in)

## Installation

1. Ensure you have Python 3.x installed.
2. Navigate to the `forgevault` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the `main.py` script to launch the password vault GUI.

```bash
python main.py
```

You will be prompted to set a master password on the first run. Remember this password, as it is required to encrypt and decrypt your vault.

*(Note: The vault data will be stored in an encrypted file named `vault.json.encrypted` in the same directory.)*
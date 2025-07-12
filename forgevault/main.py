import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

VAULT_FILE = 'vault.json.encrypted'
KEY_FILE = 'vault.key' # Store the derived key (or a way to derive it)

def derive_key(master_password, salt):
    """Derives a cryptographic key from the master password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # 256 bits
        salt=salt,
        iterations=100000, # Recommended iteration count
        backend=default_backend()
    )
    return kdf.derive(master_password.encode())

def load_key():
    """Loads the salt and derived key (or parameters to derive it) from a file."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            data = json.load(f)
            salt = urlsafe_b64decode(data['salt'])
            # In a real application, you'd store salt and iteration count,
            # and re-derive the key each time the user enters the master password.
            # For this basic version, we'll just store the salt and prompt for password.
            return salt
    return None

def save_key(salt):
    """Saves the salt to a file."""
    with open(KEY_FILE, 'w') as f:
        data = {'salt': urlsafe_b64encode(salt).decode()}
        json.dump(data, f)

def encrypt_data(data, key):
    """Encrypts data using AES in GCM mode."""
    iv = os.urandom(12) # GCM recommended IV size
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
    return iv, ciphertext, encryptor.tag

def decrypt_data(iv, ciphertext, tag, key):
    """Decrypts data using AES in GCM mode."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def load_vault(master_password):
    """Loads and decrypts the vault data."""
    salt = load_key()
    if salt is None:
        messagebox.showerror("Error", "Vault key not found. Please set a master password first.")
        return None

    key = derive_key(master_password, salt)

    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, 'rb') as f:
            try:
                encrypted_data = f.read()
                # Assuming the format is IV + Tag + Ciphertext
                iv = encrypted_data[:12]
                tag = encrypted_data[12:28] # GCM tag is 16 bytes
                ciphertext = encrypted_data[28:]

                decrypted_bytes = decrypt_data(iv, ciphertext, tag, key)
                vault_data = json.loads(decrypted_bytes.decode())
                return vault_data
            except Exception as e:
                messagebox.showerror("Decryption Error", f"Could not decrypt vault. Incorrect password or corrupted file. {e}")
                return None
    return {} # Return empty vault if file doesn't exist

def save_vault(vault_data, master_password):
    """Encrypts and saves the vault data."""
    salt = load_key()
    if salt is None:
        # First time saving, generate salt and save it
        salt = os.urandom(16)
        save_key(salt)

    key = derive_key(master_password, salt)
    data_to_encrypt = json.dumps(vault_data)
    iv, ciphertext, tag = encrypt_data(data_to_encrypt, key)

    with open(VAULT_FILE, 'wb') as f:
        # Write IV, Tag, and Ciphertext
        f.write(iv + tag + ciphertext)

class VaultGUI:
    def __init__(self, master):
        self.master = master
        master.title("ForgeVault")

        self.master_password = None
        self.vault_data = {}

        self.get_master_password()

        if self.master_password:
            self.vault_data = load_vault(self.master_password)
            if self.vault_data is None: # Decryption failed
                master.destroy()
                return

            self.create_widgets()

    def get_master_password(self):
        """Prompts the user for the master password."""
        if not os.path.exists(KEY_FILE):
            # First time setup
            password = simpledialog.askstring("Master Password Setup", "Set your master password:", show='*')
            if password:
                confirm_password = simpledialog.askstring("Master Password Setup", "Confirm your master password:", show='*')
                if password == confirm_password:
                    salt = os.urandom(16)
                    save_key(salt)
                    self.master_password = password
                    messagebox.showinfo("Success", "Master password set. Please restart the application.")
                    self.master.destroy() # Close the app after setting password
                else:
                    messagebox.showerror("Error", "Passwords do not match.")
                    self.master.destroy()
            else:
                self.master.destroy() # Close if no password is set
        else:
            # Existing vault, prompt for password to unlock
            password = simpledialog.askstring("Unlock Vault", "Enter your master password:", show='*')
            if password:
                self.master_password = password
            else:
                self.master.destroy() # Close if no password entered

    def create_widgets(self):
        """Creates the GUI elements."""
        self.label_service = tk.Label(self.master, text="Service:")
        self.label_service.grid(row=0, column=0, sticky=tk.W)
        self.entry_service = tk.Entry(self.master)
        self.entry_service.grid(row=0, column=1, sticky=tk.EW)

        self.label_username = tk.Label(self.master, text="Username:")
        self.label_username.grid(row=1, column=0, sticky=tk.W)
        self.entry_username = tk.Entry(self.master)
        self.entry_username.grid(row=1, column=1, sticky=tk.EW)

        self.label_password = tk.Label(self.master, text="Password:")
        self.label_password.grid(row=2, column=0, sticky=tk.W)
        self.entry_password = tk.Entry(self.master, show="*")
        self.entry_password.grid(row=2, column=1, sticky=tk.EW)

        self.button_add = tk.Button(self.master, text="Add Entry", command=self.add_entry)
        self.button_add.grid(row=3, column=0, columnspan=2, pady=5)

        self.label_lookup = tk.Label(self.master, text="Lookup Service:")
        self.label_lookup.grid(row=4, column=0, sticky=tk.W)
        self.entry_lookup = tk.Entry(self.master)
        self.entry_lookup.grid(row=4, column=1, sticky=tk.EW)

        self.button_lookup = tk.Button(self.master, text="Lookup", command=self.lookup_entry)
        self.button_lookup.grid(row=5, column=0, columnspan=2, pady=5)

        self.text_result = tk.Text(self.master, height=5, width=40)
        self.text_result.grid(row=6, column=0, columnspan=2, sticky=tk.EW)

    def add_entry(self):
        """Adds a new password entry to the vault."""
        service = self.entry_service.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not service or not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        self.vault_data[service] = {"username": username, "password": password}
        save_vault(self.vault_data, self.master_password)
        messagebox.showinfo("Success", f"Entry for '{service}' added.")

        # Clear input fields
        self.entry_service.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    def lookup_entry(self):
        """Looks up a password entry in the vault."""
        service = self.entry_lookup.get().strip()

        self.text_result.delete(1.0, tk.END) # Clear previous result

        if not service:
            messagebox.showwarning("Input Error", "Please enter a service to lookup.")
            return

        if service in self.vault_data:
            entry = self.vault_data[service]
            result_text = f"Service: {service}\nUsername: {entry['username']}\nPassword: {entry['password']}"
            self.text_result.insert(tk.END, result_text)
        else:
            self.text_result.insert(tk.END, f"No entry found for '{service}'.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = VaultGUI(root)
    if gui.master_password: # Only start mainloop if master password was successfully handled
        root.mainloop()

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


# --- Enhanced Vault GUI ---
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import threading
import time

class VaultGUI:
    def __init__(self, master):
        self.master = master
        master.title("ForgeVault")
        master.geometry("420x320")
        master.resizable(False, False)
        self.master_password = None
        self.vault_data = {}
        self.categories = set()
        self.clipboard_timer = None
        self.get_master_password()
        if self.master_password:
            self.vault_data = load_vault(self.master_password)
            if self.vault_data is None:
                master.destroy()
                return
            self.extract_categories()
            self.create_widgets()

    def get_master_password(self):
        if not os.path.exists(KEY_FILE):
            password = simpledialog.askstring("Master Password Setup", "Set your master password:", show='*')
            if password:
                confirm_password = simpledialog.askstring("Master Password Setup", "Confirm your master password:", show='*')
                if password == confirm_password:
                    salt = os.urandom(16)
                    save_key(salt)
                    self.master_password = password
                    messagebox.showinfo("Success", "Master password set. Please restart the application.")
                    self.master.destroy()
                else:
                    messagebox.showerror("Error", "Passwords do not match.")
                    self.master.destroy()
            else:
                self.master.destroy()
        else:
            password = simpledialog.askstring("Unlock Vault", "Enter your master password:", show='*')
            if password:
                self.master_password = password
            else:
                self.master.destroy()

    def extract_categories(self):
        self.categories = set()
        for entry in self.vault_data.values():
            cat = entry.get('category', '')
            if cat:
                self.categories.add(cat)

    def create_widgets(self):
        # Minimal UI
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Service
        ttk.Label(self.frame, text="Service:").grid(row=0, column=0, sticky=tk.W)
        self.entry_service = ttk.Entry(self.frame)
        self.entry_service.grid(row=0, column=1, sticky=tk.EW)

        # Username
        ttk.Label(self.frame, text="Username:").grid(row=1, column=0, sticky=tk.W)
        self.entry_username = ttk.Entry(self.frame)
        self.entry_username.grid(row=1, column=1, sticky=tk.EW)

        # Password
        ttk.Label(self.frame, text="Password:").grid(row=2, column=0, sticky=tk.W)
        self.entry_password = ttk.Entry(self.frame, show="*")
        self.entry_password.grid(row=2, column=1, sticky=tk.EW)

        # Category/Tag
        ttk.Label(self.frame, text="Category:").grid(row=3, column=0, sticky=tk.W)
        self.entry_category = ttk.Entry(self.frame)
        self.entry_category.grid(row=3, column=1, sticky=tk.EW)

        # Add Entry
        self.button_add = ttk.Button(self.frame, text="Add Entry", command=self.add_entry)
        self.button_add.grid(row=4, column=0, columnspan=2, pady=5)

        # Lookup
        ttk.Label(self.frame, text="Lookup Service:").grid(row=5, column=0, sticky=tk.W)
        self.entry_lookup = ttk.Entry(self.frame)
        self.entry_lookup.grid(row=5, column=1, sticky=tk.EW)
        self.button_lookup = ttk.Button(self.frame, text="Lookup", command=self.lookup_entry)
        self.button_lookup.grid(row=6, column=0, columnspan=2, pady=5)

        # Result
        self.result_frame = ttk.Frame(self.frame)
        self.result_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW)
        self.label_result = ttk.Label(self.result_frame, text="", font=("TkDefaultFont", 10))
        self.label_result.pack(anchor='w')
        self.button_reveal = ttk.Button(self.result_frame, text="Reveal", command=self.reveal_password, state='disabled')
        self.button_reveal.pack(side='left', padx=2)
        self.button_copy = ttk.Button(self.result_frame, text="Copy", command=self.copy_password, state='disabled')
        self.button_copy.pack(side='left', padx=2)

        # Backup/Restore
        self.button_backup = ttk.Button(self.frame, text="Backup Vault", command=self.backup_vault)
        self.button_backup.grid(row=8, column=0, pady=5)
        self.button_restore = ttk.Button(self.frame, text="Restore Vault", command=self.restore_vault)
        self.button_restore.grid(row=8, column=1, pady=5)

        # Category filter (optional, minimal)
        ttk.Label(self.frame, text="Filter by Category:").grid(row=9, column=0, sticky=tk.W)
        self.combo_category = ttk.Combobox(self.frame, values=list(self.categories), state='readonly')
        self.combo_category.grid(row=9, column=1, sticky=tk.EW)
        self.combo_category.bind('<<ComboboxSelected>>', self.filter_by_category)

        self.frame.columnconfigure(1, weight=1)

    def add_entry(self):
        service = self.entry_service.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        category = self.entry_category.get().strip()
        if not service or not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        self.vault_data[service] = {"username": username, "password": password, "category": category}
        save_vault(self.vault_data, self.master_password)
        self.extract_categories()
        self.combo_category['values'] = list(self.categories)
        messagebox.showinfo("Success", f"Entry for '{service}' added.")
        self.entry_service.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_category.delete(0, tk.END)

    def lookup_entry(self):
        service = self.entry_lookup.get().strip()
        self.label_result.config(text="")
        self.button_reveal.config(state='disabled')
        self.button_copy.config(state='disabled')
        self._lookup_password = None
        if not service:
            messagebox.showwarning("Input Error", "Please enter a service to lookup.")
            return
        entry = self.vault_data.get(service)
        if entry:
            self.label_result.config(text=f"Service: {service}\nUsername: {entry['username']}\nPassword: {'*' * len(entry['password'])}")
            self._lookup_password = entry['password']
            self.button_reveal.config(state='normal')
            self.button_copy.config(state='normal')
        else:
            self.label_result.config(text=f"No entry found for '{service}'.")

    def reveal_password(self):
        if self._lookup_password:
            self.label_result.config(text=self.label_result.cget('text').replace('*' * len(self._lookup_password), self._lookup_password))
            self.button_reveal.config(state='disabled')
            self.after(5000, self.hide_password)

    def hide_password(self):
        if self._lookup_password:
            self.label_result.config(text=self.label_result.cget('text').replace(self._lookup_password, '*' * len(self._lookup_password)))
            self.button_reveal.config(state='normal')

    def copy_password(self):
        if self._lookup_password:
            self.master.clipboard_clear()
            self.master.clipboard_append(self._lookup_password)
            self.button_copy.config(text='Copied!')
            if self.clipboard_timer:
                self.master.after_cancel(self.clipboard_timer)
            self.clipboard_timer = self.master.after(5000, self.clear_clipboard)

    def clear_clipboard(self):
        self.master.clipboard_clear()
        self.button_copy.config(text='Copy')

    def backup_vault(self):
        filename = filedialog.asksaveasfilename(defaultextension='.bak', filetypes=[('Backup Files', '*.bak')])
        if filename:
            try:
                with open(VAULT_FILE, 'rb') as src, open(filename, 'wb') as dst:
                    dst.write(src.read())
                messagebox.showinfo('Backup', 'Vault backup created.')
            except Exception as e:
                messagebox.showerror('Backup Error', str(e))

    def restore_vault(self):
        filename = filedialog.askopenfilename(filetypes=[('Backup Files', '*.bak')])
        if filename:
            try:
                with open(filename, 'rb') as src, open(VAULT_FILE, 'wb') as dst:
                    dst.write(src.read())
                messagebox.showinfo('Restore', 'Vault restored. Please restart the app.')
                self.master.destroy()
            except Exception as e:
                messagebox.showerror('Restore Error', str(e))

    def filter_by_category(self, event):
        cat = self.combo_category.get()
        matches = [s for s, v in self.vault_data.items() if v.get('category') == cat]
        if matches:
            self.entry_lookup.delete(0, tk.END)
            self.entry_lookup.insert(0, matches[0])
            self.lookup_entry()
        else:
            self.label_result.config(text=f"No entries in category '{cat}'.")


if __name__ == "__main__":
    root = tk.Tk()
    gui = VaultGUI(root)
    if gui.master_password: # Only start mainloop if master password was successfully handled
        root.mainloop()

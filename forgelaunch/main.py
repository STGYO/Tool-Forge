import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import subprocess
import sys

SHORTCUTS_FILE = 'shortcuts.json'
SHORTCUTS = {}

def load_shortcuts():
    """Loads shortcuts from the JSON file."""
    if os.path.exists(SHORTCUTS_FILE):
        with open(SHORTCUTS_FILE, 'r') as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    print(f"Warning: Shortcuts file {SHORTCUTS_FILE} is corrupted. Starting with empty data.")
                    return {}
                return data
            except json.JSONDecodeError:
                print(f"Warning: Shortcuts file {SHORTCUTS_FILE} is empty or invalid JSON. Starting with empty data.")
                return {}
    return {}

def save_shortcuts():
    """Saves current shortcuts to the JSON file."""
    with open(SHORTCUTS_FILE, 'w') as f:
        json.dump(SHORTCUTS, f, indent=4)

class LauncherGUI:
    def __init__(self, master):
        self.master = master
        master.title("ForgeLaunch")

        self.shortcuts = load_shortcuts()

        # --- Add Shortcut Section ---
        self.frame_add = tk.LabelFrame(master, text="Add New Shortcut")
        self.frame_add.grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW)

        self.label_name = tk.Label(self.frame_add, text="Name:")
        self.label_name.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_name = tk.Entry(self.frame_add, width=40)
        self.entry_name.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        self.label_path = tk.Label(self.frame_add, text="Path:")
        self.label_path.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_path = tk.Entry(self.frame_add, width=40)
        self.entry_path.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        self.button_browse = tk.Button(self.frame_add, text="Browse", command=self.browse_file)
        self.button_browse.grid(row=1, column=2, padx=5, pady=2)

        self.button_add = tk.Button(self.frame_add, text="Add Shortcut", command=self.add_shortcut)
        self.button_add.grid(row=2, column=0, columnspan=3, pady=5)

        # Configure column weights so entry fields expand
        self.frame_add.columnconfigure(1, weight=1)

        # --- Search and Launch Section ---
        self.frame_launch = tk.LabelFrame(master, text="Search and Launch")
        self.frame_launch.grid(row=1, column=0, padx=10, pady=5, sticky=tk.EW)

        self.label_search = tk.Label(self.frame_launch, text="Search:")
        self.label_search.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_search = tk.Entry(self.frame_launch, width=40)
        self.entry_search.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.entry_search.bind("<KeyRelease>", self.filter_list)

        self.listbox_shortcuts = tk.Listbox(self.frame_launch, height=10)
        self.listbox_shortcuts.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.listbox_shortcuts.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.button_launch = tk.Button(self.frame_launch, text="Launch Selected", command=self.launch_selected)
        self.button_launch.grid(row=2, column=0, columnspan=2, pady=5)

        # Configure column weights
        self.frame_launch.columnconfigure(1, weight=1)

        self.populate_listbox()

    def browse_file(self):
        """Opens a file dialog to select an application, script, or folder."""
        # Use askopenfilename for files, askdirectory for folders.
        # For simplicity, let's use askopenfilename and allow all files.
        # A more advanced version could use different dialogs or check file types.
        filepath = filedialog.askopenfilename(
            title="Select File or Application",
            filetypes=(("All files", "*.*"),)
        )
        if filepath:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, filepath)

    def add_shortcut(self):
        """Adds a new shortcut to the list and saves it."""
        name = self.entry_name.get().strip()
        path = self.entry_path.get().strip()

        if not name or not path:
            messagebox.showwarning("Input Error", "Please provide both a name and a path.")
            return

        if name in self.shortcuts:
            if not messagebox.askyesno("Overwrite?", f"Shortcut '{name}' already exists. Overwrite?"):
                return

        self.shortcuts[name] = path
        save_shortcuts()
        self.populate_listbox()
        messagebox.showinfo("Success", f"Shortcut '{name}' added.")

        # Clear input fields
        self.entry_name.delete(0, tk.END)
        self.entry_path.delete(0, tk.END)

    def populate_listbox(self, filtered_names=None):
        """Populates the listbox with shortcut names."""
        self.listbox_shortcuts.delete(0, tk.END)
        names_to_display = filtered_names if filtered_names is not None else sorted(self.shortcuts.keys())
        for name in names_to_display:
            self.listbox_shortcuts.insert(tk.END, name)

    def filter_list(self, event):
        """Filters the listbox based on the search entry."""
        query = self.entry_search.get().strip().lower()
        filtered_names = [name for name in sorted(self.shortcuts.keys()) if query in name.lower()]
        self.populate_listbox(filtered_names)

    def on_listbox_select(self, event):
        """Handles selection in the listbox (optional, could display path)."""
        # You could add logic here to display the path of the selected shortcut
        # in a label or entry field if desired.
        pass

    def launch_selected(self):
        """Launches the application, script, or folder associated with the selected shortcut."""
        selected_indices = self.listbox_shortcuts.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a shortcut to launch.")
            return

        # Get the selected shortcut name from the listbox
        selected_name = self.listbox_shortcuts.get(selected_indices[0])
        shortcut_path = self.shortcuts.get(selected_name)

        if not shortcut_path:
            messagebox.showerror("Launch Error", f"Path not found for shortcut '{selected_name}'.")
            return

        try:
            # Use os.startfile on Windows, subprocess.call on others
            if sys.platform == "win32":
                os.startfile(shortcut_path)
            else:
                # For Linux/macOS, use subprocess.call with appropriate command
                # This is a basic attempt; more robust handling might be needed
                # depending on the type of file (executable, script, folder).
                subprocess.call(['open', shortcut_path]) # macOS
                # subprocess.call(['xdg-open', shortcut_path]) # Linux
            print(f"Launched: {shortcut_path}")
        except FileNotFoundError:
            messagebox.showerror("Launch Error", f"File or application not found at '{shortcut_path}'.")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch '{shortcut_path}': {e}")


if __name__ == "__main__":
    root = tk.Tk()
    gui = LauncherGUI(root)
    root.mainloop()

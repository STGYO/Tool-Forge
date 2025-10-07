

# ForgeClip GUI Clipboard Manager
import pyperclip
import json
import os
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

HISTORY_FILE = 'history.json'
MAX_HISTORY = 500

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
                if not isinstance(history, list):
                    return []
                return history
            except Exception:
                return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history[-MAX_HISTORY:], f, indent=2, ensure_ascii=False)

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeClip - Clipboard Manager")
        self.history = load_history()
        self.filtered = self.history[::-1]  # reverse chronological
        self.last_clip = ""
        self.monitoring = True

        # Search bar
        search_frame = ttk.Frame(root)
        search_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.update_filter)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)

        # Buttons
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side="left")
        ttk.Button(btn_frame, text="Pause", command=self.toggle_monitor).pack(side="left")

        # Listbox for history
        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, activestyle='dotbox')
        self.listbox.pack(fill="both", expand=True, padx=5, pady=2)
        self.listbox.bind('<Double-1>', self.recopy_selected)
        self.listbox.bind('<Return>', self.recopy_selected)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.listbox, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.update_listbox()

        # Start clipboard monitor in a thread
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

    def update_filter(self, *args):
        query = self.search_var.get().lower()
        if query:
            self.filtered = [h for h in self.history[::-1] if query in h.lower()]
        else:
            self.filtered = self.history[::-1]
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for entry in self.filtered:
            display = entry.replace('\n', ' ')[:100]
            self.listbox.insert(tk.END, display)

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all clipboard history?"):
            self.history.clear()
            save_history(self.history)
            self.update_filter()

    def recopy_selected(self, event=None):
        idx = self.listbox.curselection()
        if not idx:
            return
        entry = self.filtered[idx[0]]
        try:
            pyperclip.copy(entry)
            messagebox.showinfo("Copied", "Copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")

    def toggle_monitor(self):
        self.monitoring = not self.monitoring
        msg = "Clipboard monitoring resumed." if self.monitoring else "Clipboard monitoring paused."
        messagebox.showinfo("Monitor", msg)

    def monitor_clipboard(self):
        while True:
            if self.monitoring:
                try:
                    current = pyperclip.paste()
                    if current != self.last_clip and current.strip():
                        self.last_clip = current
                        if not self.history or self.history[-1] != current:
                            self.history.append(current)
                            save_history(self.history)
                            self.update_filter()
                except Exception:
                    pass
            time.sleep(0.2)

def main():
    root = tk.Tk()
    root.geometry("600x400")
    app = ClipboardManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()

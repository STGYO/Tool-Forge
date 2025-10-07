
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import time
from datetime import datetime, timedelta
import threading
import os
import sys
try:
    from playsound import playsound
except ImportError:
    playsound = None

REMINDERS_FILE = 'reminders.json'

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            try:
                reminders = json.load(f)
                for r in reminders:
                    if 'timestamp' in r and isinstance(r['timestamp'], str):
                        try:
                            r['timestamp'] = datetime.fromisoformat(r['timestamp'])
                        except Exception:
                            r['timestamp'] = None
                return [r for r in reminders if r.get('timestamp') is not None]
            except Exception:
                return []
    return []

def save_reminders(reminders):
    reminders_to_save = []
    for r in reminders:
        r_copy = r.copy()
        if isinstance(r_copy.get('timestamp'), datetime):
            r_copy['timestamp'] = r_copy['timestamp'].isoformat()
        reminders_to_save.append(r_copy)
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders_to_save, f, indent=4)

def play_sound():
    if playsound:
        try:
            playsound('SystemExclamation.wav') # Use a system sound or provide your own
        except Exception:
            pass

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeRemind - Reminder App")
        self.reminders = load_reminders()
        self.selected_idx = None
        self.running = True

        # Reminder list
        self.listbox = tk.Listbox(root, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=2)
        tk.Button(btn_frame, text="Add One-Time", command=self.add_one_time).pack(side="left")
        tk.Button(btn_frame, text="Add Recurring", command=self.add_recurring).pack(side="left")
        tk.Button(btn_frame, text="Edit", command=self.edit_selected).pack(side="left")
        tk.Button(btn_frame, text="Remove", command=self.remove_selected).pack(side="left")

        self.status = tk.StringVar()
        tk.Label(root, textvariable=self.status).pack(fill="x", padx=5, pady=2)

        self.update_list()
        self.checker_thread = threading.Thread(target=self.reminder_checker, daemon=True)
        self.checker_thread.start()

    def update_list(self):
        self.listbox.delete(0, tk.END)
        for r in sorted(self.reminders, key=lambda x: x['timestamp']):
            t = r['timestamp'].strftime('%Y-%m-%d %H:%M')
            msg = r['message']
            if r.get('recurring'):
                msg += f" (Every {r['recurring']})"
            self.listbox.insert(tk.END, f"{t} - {msg}")

    def on_select(self, event):
        idxs = self.listbox.curselection()
        self.selected_idx = idxs[0] if idxs else None

    def add_one_time(self):
        msg = simpledialog.askstring("Reminder", "Message:")
        if not msg:
            return
        dt = self.ask_datetime()
        if not dt:
            return
        self.reminders.append({"message": msg, "timestamp": dt})
        save_reminders(self.reminders)
        self.update_list()

    def add_recurring(self):
        msg = simpledialog.askstring("Reminder", "Message:")
        if not msg:
            return
        dt = self.ask_datetime()
        if not dt:
            return
        freq = simpledialog.askstring("Recurring", "Repeat every (e.g. 'day', 'week', 'hour'):")
        if not freq:
            return
        self.reminders.append({"message": msg, "timestamp": dt, "recurring": freq})
        save_reminders(self.reminders)
        self.update_list()

    def edit_selected(self):
        if self.selected_idx is None:
            return
        r = sorted(self.reminders, key=lambda x: x['timestamp'])[self.selected_idx]
        msg = simpledialog.askstring("Edit Message", "Message:", initialvalue=r['message'])
        if not msg:
            return
        dt = self.ask_datetime(initial=r['timestamp'])
        if not dt:
            return
        freq = r.get('recurring')
        if freq:
            freq = simpledialog.askstring("Recurring", "Repeat every (e.g. 'day', 'week', 'hour'):", initialvalue=freq)
        r['message'] = msg
        r['timestamp'] = dt
        if freq:
            r['recurring'] = freq
        elif 'recurring' in r:
            del r['recurring']
        save_reminders(self.reminders)
        self.update_list()

    def remove_selected(self):
        if self.selected_idx is None:
            return
        r = sorted(self.reminders, key=lambda x: x['timestamp'])[self.selected_idx]
        self.reminders.remove(r)
        save_reminders(self.reminders)
        self.update_list()

    def ask_datetime(self, initial=None):
        # Simple dialog for date/time (could be improved)
        if initial is None:
            initial = datetime.now() + timedelta(minutes=1)
        y = simpledialog.askinteger("Year", "Year:", initialvalue=initial.year)
        m = simpledialog.askinteger("Month", "Month:", initialvalue=initial.month)
        d = simpledialog.askinteger("Day", "Day:", initialvalue=initial.day)
        h = simpledialog.askinteger("Hour", "Hour (24h):", initialvalue=initial.hour)
        mi = simpledialog.askinteger("Minute", "Minute:", initialvalue=initial.minute)
        try:
            return datetime(y, m, d, h, mi)
        except Exception:
            return None

    def reminder_checker(self):
        while self.running:
            now = datetime.now()
            triggered = []
            for r in self.reminders:
                if r['timestamp'] <= now:
                    self.root.after(0, self.show_reminder_popup, r['message'])
                    if r.get('recurring'):
                        r['timestamp'] = self.next_occurrence(r['timestamp'], r['recurring'])
                    else:
                        triggered.append(r)
            if triggered:
                for r in triggered:
                    self.reminders.remove(r)
                save_reminders(self.reminders)
                self.update_list()
            time.sleep(10)

    def show_reminder_popup(self, message):
        messagebox.showinfo("Reminder", message)
        play_sound()

    def next_occurrence(self, dt, freq):
        if freq == 'day':
            return dt + timedelta(days=1)
        elif freq == 'week':
            return dt + timedelta(weeks=1)
        elif freq == 'hour':
            return dt + timedelta(hours=1)
        else:
            return dt + timedelta(days=1)

def main():
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

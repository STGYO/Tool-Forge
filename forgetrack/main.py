
# ForgeTrack: Cross-platform App Usage Tracker with GUI
import os
import sys
import time
import json
import threading
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import psutil

LOG_FILE = 'usage_log.json'
IDLE_THRESHOLD = 60  # seconds of inactivity to consider system idle

def get_active_window_title():
    system = platform.system()
    try:
        if system == 'Windows':
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        elif system == 'Darwin':
            from AppKit import NSWorkspace
            return NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
        elif system == 'Linux':
            import subprocess
            try:
                root = subprocess.check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW'])
                window_id = root.decode().strip().split()[-1]
                if window_id == '0x0':
                    return None
                win = subprocess.check_output(['xprop', '-id', window_id, 'WM_CLASS'])
                return win.decode().split('=')[-1].strip().strip('"')
            except Exception:
                return None
        else:
            return None
    except Exception:
        return None

def get_idle_time():
    system = platform.system()
    try:
        if system == 'Windows':
            import ctypes
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return millis / 1000.0
        elif system == 'Linux':
            import subprocess
            try:
                idle = subprocess.check_output(['xprintidle'])
                return int(idle) / 1000.0
            except Exception:
                return 0
        elif system == 'Darwin':
            # macOS idle time (approximate)
            import subprocess
            try:
                idle = subprocess.check_output(['ioreg', '-c', 'IOHIDSystem'])
                for line in idle.decode().split('\n'):
                    if 'HIDIdleTime' in line:
                        nanosec = int(line.split('=')[-1].strip())
                        return nanosec / 1e9
            except Exception:
                return 0
        return 0
    except Exception:
        return 0

def load_usage_data():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
            except Exception:
                return []
    return []

def save_usage_data(data):
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def export_data(data, filetype):
    if filetype == 'csv':
        import csv
        filename = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not filename:
            return
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['App', 'Start', 'End', 'Duration (s)'])
            for entry in data:
                writer.writerow([entry['app'], entry['start'], entry['end'], entry['duration']])
    elif filetype == 'json':
        filename = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not filename:
            return
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

class Tracker:
    def __init__(self):
        self.data = load_usage_data()  # List of {app, start, end, duration}
        self.current_app = None
        self.current_start = None
        self.paused = False
        self.running = True
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self._track_loop, daemon=True).start()

    def _track_loop(self):
        while self.running:
            if self.paused:
                time.sleep(1)
                continue
            idle = get_idle_time()
            if idle > IDLE_THRESHOLD:
                app = 'Idle'
            else:
                app = get_active_window_title() or 'Unknown'
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with self.lock:
                if app != self.current_app:
                    if self.current_app is not None:
                        end = now
                        duration = (datetime.strptime(now, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.current_start, '%Y-%m-%d %H:%M:%S')).total_seconds()
                        if duration > 0:
                            self.data.append({'app': self.current_app, 'start': self.current_start, 'end': end, 'duration': duration})
                            save_usage_data(self.data)
                    self.current_app = app
                    self.current_start = now
            time.sleep(1)

    def stop(self):
        self.running = False
        with self.lock:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if self.current_app and self.current_start:
                duration = (datetime.strptime(now, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.current_start, '%Y-%m-%d %H:%M:%S')).total_seconds()
                if duration > 0:
                    self.data.append({'app': self.current_app, 'start': self.current_start, 'end': now, 'duration': duration})
                    save_usage_data(self.data)

    def get_summary(self, start_date=None, end_date=None):
        # Returns dict: app -> total seconds in date range
        summary = {}
        for entry in self.data:
            s = datetime.strptime(entry['start'], '%Y-%m-%d %H:%M:%S')
            if start_date and s < start_date:
                continue
            if end_date and s > end_date:
                continue
            app = entry['app']
            summary[app] = summary.get(app, 0) + entry['duration']
        return summary

    def get_sessions(self, start_date=None, end_date=None):
        # Returns list of sessions in date range
        sessions = []
        for entry in self.data:
            s = datetime.strptime(entry['start'], '%Y-%m-%d %H:%M:%S')
            if start_date and s < start_date:
                continue
            if end_date and s > end_date:
                continue
            sessions.append(entry)
        return sessions

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

class TrackerApp(tk.Tk):
    def __init__(self, tracker):
        super().__init__()
        self.title('ForgeTrack – App Usage Tracker')
        self.geometry('700x500')
        self.tracker = tracker
        self.protocol('WM_DELETE_WINDOW', self.on_close)

        # Date filter
        self.filter_frame = ttk.Frame(self)
        self.filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(self.filter_frame, text='From:').pack(side='left')
        self.from_var = tk.StringVar()
        self.from_entry = ttk.Entry(self.filter_frame, textvariable=self.from_var, width=12)
        self.from_entry.pack(side='left', padx=2)
        ttk.Label(self.filter_frame, text='To:').pack(side='left')
        self.to_var = tk.StringVar()
        self.to_entry = ttk.Entry(self.filter_frame, textvariable=self.to_var, width=12)
        self.to_entry.pack(side='left', padx=2)
        self.filter_btn = ttk.Button(self.filter_frame, text='Apply Filter', command=self.refresh)
        self.filter_btn.pack(side='left', padx=5)

        # Pause/Resume
        self.pause_btn = ttk.Button(self.filter_frame, text='Pause', command=self.toggle_pause)
        self.pause_btn.pack(side='right', padx=5)
        self.paused = False

        # Export
        self.export_csv_btn = ttk.Button(self.filter_frame, text='Export CSV', command=lambda: export_data(self.tracker.get_sessions(self.get_from(), self.get_to()), 'csv'))
        self.export_csv_btn.pack(side='right', padx=2)
        self.export_json_btn = ttk.Button(self.filter_frame, text='Export JSON', command=lambda: export_data(self.tracker.get_sessions(self.get_from(), self.get_to()), 'json'))
        self.export_json_btn.pack(side='right', padx=2)

        # Top-used apps
        self.top_frame = ttk.LabelFrame(self, text='Top Used Apps')
        self.top_frame.pack(fill='x', padx=10, pady=5)
        self.top_tree = ttk.Treeview(self.top_frame, columns=('App', 'Time (min)'), show='headings', height=5)
        self.top_tree.heading('App', text='App')
        self.top_tree.heading('Time (min)', text='Time (min)')
        self.top_tree.pack(fill='x')

        # Session log
        self.log_frame = ttk.LabelFrame(self, text='Session Log')
        self.log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.log_tree = ttk.Treeview(self.log_frame, columns=('App', 'Start', 'End', 'Duration (min)'), show='headings')
        for col in ('App', 'Start', 'End', 'Duration (min)'):
            self.log_tree.heading(col, text=col)
        self.log_tree.pack(fill='both', expand=True)

        self.refresh()
        self.after(5000, self.periodic_refresh)

    def get_from(self):
        try:
            return datetime.strptime(self.from_var.get(), '%Y-%m-%d') if self.from_var.get() else None
        except Exception:
            return None

    def get_to(self):
        try:
            return datetime.strptime(self.to_var.get(), '%Y-%m-%d') + timedelta(days=1) if self.to_var.get() else None
        except Exception:
            return None

    def refresh(self):
        # Top-used apps
        for i in self.top_tree.get_children():
            self.top_tree.delete(i)
        summary = self.tracker.get_summary(self.get_from(), self.get_to())
        top = sorted(summary.items(), key=lambda x: x[1], reverse=True)[:10]
        for app, secs in top:
            self.top_tree.insert('', 'end', values=(app, f'{secs/60:.1f}'))
        # Session log
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
        sessions = self.tracker.get_sessions(self.get_from(), self.get_to())
        for entry in sessions[-200:][::-1]:
            self.log_tree.insert('', 'end', values=(entry['app'], entry['start'], entry['end'], f'{entry['duration']/60:.1f}'))

    def periodic_refresh(self):
        self.refresh()
        self.after(5000, self.periodic_refresh)

    def toggle_pause(self):
        if self.paused:
            self.tracker.resume()
            self.pause_btn.config(text='Pause')
            self.paused = False
        else:
            self.tracker.pause()
            self.pause_btn.config(text='Resume')
            self.paused = True

    def on_close(self):
        self.tracker.stop()
        self.destroy()

if __name__ == '__main__':
    tracker = Tracker()
    tracker.start()
    app = TrackerApp(tracker)
    app.mainloop()

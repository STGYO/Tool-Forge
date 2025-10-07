
import platform
import psutil
import subprocess
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, timedelta

def get_system_info():
    info = {}
    # OS
    info['os'] = {
        'System': platform.system(),
        'Node Name': platform.node(),
        'Release': platform.release(),
        'Version': platform.version(),
        'Machine': platform.machine(),
        'Processor': platform.processor(),
        'Architecture': str(platform.architecture())
    }
    # CPU
    info['cpu'] = {
        'Physical cores': psutil.cpu_count(logical=False),
        'Total cores': psutil.cpu_count(logical=True),
        'CPU usage': f"{psutil.cpu_percent(interval=1)}%",
        'CPU frequency': f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else 'N/A'
    }
    # RAM
    svmem = psutil.virtual_memory()
    info['ram'] = {
        'Total': f"{svmem.total / (1024**3):.2f} GB",
        'Available': f"{svmem.available / (1024**3):.2f} GB",
        'Used': f"{svmem.used / (1024**3):.2f} GB",
        'Percentage': f"{svmem.percent}%"
    }
    # Disk
    info['disk'] = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            info['disk'][partition.device] = {
                'Mountpoint': partition.mountpoint,
                'File system type': partition.fstype,
                'Total Size': f"{usage.total / (1024**3):.2f} GB",
                'Used': f"{usage.used / (1024**3):.2f} GB",
                'Free': f"{usage.free / (1024**3):.2f} GB",
                'Percentage': f"{usage.percent}%"
            }
        except Exception:
            info['disk'][partition.device] = {'Error': 'Permission denied or unavailable'}
    # GPU (best effort)
    info['gpu'] = {}
    sysname = platform.system()
    if sysname == "Windows":
        try:
            command = "wmic path win32_videocontroller get name"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                gpu_names = [line.strip() for line in result.stdout.splitlines() if line.strip() and "Name" not in line]
                info['gpu']['Name'] = ", ".join(gpu_names) if gpu_names else 'Unknown'
            else:
                info['gpu']['Error'] = result.stderr.strip()
        except Exception as e:
            info['gpu']['Error'] = str(e)
    elif sysname == "Darwin":
        try:
            command = "system_profiler SPDisplaysDataType"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            info['gpu']['Info'] = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        except Exception as e:
            info['gpu']['Error'] = str(e)
    elif sysname == "Linux":
        try:
            command = "lspci -vnn | grep -i VGA"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            info['gpu']['Info'] = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        except Exception as e:
            info['gpu']['Error'] = str(e)
    # Uptime
    try:
        boot = datetime.fromtimestamp(psutil.boot_time())
        now = datetime.now()
        uptime = now - boot
        info['uptime'] = str(uptime).split('.')[0]
    except Exception:
        info['uptime'] = 'N/A'
    # Battery
    try:
        battery = psutil.sensors_battery()
        if battery:
            info['battery'] = {
                'Percent': f"{battery.percent}%",
                'Plugged in': battery.power_plugged,
                'Time left': f"{timedelta(seconds=battery.secsleft)}" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Unlimited'
            }
        else:
            info['battery'] = 'No battery info available'
    except Exception:
        info['battery'] = 'N/A'
    return info

def export_txt(info, filename):
    with open(filename, 'w') as f:
        for section, data in info.items():
            f.write(f"--- {section.upper()} ---\n")
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        f.write(f"{k}:\n")
                        for sk, sv in v.items():
                            f.write(f"  {sk}: {sv}\n")
                    else:
                        f.write(f"{k}: {v}\n")
            else:
                f.write(f"{data}\n")
            f.write("\n")

def export_json(info, filename):
    with open(filename, 'w') as f:
        json.dump(info, f, indent=2)

class SpecApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeSpec - System Info")
        self.info = get_system_info()

        self.text = tk.Text(root, wrap="word", height=30, width=80)
        self.text.pack(fill="both", expand=True, padx=5, pady=5)
        self.text.insert("end", self.format_info(self.info))

        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_frame, text="Copy All", command=self.copy_all).pack(side="left")
        ttk.Button(btn_frame, text="Export TXT", command=self.export_txt).pack(side="left")
        ttk.Button(btn_frame, text="Export JSON", command=self.export_json).pack(side="left")

    def format_info(self, info):
        out = []
        for section, data in info.items():
            out.append(f"--- {section.upper()} ---")
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        out.append(f"{k}:")
                        for sk, sv in v.items():
                            out.append(f"  {sk}: {sv}")
                    else:
                        out.append(f"{k}: {v}")
            else:
                out.append(str(data))
            out.append("")
        return "\n".join(out)

    def copy_all(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text.get("1.0", "end"))
        messagebox.showinfo("Copied", "System info copied to clipboard.")

    def export_txt(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if f:
            export_txt(self.info, f)
            messagebox.showinfo("Export", f"Exported to {f}")

    def export_json(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if f:
            export_json(self.info, f)
            messagebox.showinfo("Export", f"Exported to {f}")

def main():
    root = tk.Tk()
    app = SpecApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

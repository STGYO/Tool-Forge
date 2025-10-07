
import speedtest
import json
import time
from datetime import datetime
import threading
import os
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

LOG_FILE = 'speed_log.json'
SLOWDOWN_THRESHOLD_MBPS = 10 # Example threshold for download speed

def load_log_data():
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

def save_log_data(log_data):
    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=4)

def run_speed_test():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        ping = st.results.ping
        download_mbps = download_speed / (10**6)
        upload_mbps = upload_speed / (10**6)
        return {
            "timestamp": datetime.now().isoformat(),
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps,
            "ping_ms": ping
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

def summarize(log):
    if not log:
        return {}
    dls = [x['download_mbps'] for x in log if 'download_mbps' in x]
    uls = [x['upload_mbps'] for x in log if 'upload_mbps' in x]
    pings = [x['ping_ms'] for x in log if 'ping_ms' in x]
    return {
        'current': log[-1] if log else {},
        'avg_dl': sum(dls)/len(dls) if dls else 0,
        'min_dl': min(dls) if dls else 0,
        'max_dl': max(dls) if dls else 0,
        'avg_ul': sum(uls)/len(uls) if uls else 0,
        'min_ul': min(uls) if uls else 0,
        'max_ul': max(uls) if uls else 0,
        'avg_ping': sum(pings)/len(pings) if pings else 0,
        'min_ping': min(pings) if pings else 0,
        'max_ping': max(pings) if pings else 0,
    }

class SpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeSpeed - Network Speed Test")
        self.log = load_log_data()

        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_frame, text="Run Test", command=self.run_test).pack(side="left")
        ttk.Button(btn_frame, text="Refresh Graph", command=self.plot_graph).pack(side="left")
        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side="left")

        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status).pack(fill="x", padx=5, pady=2)

        self.fig, self.ax = plt.subplots(figsize=(7,3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        self.summary_label = tk.Label(root, text="", justify="left")
        self.summary_label.pack(fill="x", padx=5, pady=2)

        self.plot_graph()
        self.update_summary()

    def run_test(self):
        self.status.set("Running speed test...")
        self.root.update()
        result = run_speed_test()
        if 'error' in result:
            messagebox.showerror("Speed Test Error", result['error'])
            self.status.set("Speed test failed.")
            return
        self.log.append(result)
        save_log_data(self.log)
        self.status.set("Speed test complete.")
        self.plot_graph()
        self.update_summary()
        if result['download_mbps'] < SLOWDOWN_THRESHOLD_MBPS:
            messagebox.showwarning("Slowdown Detected", f"Download speed dropped below {SLOWDOWN_THRESHOLD_MBPS} Mbps!")

    def plot_graph(self):
        self.ax.clear()
        dls = [x['download_mbps'] for x in self.log if 'download_mbps' in x]
        uls = [x['upload_mbps'] for x in self.log if 'upload_mbps' in x]
        pings = [x['ping_ms'] for x in self.log if 'ping_ms' in x]
        ts = [x['timestamp'][5:16] for x in self.log if 'timestamp' in x]
        if dls:
            self.ax.plot(ts, dls, label='Download (Mbps)', marker='o')
        if uls:
            self.ax.plot(ts, uls, label='Upload (Mbps)', marker='o')
        if pings:
            self.ax.plot(ts, pings, label='Ping (ms)', marker='o')
        self.ax.legend()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Speed / Ping')
        self.ax.set_title('Network Speed Over Time')
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def update_summary(self):
        s = summarize(self.log)
        if not s:
            self.summary_label.config(text="No data.")
            return
        cur = s['current']
        txt = (
            f"Current: DL {cur.get('download_mbps',0):.2f} Mbps, UL {cur.get('upload_mbps',0):.2f} Mbps, Ping {cur.get('ping_ms',0):.2f} ms\n"
            f"Average: DL {s['avg_dl']:.2f} Mbps, UL {s['avg_ul']:.2f} Mbps, Ping {s['avg_ping']:.2f} ms\n"
            f"Min: DL {s['min_dl']:.2f} Mbps, UL {s['min_ul']:.2f} Mbps, Ping {s['min_ping']:.2f} ms\n"
            f"Max: DL {s['max_dl']:.2f} Mbps, UL {s['max_ul']:.2f} Mbps, Ping {s['max_ping']:.2f} ms"
        )
        self.summary_label.config(text=txt)

    def clear_log(self):
        if messagebox.askyesno("Clear Log", "Are you sure you want to clear all speed test history?"):
            self.log.clear()
            save_log_data(self.log)
            self.plot_graph()
            self.update_summary()

def main():
    root = tk.Tk()
    app = SpeedApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

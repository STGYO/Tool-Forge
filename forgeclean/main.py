
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import json
import time

LOG_FILE = "delete_log.txt"

def get_size(path):
    """Get size of file or folder (recursively for folders)."""
    total = 0
    if os.path.isfile(path):
        try:
            total = os.path.getsize(path)
        except Exception:
            pass
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
                except Exception:
                    pass
    return total

def scan_directory(directory, exclude_patterns=None):
    """Scan directory and return list of (name, path, type, size)."""
    items = []
    try:
        for entry in os.listdir(directory):
            path = os.path.join(directory, entry)
            if exclude_patterns and any(p in path for p in exclude_patterns):
                continue
            t = "Folder" if os.path.isdir(path) else "File"
            size = get_size(path)
            items.append({"name": entry, "path": path, "type": t, "size": size})
    except Exception as e:
        print(f"Error scanning directory: {e}")
    return items

def log_delete(path):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()}: Deleted {path}\n")

def export_csv(data, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "path", "type", "size"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def export_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

class DiskAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeClean - Disk Analyzer")
        self.data = []
        self.exclude_patterns = []
        self.current_dir = os.getcwd()
        self.sort_by = tk.StringVar(value="size")
        self.sort_order = tk.BooleanVar(value=True)  # True=desc, False=asc

        # Directory selection
        dir_frame = ttk.Frame(root)
        dir_frame.pack(fill="x", padx=5, pady=5)
        self.dir_label = ttk.Label(dir_frame, text=f"Directory: {self.current_dir}")
        self.dir_label.pack(side="left", expand=True, fill="x")
        ttk.Button(dir_frame, text="Browse", command=self.browse_dir).pack(side="right")

        # Exclude pattern entry
        ex_frame = ttk.Frame(root)
        ex_frame.pack(fill="x", padx=5)
        ttk.Label(ex_frame, text="Exclude pattern (comma-separated):").pack(side="left")
        self.exclude_entry = ttk.Entry(ex_frame)
        self.exclude_entry.pack(side="left", fill="x", expand=True)

        # Table
        self.tree = ttk.Treeview(root, columns=("type", "size", "path"), show="headings")
        self.tree.heading("type", text="Type", command=lambda: self.sort_table("type"))
        self.tree.heading("size", text="Size (MB)", command=lambda: self.sort_table("size"))
        self.tree.heading("path", text="Path", command=lambda: self.sort_table("name"))
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(btn_frame, text="Scan", command=self.scan).pack(side="left")
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left")
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side="left")
        ttk.Button(btn_frame, text="Export JSON", command=self.export_json).pack(side="left")
        ttk.Button(btn_frame, text="Bar Chart", command=self.show_chart).pack(side="left")

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.current_dir)
        if d:
            self.current_dir = d
            self.dir_label.config(text=f"Directory: {self.current_dir}")

    def scan(self):
        exclude = self.exclude_entry.get().split(",") if self.exclude_entry.get() else []
        self.exclude_patterns = [e.strip() for e in exclude if e.strip()]
        self.tree.delete(*self.tree.get_children())
        self.data = scan_directory(self.current_dir, self.exclude_patterns)
        self.sort_table(self.sort_by.get(), redraw=False)
        self.redraw_table()

    def sort_table(self, by, redraw=True):
        reverse = self.sort_order.get() if by == self.sort_by.get() else True
        self.data.sort(key=lambda x: x[by] if by != "size" else x[by], reverse=reverse)
        self.sort_by.set(by)
        self.sort_order.set(reverse)
        if redraw:
            self.redraw_table()

    def redraw_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.data:
            self.tree.insert("", "end", values=(item["type"], f"{item['size']/(1024*1024):.2f}", item["path"]))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "No item selected.")
            return
        paths = [self.tree.item(i)["values"][2] for i in selected]
        msg = "Are you sure you want to delete the following?\n" + "\n".join(paths)
        if not messagebox.askyesno("Confirm Delete", msg):
            return
        for p in paths:
            try:
                if os.path.isfile(p):
                    os.remove(p)
                elif os.path.isdir(p):
                    import shutil
                    shutil.rmtree(p)
                log_delete(p)
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete {p}: {e}")
        self.scan()

    def export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if f:
            export_csv(self.data, f)
            messagebox.showinfo("Export", f"Exported to {f}")

    def export_json(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if f:
            export_json(self.data, f)
            messagebox.showinfo("Export", f"Exported to {f}")

    def show_chart(self):
        if not self.data:
            messagebox.showinfo("Chart", "No data to display.")
            return
        top_items = sorted(self.data, key=lambda x: x["size"], reverse=True)[:10]
        names = [i["name"] for i in top_items]
        sizes = [i["size"]/(1024*1024) for i in top_items]
        fig, ax = plt.subplots()
        ax.barh(names, sizes)
        ax.set_xlabel("Size (MB)")
        ax.set_title("Top 10 Largest Files/Folders")
        plt.tight_layout()
        win = tk.Toplevel(self.root)
        win.title("Bar Chart")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

def main():
    root = tk.Tk()
    app = DiskAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

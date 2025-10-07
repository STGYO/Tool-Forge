
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import threading

UNDO_LOG = []

def scan_files(directory, nested=True):
    files = []
    for root, dirs, filenames in os.walk(directory):
        for f in filenames:
            files.append(os.path.join(root, f))
        if not nested:
            break
    return files

def get_type_folder(filename):
    ext = os.path.splitext(filename)[1].lstrip('.').lower()
    if not ext:
        return "No_Extension"
    elif ext in ['txt', 'doc', 'docx', 'pdf', 'odt']:
        return "Documents"
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']:
        return "Images"
    elif ext in ['mp4', 'mkv', 'avi', 'mov', 'wmv']:
        return "Videos"
    elif ext in ['mp3', 'wav', 'flac', 'aac']:
        return "Audio"
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
        return "Archives"
    elif ext in ['exe', 'msi', 'dmg', 'deb', 'rpm']:
        return "Executables"
    elif ext in ['py', 'js', 'html', 'css', 'java', 'c', 'cpp']:
        return "Code"
    else:
        return "Others"

def get_date_folder(filepath):
    ts = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(ts)
    return dt.strftime('%Y/%m')

def preview_sort(files, method, base_dir):
    preview = []
    for f in files:
        if method == 'type':
            folder = get_type_folder(f)
        else:
            folder = get_date_folder(f)
        dest = os.path.join(base_dir, folder, os.path.basename(f))
        preview.append((f, dest))
    return preview

def do_sort(preview, collision_mode):
    undo = []
    for src, dest in preview:
        if os.path.exists(dest):
            if collision_mode == 'skip':
                continue
            elif collision_mode == 'rename':
                base, ext = os.path.splitext(dest)
                i = 1
                while os.path.exists(f"{base}_{i}{ext}"):
                    i += 1
                dest = f"{base}_{i}{ext}"
            elif collision_mode == 'overwrite':
                os.remove(dest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
        undo.append((dest, src))
    UNDO_LOG.clear()
    UNDO_LOG.extend(undo)

def undo_sort():
    for src, dest in reversed(UNDO_LOG):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
    UNDO_LOG.clear()

class SortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeSort - File Organizer")
        self.dir = os.path.expanduser("~")
        self.method = tk.StringVar(value='type')
        self.collision = tk.StringVar(value='rename')
        self.nested = tk.BooleanVar(value=True)
        self.files = []
        self.preview = []

        dir_frame = ttk.Frame(root)
        dir_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(dir_frame, text="Target Folder:").pack(side="left")
        self.dir_label = ttk.Label(dir_frame, text=self.dir)
        self.dir_label.pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.choose_dir).pack(side="right")

        opt_frame = ttk.Frame(root)
        opt_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(opt_frame, text="Sort by:").pack(side="left")
        ttk.Radiobutton(opt_frame, text="Type", variable=self.method, value='type').pack(side="left")
        ttk.Radiobutton(opt_frame, text="Date", variable=self.method, value='date').pack(side="left")
        ttk.Checkbutton(opt_frame, text="Include subfolders", variable=self.nested).pack(side="left")
        ttk.Label(opt_frame, text="On collision:").pack(side="left")
        ttk.Combobox(opt_frame, textvariable=self.collision, values=['rename','skip','overwrite'], width=10).pack(side="left")

        ttk.Button(root, text="Preview", command=self.preview_action).pack(fill="x", padx=5, pady=2)
        ttk.Button(root, text="Sort!", command=self.sort_action).pack(fill="x", padx=5, pady=2)
        ttk.Button(root, text="Undo", command=self.undo_action).pack(fill="x", padx=5, pady=2)

        self.tree = ttk.Treeview(root, columns=("from","to"), show="headings", height=15)
        self.tree.heading("from", text="From")
        self.tree.heading("to", text="To")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status).pack(fill="x", padx=5, pady=2)

    def choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir)
        if d:
            self.dir = d
            self.dir_label.config(text=self.dir)

    def preview_action(self):
        self.files = scan_files(self.dir, self.nested.get())
        self.preview = preview_sort(self.files, self.method.get(), self.dir)
        self.tree.delete(*self.tree.get_children())
        for src, dest in self.preview:
            self.tree.insert("", "end", values=(src, dest))
        self.status.set(f"Preview: {len(self.preview)} files will be moved.")

    def sort_action(self):
        if not self.preview:
            self.status.set("Nothing to sort. Run preview first.")
            return
        try:
            do_sort(self.preview, self.collision.get())
            self.status.set(f"Sorted {len(self.preview)} files.")
            self.preview = []
            self.tree.delete(*self.tree.get_children())
        except Exception as e:
            messagebox.showerror("Sort Error", str(e))

    def undo_action(self):
        if not UNDO_LOG:
            self.status.set("Nothing to undo.")
            return
        try:
            undo_sort()
            self.status.set("Undo complete.")
        except Exception as e:
            messagebox.showerror("Undo Error", str(e))

def main():
    root = tk.Tk()
    app = SortApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

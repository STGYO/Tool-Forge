
# ForgeDrop: Local Wi-Fi File Drop Tool
import os
import sys
import threading
import socket
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

CHUNK_SIZE = 1024 * 1024  # 1MB
PORT = 50001
SERVICE_TYPE = "_forgedrop._tcp.local."
SERVICE_NAME = f"ForgeDrop-{socket.gethostname()}._forgedrop._tcp.local."

class PeerDiscovery:
    def __init__(self, on_update):
        self.zeroconf = Zeroconf()
        self.on_update = on_update
        self.peers = {}
        self.browser = ServiceBrowser(self.zeroconf, SERVICE_TYPE, self)

    def remove_service(self, zc, type, name):
        if name in self.peers:
            del self.peers[name]
            self.on_update(list(self.peers.values()))

    def add_service(self, zc, type, name):
        info = zc.get_service_info(type, name)
        if info and name != SERVICE_NAME:
            addr = socket.inet_ntoa(info.addresses[0])
            self.peers[name] = (addr, info.port)
            self.on_update(list(self.peers.values()))

    def close(self):
        self.zeroconf.close()

def start_server(save_dir, ask_confirm):
    def handle_client(conn, addr):
        try:
            meta_len = int.from_bytes(conn.recv(4), 'big')
            meta = conn.recv(meta_len).decode('utf-8')
            filename, filesize = meta.split(':')
            filesize = int(filesize)
            if ask_confirm(filename, filesize, addr):
                with open(os.path.join(save_dir, filename), 'wb') as f:
                    received = 0
                    while received < filesize:
                        chunk = conn.recv(min(CHUNK_SIZE, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                conn.sendall(b'OK')
            else:
                conn.sendall(b'NO')
        except Exception as e:
            pass
        finally:
            conn.close()

    def server():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    threading.Thread(target=server, daemon=True).start()

def send_file(peer_addr, peer_port, filepath):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer_addr, peer_port))
    meta = f"{filename}:{filesize}".encode('utf-8')
    s.sendall(len(meta).to_bytes(4, 'big'))
    s.sendall(meta)
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            s.sendall(chunk)
    resp = s.recv(2)
    s.close()
    return resp == b'OK'

class ForgeDropApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeDrop - Local File Drop")
        self.save_dir = os.path.expanduser("~")
        self.peers = []
        self.selected_peer = None

        # Register Zeroconf service
        self.zeroconf = Zeroconf()
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        self.info = ServiceInfo(
            SERVICE_TYPE,
            SERVICE_NAME,
            addresses=[socket.inet_aton(ip)],
            port=PORT,
            properties={},
            server=f"{hostname}.local."
        )
        self.zeroconf.register_service(self.info)

        # Peer discovery
        self.discovery = PeerDiscovery(self.update_peers)

        # Start server
        start_server(self.save_dir, self.ask_confirm)

        # UI
        peer_frame = ttk.Frame(root)
        peer_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(peer_frame, text="Peers:").pack(side="left")
        self.peer_list = ttk.Combobox(peer_frame, state="readonly")
        self.peer_list.pack(side="left", fill="x", expand=True)
        self.peer_list.bind('<<ComboboxSelected>>', self.select_peer)

        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(btn_frame, text="Choose Save Folder", command=self.choose_folder).pack(side="left")
        ttk.Button(btn_frame, text="Send File(s)", command=self.send_files).pack(side="left")

        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status).pack(fill="x", padx=5, pady=5)

        # Drag and drop support (Tkinter native is limited, so use file dialog)
        ttk.Button(root, text="Send File(s) (Browse)", command=self.send_files).pack(fill="x", padx=5, pady=5)

    def update_peers(self, peers):
        self.peers = peers
        self.peer_list['values'] = [f"{addr}:{port}" for addr, port in peers]
        if peers:
            self.peer_list.current(0)
            self.selected_peer = peers[0]
        else:
            self.selected_peer = None

    def select_peer(self, event=None):
        idx = self.peer_list.current()
        if 0 <= idx < len(self.peers):
            self.selected_peer = self.peers[idx]

    def choose_folder(self):
        d = filedialog.askdirectory(initialdir=self.save_dir)
        if d:
            self.save_dir = d
            self.status.set(f"Save folder set to: {self.save_dir}")

    def ask_confirm(self, filename, filesize, addr):
        resp = messagebox.askyesno("Incoming File", f"Receive file '{filename}' ({filesize/1024/1024:.2f} MB) from {addr[0]}?")
        return resp

    def send_files(self):
        if not self.selected_peer:
            messagebox.showinfo("No Peer", "No peer selected.")
            return
        files = filedialog.askopenfilenames()
        if not files:
            return
        addr, port = self.selected_peer
        for f in files:
            self.status.set(f"Sending {os.path.basename(f)}...")
            ok = send_file(addr, port, f)
            if ok:
                self.status.set(f"Sent {os.path.basename(f)} successfully.")
            else:
                self.status.set(f"Failed to send {os.path.basename(f)}.")

def main():
    root = tk.Tk()
    app = ForgeDropApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

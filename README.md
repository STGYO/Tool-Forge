[![Built with AI](https://img.shields.io/badge/Built%20with-AI-blueviolet?style=for-the-badge&logo=openai&logoColor=white)](#acknowledgements)
# 🛠️ ToolForge

**Your Personal Utility Arsenal**  
A handcrafted suite of essential tools built for general PC users — simple, lightweight, offline-first, and incredibly useful.

---

## 🔍 What is ToolForge?

**ToolForge** is a collection of mini desktop utilities that solve everyday PC problems — built from scratch with privacy, performance, and productivity in mind. No bloat. No background surveillance. Just tools that work.

Whether you're organizing files, tracking time, cleaning disk space, or just managing passwords locally, ToolForge has your back.

---

## 🚀 Tools Included (Work in Progress)

| Tool          | Description                                                                 | Version  |
|---------------|-----------------------------------------------------------------------------|----------|
| **ForgeClip**   | Smart clipboard manager that stores history, lets you search and reuse past clipboard entries. | 25.1.0   |
| **ForgeRename** | Bulk file renamer with pattern, regex, and preview support.                | 25.1.1   |
| **ForgeClean**  | Disk analyzer and cleanup assistant with visual folder size breakdown.     | 25.1.1   |
| **ForgeTrack**  | App usage tracker that logs active window time and summarizes productivity. | 25.1.1   |
| **ForgeVault**  | Offline password vault with strong encryption and backup features.         | 25.1.1   |
| **ForgeSort**   | Auto-folder organizer that cleans your Desktop/Downloads by file type/date.| 25.1.1   |
| **ForgeRemind** | Local reminder tool with popup notifications and recurring schedule support.| 25.1.1  |
| **ForgeDrop**   | Local Wi-Fi file transfer tool with drag & drop simplicity.                | 25.1.1   |
| **ForgeSpeed**  | Internet speed logger that tracks performance over time and alerts on slowdowns.| 25.1.1 |
| **ForgeLaunch** | Portable app launcher with custom icons, tags, and search.                 | 25.1.1   |
| **ForgeSpec**   | One-click system info snapshot generator (CPU, RAM, OS, GPU, etc.).        | 25.1.1   |

Each tool is:
- Fully **offline**
- **Open-source**
- **Easy to use** and extend

---

## 🧰 Getting Started

To run any tool:

1. Make sure you have Python 3.8+ installed
2. Navigate into the tool's folder:
   ```bash
   cd forgeclip
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the tool:
   ```bash
   python main.py
   ```

> Repeat the same for any other tool in `/ToolForge/`.

---

## 🛠️ Built With

- **Python** (Tkinter, PyQt, Flask, Watchdog, etc.)
- **Electron.js** (for GUI tools if cross-platform is needed)
- **SQLite** and **JSON** for fast, local storage
- Targeting **Windows first**, with future Linux/macOS support planned

---

## 📦 Installation & Usage

> ⚠️ Coming soon: prebuilt installers and detailed docs for each tool

For now, clone the repo and run tools individually:

```bash
git clone https://github.com/yourusername/ToolForge.git
cd ToolForge/forgeclip
python main.py
```

Dependencies will be listed in each tool’s `requirements.txt`.

---

## 🧾 Versioning

ToolForge uses **semantic, time-based versioning**:

```
<YY>.<MX>.<P>
```

- `YY` – Year (`25` for 2025)
- `MX` – Major milestone (new feature sets or UI changes)
- `P`  – Patch number (fixes, improvements)

See `VERSION.md` for full version history and roadmap.

---

Have ideas? Open an issue or start a discussion!

---

## 🤝 Contributing

We welcome contributors and tool builders!

- Found a bug? Open an issue
- Want to add a new tool? Fork the repo and submit a PR
- Follow the structure of existing tools like `forgeclip/`
- Use the standard versioning format (`YY.MX.P`)
- Keep tools modular and self-contained

---

## 🧩 Folder Structure

```
ToolForge/
├── VERSION.md            # Global version tracking
├── read_versions.py      # CLI version reporter
├── forgeclip/
│   ├── VERSION.txt
│   ├── main.py
│   ├── requirements.txt
│   ├── README.md
│   └── ...
├── forgeclean/
│   └── ...
└── ...
```

---

## 📜 License

This project is licensed under the **MIT License** — free to use, improve, and distribute.

See the `LICENSE` file for full terms.


---

## 🤖 Acknowledgements

This project was crafted with the help of AI tools like **OpenAI**, **Cursor**, and other code accelerators.  
While the code was generated collaboratively, every decision, structure, and final implementation was guided by human understanding and intentional design.

ToolForge is both a personal learning journey and a showcase of how AI can empower independent development.

---

> ✨ *“Tools that do one thing well — and respect your time, space, and data.”*

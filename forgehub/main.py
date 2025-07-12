import tkinter as tk
from tkinter import ttk
import os
import subprocess

class ForgeHub:
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeHub")

        self.tools_frame = ttk.Frame(root, padding="10")
        self.tools_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.tools_frame)
        self.scrollbar = ttk.Scrollbar(self.tools_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.tools = self.load_tools()
        self.render_ui()

    def load_tools(self):
        """Detect sub-tools and read their info."""
        tools_list = []
        # Assuming tool folders are siblings to forgehub
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        forgehub_dir_name = os.path.basename(os.path.dirname(__file__))

        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            # Check if it's a directory and not forgehub itself
            if os.path.isdir(item_path) and item != forgehub_dir_name:
                tool_info = self.get_tool_info(item_path, item)
                if tool_info:
                    tools_list.append(tool_info)
        return tools_list

    def get_tool_info(self, tool_path, tool_name):
        """Read VERSION.txt and README.md for a tool."""
        version = "N/A"
        description = "No description available."
        version_file = os.path.join(tool_path, "VERSION.txt")
        readme_file = os.path.join(tool_path, "README.md")

        if os.path.exists(version_file):
            try:
                with open(version_file, "r") as f:
                    version = f.read().strip()
            except Exception as e:
                print(f"Error reading {version_file}: {e}")

        if os.path.exists(readme_file):
            try:
                with open(readme_file, "r") as f:
                    # Read only the first few lines for a short description
                    lines = f.readlines()
                    description = "".join(lines[:3]).strip() + "..." if len(lines) > 3 else "".join(lines).strip()
            except Exception as e:
                print(f"Error reading {readme_file}: {e}")

        # Check if main.py or .exe exists
        main_py = os.path.join(tool_path, "main.py")
        tool_exe = os.path.join(tool_path, f"{tool_name}.exe")
        executable_exists = os.path.exists(main_py) or os.path.exists(tool_exe)

        if executable_exists:
            return {
                "name": tool_name,
                "version": version,
                "description": description,
                "path": tool_path,
                "main_py": main_py,
                "tool_exe": tool_exe
            }
        return None

    def render_ui(self):
        """Display tool info and launch buttons."""
        for tool in self.tools:
            tool_frame = ttk.LabelFrame(self.scrollable_frame, text=tool["name"], padding="10")
            tool_frame.pack(fill="x", padx=5, pady=5)

            version_label = ttk.Label(tool_frame, text=f"Version: {tool['version']}")
            version_label.pack(anchor="w")

            description_label = ttk.Label(tool_frame, text=f"Description: {tool['description']}", wraplength=400)
            description_label.pack(anchor="w")

            launch_button = ttk.Button(tool_frame, text="Launch", command=lambda t=tool: self.launch_tool(t))
            launch_button.pack(anchor="e")

    def launch_tool(self, tool):
        """Launch the selected tool in a separate process."""
        executable_path = tool["tool_exe"] if os.path.exists(tool["tool_exe"]) else tool["main_py"]

        if os.path.exists(executable_path):
            try:
                # Use subprocess.Popen to run in a separate process
                if executable_path.endswith(".py"):
                    # Assuming python is in the PATH
                    subprocess.Popen(["python", executable_path], cwd=tool["path"])
                else:
                    subprocess.Popen([executable_path], cwd=tool["path"])
                print(f"Launched {tool['name']}")
            except Exception as e:
                print(f"Error launching {tool['name']}: {e}")
        else:
            print(f"Executable not found for {tool['name']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ForgeHub(root)
    root.mainloop()
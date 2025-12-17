import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


class ParkingInterface(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        # App basics
        self.master.title("Parking Space Detection")
        self.master.resizable(False, False)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_py = os.path.join(self.base_dir, "src", "main.py")

        # Vars
        self.mode_var = tk.StringVar(value="generate")
        self.start_frame_var = tk.StringVar(value="1")

        self._setup_theme()
        self._create_layout()
        self._prefill_defaults()

        # React to mode changes (only UI behavior; logic stays same)
        self.mode_var.trace_add("write", lambda *_: self._on_mode_change())
        self._on_mode_change()

    def _setup_theme(self):
        # Use a modern built-in theme if available
        style = ttk.Style(self.master)
        preferred = ["vista", "xpnative", "clam"]
        for t in preferred:
            if t in style.theme_names():
                style.theme_use(t)
                break

        # Premium white look
        self.bg = "#FFFFFF"
        self.card = "#FFFFFF"
        self.border = "#D9D9D9"
        self.text = "#111827"
        self.muted = "#6B7280"
        self.accent = "#2563EB"  # subtle blue accent
        self.btn_bg = "#111827"
        self.btn_fg = "#FFFFFF"

        self.master.configure(bg=self.bg)

        style.configure(".", font=("Segoe UI", 10))
        style.configure("App.TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.card)
        style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 14, "bold"))
        style.configure("Sub.TLabel", background=self.bg, foreground=self.muted, font=("Segoe UI", 10))
        style.configure("Field.TLabel", background=self.card, foreground=self.text, font=("Segoe UI", 10))
        style.configure("Hint.TLabel", background=self.card, foreground=self.muted, font=("Segoe UI", 9))

        style.configure(
            "Card.TLabelframe",
            background=self.card,
            bordercolor=self.border,
            relief="solid"
        )
        style.configure("Card.TLabelframe.Label", background=self.card, foreground=self.text, font=("Segoe UI", 10, "bold"))

        style.configure("TEntry", padding=6)
        style.configure("TButton", padding=(10, 7))
        style.configure("Primary.TButton", padding=(10, 7))
        style.map(
            "Primary.TButton",
            background=[("active", self.btn_bg), ("!disabled", self.btn_bg)],
            foreground=[("active", self.btn_fg), ("!disabled", self.btn_fg)]
        )
        style.configure("Primary.TButton", background=self.btn_bg, foreground=self.btn_fg)

        style.map(
            "TButton",
            background=[("active", "#F3F4F6")]
        )

    def _create_layout(self):
        outer = ttk.Frame(self.master, style="App.TFrame", padding=14)
        outer.grid(row=0, column=0)
        outer.columnconfigure(0, weight=1)

        # Header
        header = ttk.Frame(outer, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="Parking Space Detection", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Generate coordinates or run detection (OpenCV window will open)",
            style="Sub.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Card container
        card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        card.grid(row=1, column=0, sticky="ew")
        card.columnconfigure(1, weight=1)

        # Mode section
        mode_box = ttk.Labelframe(card, text="Mode", style="Card.TLabelframe", padding=10)
        mode_box.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        mode_box.columnconfigure(0, weight=1)

        ttk.Radiobutton(
            mode_box,
            text="Generate Parking Coordinates (draw slots with mouse)",
            variable=self.mode_var, value="generate"
        ).grid(row=0, column=0, sticky="w", pady=2)

        ttk.Radiobutton(
            mode_box,
            text="Run Parking Detection",
            variable=self.mode_var, value="detect"
        ).grid(row=1, column=0, sticky="w", pady=2)

        # Fields
        self.image_entry = ttk.Entry(card, width=62)
        self.video_entry = ttk.Entry(card, width=62)
        self.data_entry = ttk.Entry(card, width=62)

        # Image
        ttk.Label(card, text="Image file (.png/.jpg)", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.image_entry.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(card, text="Browse", command=self._browse_image).grid(row=2, column=2, padx=(10, 0))
        self.image_hint = ttk.Label(card, text="", style="Hint.TLabel")
        self.image_hint.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 10))

        # Video
        ttk.Label(card, text="Video file (.mp4)", style="Field.TLabel").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.video_entry.grid(row=5, column=0, columnspan=2, sticky="ew")
        ttk.Button(card, text="Browse", command=self._browse_video).grid(row=5, column=2, padx=(10, 0))
        ttk.Label(card, text="Required for both modes.", style="Hint.TLabel").grid(row=6, column=0, columnspan=3, sticky="w", pady=(4, 10))

        # Data
        ttk.Label(card, text="Coordinates data file (.yml)", style="Field.TLabel").grid(row=7, column=0, sticky="w", pady=(0, 4))
        self.data_entry.grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Button(card, text="Browse", command=self._browse_data).grid(row=8, column=2, padx=(10, 0))
        self.data_hint = ttk.Label(card, text="", style="Hint.TLabel")
        self.data_hint.grid(row=9, column=0, columnspan=3, sticky="w", pady=(4, 10))

        # Start frame
        sf_row = ttk.Frame(card, style="Card.TFrame")
        sf_row.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        ttk.Label(sf_row, text="Start frame", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        sf_entry = ttk.Entry(sf_row, width=12, textvariable=self.start_frame_var)
        sf_entry.grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(sf_row, text="(positive integer)", style="Hint.TLabel").grid(row=0, column=2, sticky="w", padx=(8, 0))

        # Buttons
        btns = ttk.Frame(card, style="Card.TFrame")
        btns.grid(row=11, column=0, columnspan=3, sticky="e")
        ttk.Button(btns, text="Quit", command=self.master.destroy).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(btns, text="Run", command=self._run).grid(row=0, column=1)


    def _on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "generate":
            self.image_entry.state(["!disabled"])
            self.image_hint.config(text="Used to draw 4 corners per parking slot. Press 'q' when finished.")
            self.data_hint.config(text="This will be SAVED to the path you choose.")
        else:
            # Image is optional in detect mode (keep same behavior: only required for generate)
            self.image_entry.state(["disabled"])
            self.image_hint.config(text="Not required in detection mode.")
            self.data_hint.config(text="Select an EXISTING .yml file generated earlier.")

    def _prefill_defaults(self):
        img_default = os.path.join(self.base_dir, "src", "assets", "images", "parking_lot_1.png")
        vid_default = os.path.join(self.base_dir, "src", "assets", "videos", "parking_lot_1.mp4")
        data_default = os.path.join(self.base_dir, "src", "assets", "data", "coordinates_1.yml")

        if os.path.exists(img_default):
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, img_default)
        if os.path.exists(vid_default):
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, vid_default)

        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, data_default)

    def _browse_image(self):
        filename = filedialog.askopenfilename(
            title="Select parking lot image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        if filename:
            self.image_entry.state(["!disabled"])
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)
            if self.mode_var.get() == "detect":
                self.image_entry.state(["disabled"])

    def _browse_video(self):
        filename = filedialog.askopenfilename(
            title="Select parking lot video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        if filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, filename)

    def _browse_data(self):
        if self.mode_var.get() == "generate":
            filename = filedialog.asksaveasfilename(
                title="Where to save coordinates .yml file",
                defaultextension=".yml",
                filetypes=[("YAML files", "*.yml"), ("All files", "*.*")]
            )
        else:
            filename = filedialog.askopenfilename(
                title="Select existing coordinates .yml file",
                filetypes=[("YAML files", "*.yml"), ("All files", "*.*")]
            )

        if filename:
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, filename)

    def _run(self):
        if not os.path.exists(self.main_py):
            messagebox.showerror(
                "Error",
                f"Could not find main.py at:\n{self.main_py}\n\n"
                "Make sure you place this interface.py file in the project root\n"
                "next to the src/ folder."
            )
            return

        image_file = self.image_entry.get().strip()
        data_file = self.data_entry.get().strip()
        video_file = self.video_entry.get().strip()
        start_frame = self.start_frame_var.get().strip()
        mode = self.mode_var.get()

        # Validate required fields (same logic as your original)
        if not data_file:
            messagebox.showerror("Missing field", "Please select a data (.yml) file.")
            return

        if not video_file:
            messagebox.showerror("Missing field", "Please select a video file.")
            return

        if mode == "generate":
            if not image_file:
                messagebox.showerror("Missing field", "Please select an image file for coordinate generation.")
                return

        if not start_frame.isdigit() or int(start_frame) < 1:
            messagebox.showerror("Invalid field", "Start frame must be a positive integer.")
            return

        # Build the command line (same structure as your original)
        cmd = [sys.executable, self.main_py, "--data", data_file, "--video", video_file, "--start-frame", start_frame]

        if mode == "generate":
            cmd.insert(3, "--image")
            cmd.insert(4, image_file)

        try:
            subprocess.Popen(cmd)
            if mode == "generate":
                msg = (
                    "Coordinate generation has started.\n\n"
                    "An OpenCV window should open:\n"
                    "  - Click the 4 corners of each parking space.\n"
                    "  - Press 'q' when you're done.\n\n"
                    f"Coordinates will be saved to:\n{data_file}"
                )
            else:
                msg = (
                    "Parking detection has started.\n\n"
                    "An OpenCV video window should open showing the parking lot\n"
                    "with GREEN (free) and RED (occupied) boxes."
                )
            messagebox.showinfo("Running", msg)
        except Exception as exc:
            messagebox.showerror(
                "Error running script",
                f"Command failed:\n{' '.join(cmd)}\n\nError:\n{exc}"
            )


def main():
    root = tk.Tk()
    ParkingInterface(master=root)
    root.mainloop()


if __name__ == "__main__":
    main()

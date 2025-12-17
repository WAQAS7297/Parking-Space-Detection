import argparse
import logging
import sys
from typing import Optional

import yaml
from coordinates_generator import CoordinatesGenerator
from motion_detector import MotionDetector
from colors import COLOR_RED

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure basic logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# =========================
#  CORE ORIGINAL LOGIC
# =========================

def run(
    image_file: Optional[str],
    video_file: str,
    data_file: str,
    start_frame: int,
) -> None:
    """
    Core workflow.

    Preserves original behavior:
    1) If image_file is provided -> generate coordinates into data_file
    2) Always -> load YAML and run motion detection
    """
    logger.info(
        "Running with image=%s, video=%s, data=%s, start_frame=%s",
        image_file,
        video_file,
        data_file,
        start_frame,
    )

    if image_file is not None:
        logger.info("Image file provided, generating coordinates...")
        with open(data_file, "w+") as points_file:
            generator = CoordinatesGenerator(image_file, points_file, COLOR_RED)
            generator.generate()
        logger.info("Coordinates written to %s", data_file)

    logger.info("Loading coordinates from %s", data_file)
    with open(data_file, "r") as data:
        points = yaml.load(data, Loader=yaml.FullLoader)

    logger.info("Starting motion detection...")
    detector = MotionDetector(video_file, points, int(start_frame))
    detector.detect_motion()
    logger.info("Motion detection finished.")


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments (unchanged).
    """
    parser = argparse.ArgumentParser(description="Generates Coordinates File")

    parser.add_argument(
        "--image",
        dest="image_file",
        required=False,
        help="Image file to generate coordinates on",
    )

    parser.add_argument(
        "--video",
        dest="video_file",
        required=True,
        help="Video file to detect motion on",
    )

    parser.add_argument(
        "--data",
        dest="data_file",
        required=True,
        help="Data file to be used with OpenCV",
    )

    parser.add_argument(
        "--start-frame",
        dest="start_frame",
        required=False,
        default=1,
        help="Starting frame on the video",
    )

    return parser.parse_args()


def main_cli() -> None:
    """Run using the original CLI style."""
    configure_logging()
    args = parse_args()
    run(
        image_file=args.image_file,
        video_file=args.video_file,
        data_file=args.data_file,
        start_frame=int(args.start_frame),
    )


# =========================
#         GUI PART
# =========================

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Parking Space Detection")
        self.resizable(False, False)

        self._setup_theme()
        self._build_ui()

    def _setup_theme(self) -> None:
        
        style = ttk.Style(self)

        preferred = ["vista", "xpnative", "clam"]
        for t in preferred:
            if t in style.theme_names():
                style.theme_use(t)
                break

        # Premium white palette
        self.bg = "#FFFFFF"
        self.card = "#FFFFFF"
        self.border = "#D9D9D9"
        self.text = "#111827"
        self.muted = "#6B7280"

        self.configure(bg=self.bg)

        style.configure(".", font=("Segoe UI", 10))
        style.configure("App.TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.card)
        style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 14, "bold"))
        style.configure("Sub.TLabel", background=self.bg, foreground=self.muted, font=("Segoe UI", 10))
        style.configure("Field.TLabel", background=self.card, foreground=self.text, font=("Segoe UI", 10))
        style.configure("Hint.TLabel", background=self.card, foreground=self.muted, font=("Segoe UI", 9))

        style.configure("TEntry", padding=6)
        style.configure("TButton", padding=(10, 7))
        style.map("TButton", background=[("active", "#F3F4F6")])

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, style="App.TFrame", padding=14)
        outer.grid(row=0, column=0)
        outer.columnconfigure(0, weight=1)

        # Header
        header = ttk.Frame(outer, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="Parking Space Detection", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Provide optional image to regenerate coordinates, then run detection on video.",
            style="Sub.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Card
        card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        card.grid(row=1, column=0, sticky="ew")
        card.columnconfigure(0, weight=1)

        # Image row
        ttk.Label(card, text="Image File (optional)", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
        row_img = ttk.Frame(card, style="Card.TFrame")
        row_img.grid(row=1, column=0, sticky="ew")
        row_img.columnconfigure(0, weight=1)

        self.image_entry = ttk.Entry(row_img, width=68)
        self.image_entry.grid(row=0, column=0, sticky="ew")
        ttk.Button(row_img, text="Browse", command=self.browse_image).grid(row=0, column=1, padx=(10, 0))

        ttk.Label(
            card,
            text="Leave empty if you already have coordinates in the YAML file.",
            style="Hint.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=(4, 10))

        # Video row
        ttk.Label(card, text="Video File", style="Field.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 4))
        row_vid = ttk.Frame(card, style="Card.TFrame")
        row_vid.grid(row=4, column=0, sticky="ew")
        row_vid.columnconfigure(0, weight=1)

        self.video_entry = ttk.Entry(row_vid, width=68)
        self.video_entry.grid(row=0, column=0, sticky="ew")
        ttk.Button(row_vid, text="Browse", command=self.browse_video).grid(row=0, column=1, padx=(10, 0))

        ttk.Label(card, text="Required.", style="Hint.TLabel").grid(row=5, column=0, sticky="w", pady=(4, 10))

        # Data row
        ttk.Label(card, text="Data File (YAML)", style="Field.TLabel").grid(row=6, column=0, sticky="w", pady=(0, 4))
        row_data = ttk.Frame(card, style="Card.TFrame")
        row_data.grid(row=7, column=0, sticky="ew")
        row_data.columnconfigure(0, weight=1)

        self.data_entry = ttk.Entry(row_data, width=68)
        self.data_entry.grid(row=0, column=0, sticky="ew")
        ttk.Button(row_data, text="Browse", command=self.browse_data).grid(row=0, column=1, padx=(10, 0))

        ttk.Label(
            card,
            text="If image is provided, coordinates will be regenerated into this file.",
            style="Hint.TLabel"
        ).grid(row=8, column=0, sticky="w", pady=(4, 10))

        # Start frame row
        sf = ttk.Frame(card, style="Card.TFrame")
        sf.grid(row=9, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(sf, text="Start Frame", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        self.start_frame_entry = ttk.Entry(sf, width=12)
        self.start_frame_entry.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.start_frame_entry.insert(0, "1")
        ttk.Label(sf, text="(positive integer)", style="Hint.TLabel").grid(row=0, column=2, sticky="w", padx=(8, 0))

        # Buttons (Run aligned with others: default TButton style)
        btns = ttk.Frame(card, style="Card.TFrame")
        btns.grid(row=10, column=0, sticky="e")
        ttk.Button(btns, text="Quit", command=self.destroy).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(btns, text="Run Detection", command=self.on_run).grid(row=0, column=1)

    def browse_image(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All Files", "*.*")],
        )
        if filename:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)

    def browse_video(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")],
        )
        if filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, filename)

    def browse_data(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select YAML Data File (or create new)",
            filetypes=[("YAML Files", "*.yml *.yaml"), ("All Files", "*.*")],
        )
        if filename:
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, filename)

    def on_run(self) -> None:
        image_file = self.image_entry.get().strip() or None
        video_file = self.video_entry.get().strip()
        data_file = self.data_entry.get().strip()
        start_frame_str = self.start_frame_entry.get().strip() or "1"

        if not video_file:
            messagebox.showerror("Error", "Video file is required.")
            return

        if not data_file:
            messagebox.showerror("Error", "Data (YAML) file is required.")
            return

        try:
            start_frame = int(start_frame_str)
        except ValueError:
            messagebox.showerror("Error", "Start frame must be an integer.")
            return

        try:
            configure_logging()
            run(
                image_file=image_file,
                video_file=video_file,
                data_file=data_file,
                start_frame=start_frame,
            )
        except Exception as e:
            logger.exception("Error during execution")
            messagebox.showerror("Execution Error", str(e))


# =========================
#      ENTRY POINT
# =========================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_cli()
    else:
        app = App()
        app.mainloop()

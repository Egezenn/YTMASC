import json
import logging
from logging import Handler
from pathlib import Path
import shutil
import sys
import threading
from typing import Any, Dict


# Constants
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(".")
    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()

DATA_DIR = BASE_DIR / "data"
WORKING_DIR = DATA_DIR / "downloads"
LOG_DIR = DATA_DIR / "logs"
LIBRARY_FILE = DATA_DIR / "library.json"

AUDIO_EXTENSIONS = [".opus", ".webm", ".m4a", ".mp3"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
CONVERTIBLE_AUDIO_EXTENSIONS = [".webm", ".m4a"]
CONVERTIBLE_IMAGE_EXTENSIONS = [".webp", ".png"]

# Ensure directories exist
# TODO: decide if they should exist
DATA_DIR.mkdir(exist_ok=True)
WORKING_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


# Thread-local storage for worker configuration
worker_config = threading.local()


def init_worker(worker_id: int, padding: int):
    """Initializes worker configuration for logging."""
    worker_config.log_file = LOG_DIR / f"log_{str(worker_id).zfill(padding)}.log"


class ThreadFileHandler(Handler):
    """
    A logging handler that writes to a thread-local log file if configured,
    otherwise falls back to the main log file.
    """

    def __init__(self, main_log_path: Path = None):
        super().__init__()
        self.main_log_path = main_log_path or (LOG_DIR / "logs.log")

    def emit(self, record):
        try:
            msg = self.format(record)
            log_file = getattr(worker_config, "log_file", None)

            if log_file:
                # Write to worker-specific log file
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            else:
                # Write to main log file
                with open(self.main_log_path, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
        except Exception:
            self.handleError(record)


def setup_logging(verbosity: str = "INFO"):
    """Sets up logging configuration."""
    # Clean up old logs
    if LOG_DIR.exists():
        for log_file in LOG_DIR.glob("*.log"):
            try:
                log_file.unlink()
            except Exception:
                pass

    level = getattr(logging, verbosity.upper(), logging.INFO)

    # Remove existing handlers to avoid duplication if called multiple times
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s - %(levelname)s - %(message)s",
        handlers=[
            ThreadFileHandler(),
            logging.StreamHandler(),
        ],
    )


def check_dependencies():
    """Check if required external dependencies are available."""
    missing = []

    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")

    if not (shutil.which("magick") or shutil.which("convert")):
        missing.append("magick (or convert)")

    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")

    if missing:
        print(f"ERROR: Required dependencies not found: {', '.join(missing)}")
        print("Please install the missing dependencies and ensure they are in your PATH.")
        sys.exit(1)


def read_json(path: Path) -> Dict[str, Any]:
    """Reads a JSON file and returns a dictionary."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data: Dict[str, Any]):
    """Writes a dictionary to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_safe_filename(text: str) -> str:
    """Sanitizes a string to be used as a filename."""
    return "".join([c for c in text if c.isalpha() or c.isdigit() or c in " .-_"]).strip()


def parse_extras(extras_str: str) -> list[str]:
    """Parses a comma-separated string of extras."""
    if not extras_str:
        return []
    return [x.strip() for x in extras_str.split(",") if x.strip()]

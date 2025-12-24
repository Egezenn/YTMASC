import logging
from pathlib import Path
import subprocess

from . import utils

logger = logging.getLogger(__name__)


class Converter:
    def __init__(self, working_dir: Path = utils.WORKING_DIR):
        self.working_dir = working_dir

    def convert_audio(self, watch_id: str, target_format: str = "opus", keep_source: bool = False) -> bool:
        """
        Converts the downloaded audio file to the target format.
        Supported formats: 'opus', 'mp3'.
        """
        source_file = None
        # Only look for convertible formats as per user request
        for ext in utils.CONVERTIBLE_AUDIO_EXTENSIONS:
            path = self.working_dir / f"{watch_id}{ext}"
            if path.exists():
                source_file = path
                break

        if not source_file:
            # Check if we already have the target file
            if (self.working_dir / f"{watch_id}.{target_format}").exists():
                return True

            logger.error(
                f"No source file found for {watch_id} (checked convertible formats: {utils.CONVERTIBLE_AUDIO_EXTENSIONS})"
            )
            return False

        output_file = self.working_dir / f"{watch_id}.{target_format}"

        if output_file.exists():
            # If output already exists and is different from source, we might want to skip or overwrite.
            if source_file == output_file:
                return True
            return True

        command = ["ffmpeg", "-i", str(source_file)]

        if target_format == "opus":
            # If source is webm (which usually contains opus), copy the stream.
            if source_file.suffix == ".webm":
                command.extend(["-c:a", "copy"])
            else:
                # Re-encode for other formats (e.g. m4a)
                command.extend(["-c:a", "libopus", "-b:a", "128k"])
        elif target_format == "mp3":
            command.extend(["-acodec", "libmp3lame", "-b:a", "192k"])
        else:
            logger.error(f"Unsupported format: {target_format}")
            return False

        command.extend(["-loglevel", "error", "-y", str(output_file)])

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Converted {watch_id} to {target_format}")
            # Remove source if different
            if not keep_source and source_file != output_file:
                try:
                    source_file.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete source file {source_file}: {e}")
            return True
        else:
            logger.error(f"FFmpeg failed for {watch_id}: {result.stderr}")
            return False

    def convert_image(self, watch_id: str, target_format: str = "jpg", keep_source: bool = False) -> bool:
        """
        Converts the cover art to the target format using ImageMagick.
        """
        # Find source image
        source_file = None
        for ext in utils.CONVERTIBLE_IMAGE_EXTENSIONS:
            path = self.working_dir / f"{watch_id}{ext}"
            if path.exists():
                source_file = path
                break

        if not source_file:
            if (self.working_dir / f"{watch_id}.jpg").exists():
                return True
            pass

        if not source_file:
            logger.warning(f"No cover art found for {watch_id}")
            return False

        output_file = self.working_dir / f"{watch_id}.{target_format}"

        # If source is already target format, we are good
        if source_file == output_file:
            return True

        # If output exists, assume it's done
        if output_file.exists():
            return True

        command = ["magick", str(source_file), str(output_file)]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Converted cover for {watch_id} to {target_format}")
            if not keep_source and source_file != output_file:
                try:
                    source_file.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete source cover {source_file}: {e}")
            return True
        else:
            logger.error(f"ImageMagick failed for {watch_id}: {result.stderr}")
            return False

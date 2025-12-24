import base64
import logging
from pathlib import Path
from typing import Optional

from mutagen.easyid3 import EasyID3
from mutagen.flac import Picture
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.oggopus import OggOpus

from . import utils

logger = logging.getLogger(__name__)


class Tagger:
    def __init__(self, working_dir: Path = utils.WORKING_DIR):
        self.working_dir = working_dir

    def tag(
        self,
        watch_id: str,
        artist: str,
        title: str,
        album: Optional[str] = None,
        delete_embeds: bool = False,
        embed_extras: list = None,
    ) -> bool:
        """
        Tags the audio file with artist, title, cover art, and lyrics.
        Optionally deletes source files after embedding.
        """
        # Find audio file
        audio_file = None
        for ext in [".opus", ".mp3"]:
            path = self.working_dir / f"{watch_id}{ext}"
            if path.exists():
                audio_file = path
                break

        if not audio_file:
            logger.error(f"No audio file found for {watch_id} to tag")
            return False

        cover_file = None
        # Check for cover files (jpg or webp)
        for ext in [".jpg", ".webp"]:
            path = self.working_dir / f"{watch_id}{ext}"
            if path.exists():
                cover_file = path
                break

        # Find lyrics file (.lrc or .txt)
        lyrics_file = None
        for ext in [".lrc", ".txt"]:
            path = self.working_dir / f"{watch_id}{ext}"
            if path.exists():
                lyrics_file = path
                break

        try:
            embed_extras = embed_extras or []
            if audio_file.suffix == ".mp3":
                self._tag_mp3(audio_file, cover_file, artist, title, album, lyrics_file, embed_extras)
            elif audio_file.suffix == ".opus":
                self._tag_opus(audio_file, cover_file, artist, title, album, lyrics_file, embed_extras)

            # Delete source files if requested
            if delete_embeds:
                if lyrics_file and lyrics_file.exists():
                    lyrics_file.unlink()
                    logger.info(f"Deleted embedded lyrics file: {lyrics_file.name}")
                if cover_file and cover_file.exists():
                    cover_file.unlink()
                    logger.info(f"Deleted embedded cover file: {cover_file.name}")

            logger.info(f"Tagged {watch_id}: {artist} - {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to tag {watch_id}: {e}")
            return False

    def _tag_mp3(
        self,
        audio_path: Path,
        cover_path: Optional[Path],
        artist: str,
        title: str,
        album: Optional[str] = None,
        lyrics_file: Optional[Path] = None,
        embed_extras: list = None,
    ):
        try:
            audio = ID3(audio_path)
        except ID3NoHeaderError:
            audio = ID3()

        if "cover" in embed_extras and cover_path and cover_path.exists():
            with open(cover_path, "rb") as albumart:
                audio.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=albumart.read(),
                    )
                )

        # Add lyrics if available
        if "lyric" in embed_extras and lyrics_file and lyrics_file.exists():
            from mutagen.id3 import USLT

            lyrics_text = lyrics_file.read_text(encoding="utf-8")
            # Use USLT (Unsynchronized Lyrics) for both .lrc and .txt
            # Note: ID3 doesn't have great support for synced lyrics in the way LRC does
            # Using 'xxx' for undetermined language since songs may be in any language
            audio.add(USLT(encoding=3, lang="xxx", desc="", text=lyrics_text))

        audio.save(audio_path, v2_version=3)

        # Now text tags
        try:
            audio_easy = EasyID3(audio_path)
        except ID3NoHeaderError:
            audio_easy = EasyID3()

        if artist:
            audio_easy["artist"] = artist
        if title:
            audio_easy["title"] = title
        if album:
            audio_easy["album"] = album
        audio_easy.save(audio_path, v2_version=3)

    def _tag_opus(
        self,
        audio_path: Path,
        cover_path: Optional[Path],
        artist: str,
        title: str,
        album: Optional[str] = None,
        lyrics_file: Optional[Path] = None,
        embed_extras: list = None,
    ):
        audio = OggOpus(audio_path)
        if artist:
            audio["artist"] = artist
        if title:
            audio["title"] = title
        if album:
            audio["album"] = album

        # Add lyrics if available
        if "lyric" in embed_extras and lyrics_file and lyrics_file.exists():
            lyrics_text = lyrics_file.read_text(encoding="utf-8")
            audio["lyrics"] = lyrics_text

        if "cover" in embed_extras and cover_path and cover_path.exists():
            with open(cover_path, "rb") as img:
                image_data = img.read()

            pic = Picture()
            pic.data = image_data
            pic.type = 3
            pic.mime = "image/jpeg"
            pic.desc = "Cover"

            # OggOpus expects base64 encoded picture block
            audio["metadata_block_picture"] = [base64.b64encode(pic.write()).decode("ascii")]

        audio.save()

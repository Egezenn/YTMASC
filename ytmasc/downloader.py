import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from ytmusicapi import YTMusic

from . import utils

logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, working_dir: Path = utils.WORKING_DIR, download_extras: list = None):
        self.working_dir = working_dir
        self.download_extras = download_extras or []

    def fetch_metadata(self, watch_id: str) -> Optional[Dict[str, str]]:
        """
        Fetches metadata (artist, title, album) from YouTube Music.
        """
        try:
            ytmusic = YTMusic()
            song = ytmusic.get_song(watch_id)
            video_details = song.get("videoDetails", {})

            title = video_details.get("title")
            author = video_details.get("author")

            return {
                "artist": author,
                "title": title,
                "album": None,  # not all songs have an album property set
            }
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for {watch_id}: {e}")
            return None

    def download(
        self,
        watch_id: str,
        artist: Optional[str] = None,
        title: Optional[str] = None,
        existing_meta: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Downloads audio and cover art for a given watch_id.
        Returns (success, metadata_dict) where metadata_dict contains:
        - lyric_source: provider that provided lyrics (lrclib/kugou/yt)
        - lyric_format: format of lyrics (.lrc/.txt)
        - cover_method: how cover was obtained (api/static)
        - cover_dimensions: dimensions of cover (WxH)

        If existing_meta contains lyric_embedded or img_embedded, those downloads are skipped.
        """
        existing_meta = existing_meta or {}
        metadata = {
            "lyric_source": None,
            "lyric_format": ".lrc",
            "cover_method": None,
            "cover_dimensions": None,
        }

        # Check if already downloaded
        existing_files = list(self.working_dir.glob(f"{watch_id}.*"))
        has_audio = any(f.suffix in utils.AUDIO_EXTENSIONS for f in existing_files)

        # We always want to ensure we have the cover art too
        # Check for existing cover art with various extensions
        has_cover = any((self.working_dir / f"{watch_id}{ext}").exists() for ext in utils.IMAGE_EXTENSIONS)

        # Download audio if not already present
        if has_audio:
            logger.info(f"Skipping audio download for {watch_id} (already exists)")
        else:
            url = f"https://www.youtube.com/watch?v={watch_id}"
            output_template = str(self.working_dir / f"{watch_id}.%(ext)s")

            cmd = [
                "yt-dlp",
                "--format",
                "bestaudio/best",
                "--output",
                output_template,
                "--quiet",
                "--ignore-errors",
                url,
            ]

            try:
                import subprocess

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    logger.error(f"yt-dlp failed for {watch_id}: {result.stderr}")
                    return False, metadata

            except Exception as e:
                logger.error(f"Audio download failed for {watch_id}: {e}")

                # ---------------------------------------------------------
                # TODO: Insert custom logic for handling download failures here.
                # E.g. If the video is unavailable, select the best match
                #
                # if "Video unavailable" in str(e):
                #     pass
                # ---------------------------------------------------------

                return False, metadata

        # Download cover art manually if not already present and requested
        if "cover" in self.download_extras:
            if has_cover:
                logger.info(f"Skipping cover art download for {watch_id} (already exists)")
                # Detect existing cover dimensions using ImageMagick
                for ext in utils.IMAGE_EXTENSIONS:
                    cover_file = self.working_dir / f"{watch_id}{ext}"
                    if cover_file.exists():
                        try:
                            import subprocess

                            result = subprocess.run(
                                ["magick", "identify", "-format", "%wx%h", str(cover_file)],
                                capture_output=True,
                                text=True,
                                timeout=5,
                            )
                            if result.returncode == 0:
                                dimensions = result.stdout.strip()
                                metadata["cover_method"] = "unknown"
                                metadata["cover_dimensions"] = dimensions
                                logger.debug(f"Detected existing cover for {watch_id}: {dimensions}")
                        except Exception as e:
                            logger.debug(f"Failed to detect cover dimensions for {watch_id}: {e}")
                        break
            elif not has_cover:
                try:
                    # Use ytmusicapi to get the best quality thumbnail (usually square format)
                    # TODO: This might be undesired for archival purposes YouTube usually provides maxresdefault anyway.
                    #       We can add an option to try to get the maxresdefault thumbnail instead.
                    ytmusic = YTMusic()
                    song_info = ytmusic.get_song(watch_id)

                    thumbnails = song_info.get("videoDetails", {}).get("thumbnail", {}).get("thumbnails", [])

                    if thumbnails:
                        # Get the highest resolution thumbnail
                        best_thumbnail = max(thumbnails, key=lambda x: x.get("width", 0) * x.get("height", 0))
                        cover_url = best_thumbnail["url"]

                        response = requests.get(cover_url, timeout=10)
                        response.raise_for_status()

                        # Determine file extension from content type or URL
                        content_type = response.headers.get("content-type", "")
                        if "webp" in content_type or cover_url.endswith(".webp"):
                            cover_path = self.working_dir / f"{watch_id}.webp"
                        else:
                            cover_path = self.working_dir / f"{watch_id}.jpg"

                        cover_path.write_bytes(response.content)

                        # Track metadata
                        metadata["cover_method"] = "api"
                        metadata["cover_dimensions"] = f"{best_thumbnail.get('width')}x{best_thumbnail.get('height')}"

                        logger.info(
                            f"Downloaded cover art for {watch_id} ({best_thumbnail.get('width')}x{best_thumbnail.get('height')})"
                        )
                    else:
                        raise ValueError("No thumbnails found in API response")

                # TODO: These mostly contain 16:9 images, so we should try to find a way to get the square image
                except Exception as e:
                    logger.warning(f"ytmusicapi failed for {watch_id}, falling back to WebP URLs: {e}")

                    # Fallback to direct YouTube WebP thumbnail URLs
                    # Try maxresdefault first (1280x720)
                    cover_path = self.working_dir / f"{watch_id}.webp"
                    try:
                        cover_url = f"https://i.ytimg.com/vi_webp/{watch_id}/maxresdefault.webp"
                        response = requests.get(cover_url, timeout=10)
                        response.raise_for_status()
                        cover_path.write_bytes(response.content)
                        metadata["cover_method"] = "static"
                        metadata["cover_dimensions"] = "1280x720"
                        logger.info(f"Downloaded cover art for {watch_id} (maxresdefault.webp)")
                    except Exception:
                        # Fallback to sddefault (640x480)
                        try:
                            cover_url = f"https://i.ytimg.com/vi_webp/{watch_id}/sddefault.webp"
                            response = requests.get(cover_url, timeout=10)
                            response.raise_for_status()
                            cover_path.write_bytes(response.content)
                            metadata["cover_method"] = "static"
                            metadata["cover_dimensions"] = "640x480"
                            logger.info(f"Downloaded cover art for {watch_id} (sddefault.webp)")
                        except Exception:
                            # Final fallback to hqdefault (480x360)
                            try:
                                cover_url = f"https://i.ytimg.com/vi_webp/{watch_id}/hqdefault.webp"
                                response = requests.get(cover_url, timeout=10)
                                response.raise_for_status()
                                cover_path.write_bytes(response.content)
                                metadata["cover_method"] = "static"
                                metadata["cover_dimensions"] = "480x360"
                                logger.info(f"Downloaded cover art for {watch_id} (hqdefault.webp)")
                            except Exception as e:
                                logger.warning(f"Failed to download cover for {watch_id}: {e}")

        # Download lyrics if desired and artist and title are available
        if "lyric" in self.download_extras:
            if artist and title:
                lyrics_meta = self._download_lyrics(watch_id, artist, title)
                metadata["lyric_source"] = lyrics_meta.get("source")
                metadata["lyric_format"] = lyrics_meta.get("format")
            else:
                logger.info(f"Skipping lyrics download for {watch_id} (missing artist and/or title metadata)")

        return True, metadata

    def _download_lyrics(
        self, watch_id: str, artist: Optional[str] = None, title: Optional[str] = None
    ) -> Dict[str, Optional[str]]:
        """
        Downloads lyrics for a given watch_id.
        Tries multiple sources in order: lrclib -> kugou -> YouTube Music.
        Saves as .lrc (synced) or .txt (unsynced) file.
        Returns dict with 'source' and 'format' keys.
        """
        # Check if lyrics already exist
        lrc_path = self.working_dir / f"{watch_id}.lrc"

        if lrc_path.exists():
            # TODO: check if timestamped
            logger.info(f"Skipping lyrics download for {watch_id} (already exists)")
            return {"source": "unknown", "format": ".lrc"}

        if artist and title:
            result = self._try_lrclib(watch_id, artist, title, lrc_path)
            if result:
                return result

            # Try kugou second
            result = self._try_kugou(watch_id, artist, title, lrc_path)
            if result:
                return result

        # Try YouTube Music as fallback
        result = self._try_youtube_lyrics(watch_id, lrc_path)
        if result:
            return result

        logger.info(f"No lyrics available for {watch_id} from any source")
        return {"source": None, "format": None}

    def _try_lrclib(self, watch_id: str, artist: str, title: str, lrc_path: Path) -> Optional[Dict[str, str]]:
        """Try to download lyrics from lrclib.net"""
        try:
            url = "https://lrclib.net/api/search"
            params = {"artist_name": artist, "track_name": title}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()

            if not results or len(results) == 0:
                logger.debug(f"No lrclib results for {watch_id}")
                return None

            # Use the first result
            lyrics_data = results[0]

            # Check for synced lyrics first
            if lyrics_data.get("syncedLyrics"):
                lrc_path.write_text(lyrics_data["syncedLyrics"], encoding="utf-8")
                logger.info(f"Downloaded synced lyrics for {watch_id} from lrclib (.lrc)")
                return {"source": "lrclib", "format": ".lrc"}
            elif lyrics_data.get("plainLyrics"):
                lrc_path.write_text(lyrics_data["plainLyrics"], encoding="utf-8")
                logger.info(f"Downloaded lyrics for {watch_id} from lrclib (.lrc)")
                return {"source": "lrclib", "format": ".lrcX"}

            return None

        except Exception as e:
            logger.debug(f"lrclib failed for {watch_id}: {e}")
            return None

    def _try_kugou(self, watch_id: str, artist: str, title: str, lrc_path: Path) -> Optional[Dict[str, str]]:
        """Try to download lyrics from Kugou"""
        try:
            search_url = "http://lyrics.kugou.com/search"
            params = {
                "ver": 1,
                "man": "yes",
                "client": "pc",
                "keyword": f"{artist} {title}",
            }

            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != 200 or not data.get("candidates"):
                logger.debug(f"No kugou results for {watch_id}")
                return None

            # Get the first candidate
            candidate = data["candidates"][0]
            accesskey = candidate.get("accesskey")
            song_id = candidate.get("id")

            if not accesskey or not song_id:
                return None

            # Download the lyrics
            lyrics_url = "http://lyrics.kugou.com/download"
            params = {
                "ver": 1,
                "client": "pc",
                "id": song_id,
                "accesskey": accesskey,
                "fmt": "lrc",
                "charset": "utf8",
            }

            response = requests.get(lyrics_url, params=params, timeout=10)
            response.raise_for_status()
            lyrics_data = response.json()

            if lyrics_data.get("status") == 200 and lyrics_data.get("content"):
                import base64

                lyrics_content = base64.b64decode(lyrics_data["content"]).decode("utf-8")
                lrc_path.write_text(lyrics_content, encoding="utf-8")
                logger.info(f"Downloaded synced lyrics for {watch_id} from kugou (.lrc)")
                return {"source": "kugou", "format": ".lrc"}

            return None

        except Exception as e:
            logger.debug(f"kugou failed for {watch_id}: {e}")
            return None

    def _try_youtube_lyrics(self, watch_id: str, lrc_path: Path) -> Optional[Dict[str, str]]:
        """Try to download lyrics from YouTube Music"""
        try:
            ytmusic = YTMusic()

            # Get watch playlist to find browse_id for lyrics
            watch_playlist = ytmusic.get_watch_playlist(videoId=watch_id)

            if not watch_playlist or "lyrics" not in watch_playlist:
                return None

            lyrics_browse_id = watch_playlist["lyrics"]
            if not lyrics_browse_id:
                return None

            # Get the actual lyrics
            lyrics_data = ytmusic.get_lyrics(lyrics_browse_id)

            if not lyrics_data or "lyrics" not in lyrics_data:
                return None

            lyrics_text = lyrics_data["lyrics"]

            # Check if synced lyrics are available
            if "syncedLyrics" in lyrics_data and lyrics_data["syncedLyrics"]:
                lrc_path.write_text(lyrics_data["syncedLyrics"], encoding="utf-8")
                logger.info(f"Downloaded synced lyrics for {watch_id} from YouTube (.lrc)")
                return {"source": "yt", "format": ".lrc"}
            else:
                lrc_path.write_text(lyrics_text, encoding="utf-8")
                logger.info(f"Downloaded lyrics for {watch_id} from YouTube (.lrc)")
                return {"source": "yt", "format": ".lrcX"}

        except Exception as e:
            logger.debug(f"YouTube lyrics failed for {watch_id}: {e}")
            return None

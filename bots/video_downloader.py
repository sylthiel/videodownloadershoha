"""
Module for downloading videos from various social media platforms.
Currently supports:
- Instagram
- TikTok
"""

import os
import tempfile
import instaloader
import requests
import re
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from TikTokApi import TikTokApi


class OutputCapture:
    """Class to capture stdout output."""

    def __init__(self):
        """Initialize the OutputCapture."""
        self.captured_text = ""

    def write(self, text):
        """Write text to the captured_text attribute and to the original stdout."""
        self.captured_text += text
        # Also write to the original stdout so we can still see the output
        sys.__stdout__.write(text)

    def flush(self):
        """Flush the output."""
        sys.__stdout__.flush()


class VideoDownloader:
    """Class for downloading videos from various social media platforms."""

    def __init__(self, download_dir="downloads", cache_duration_days=1):
        """
        Initialize the VideoDownloader.

        Args:
            download_dir: Base directory for downloaded videos
            cache_duration_days: How long to keep videos in cache (in days)
        """
        self.download_dir = download_dir
        self.instagram_dir = os.path.join(download_dir, "instagram")
        self.tiktok_dir = os.path.join(download_dir, "tiktok")
        self.cache_file = os.path.join(download_dir, "cache_metadata.json")
        self.cache_duration = timedelta(days=cache_duration_days)

        # Create download directories if they don't exist
        os.makedirs(self.instagram_dir, exist_ok=True)
        os.makedirs(self.tiktok_dir, exist_ok=True)

        # Initialize or load cache metadata
        self.cache_metadata = self._load_cache_metadata()

        # Clean up old cache entries on startup
        self._cleanup_cache()

        self.instagram = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )

        # TikTok API will be initialized when needed to avoid unnecessary browser sessions

    def _load_cache_metadata(self) -> Dict:
        """Load cache metadata from file or create if it doesn't exist."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all platforms are in the cache metadata
                    if "instagram" not in data:
                        data["instagram"] = {}
                    if "tiktok" not in data:
                        data["tiktok"] = {}
                    return data
            except (json.JSONDecodeError, IOError):
                # If the file is corrupted or can't be read, start with empty cache
                return {"instagram": {}, "tiktok": {}}
        return {"instagram": {}, "tiktok": {}}

    def _save_cache_metadata(self):
        """Save cache metadata to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache_metadata, f)

    def _update_cache_entry(self, platform: str, video_id: str, file_path: str):
        """Update the cache entry for a video."""
        if platform not in self.cache_metadata:
            self.cache_metadata[platform] = {}

        self.cache_metadata[platform][video_id] = {
            "file_path": file_path,
            "last_accessed": datetime.now().isoformat(),
        }
        self._save_cache_metadata()

    def _cleanup_cache(self):
        """Remove old videos from cache."""
        now = datetime.now()
        platforms_to_check = list(self.cache_metadata.keys())

        for platform in platforms_to_check:
            videos_to_check = list(self.cache_metadata[platform].keys())

            for video_id in videos_to_check:
                entry = self.cache_metadata[platform][video_id]
                last_accessed = datetime.fromisoformat(entry["last_accessed"])

                # If the video is older than the cache duration, remove it
                if now - last_accessed > self.cache_duration:
                    file_path = entry["file_path"]
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass  # Ignore errors when removing files

                    # Remove the entry from the cache metadata
                    del self.cache_metadata[platform][video_id]

        # Save the updated cache metadata
        self._save_cache_metadata()

    def download_instagram_video(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Download a video from Instagram or retrieve from cache if available.

        Args:
            url: The URL of the Instagram post.

        Returns:
            A tuple containing (file_path, error_message).
            If successful, file_path will contain the path to the downloaded video and error_message will be None.
            If unsuccessful, file_path will be None and error_message will contain the error message.
        """
        try:
            # Extract the shortcode from the URL
            # URL format: https://www.instagram.com/p/SHORTCODE/ or https://www.instagram.com/reel/SHORTCODE/
            if '/p/' in url:
                shortcode = url.split('/p/')[1].split('/')[0]
            elif '/reel/' in url:
                shortcode = url.split('/reel/')[1].split('/')[0]
            else:
                return None, "Invalid Instagram URL format. Expected format: https://www.instagram.com/p/SHORTCODE/ or https://www.instagram.com/reel/SHORTCODE/"

            # Check if the video is in the cache
            if "instagram" in self.cache_metadata and shortcode in self.cache_metadata["instagram"]:
                cache_entry = self.cache_metadata["instagram"][shortcode]
                file_path = cache_entry["file_path"]

                # If the file exists, update the last_accessed time and return the path
                if os.path.exists(file_path):
                    print(f"Using cached video for shortcode: {shortcode}")
                    self._update_cache_entry("instagram", shortcode, file_path)
                    return file_path, None
                else:
                    # If the file doesn't exist, remove the entry from the cache
                    del self.cache_metadata["instagram"][shortcode]
                    self._save_cache_metadata()

            # If not in cache or file doesn't exist, download the video
            print(f"Downloading video for shortcode: {shortcode}")
            file_path = os.path.join(self.instagram_dir, f"{shortcode}.mp4")

            # Create a temporary directory to store the downloaded video
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download the post
                post = instaloader.Post.from_shortcode(self.instagram.context, shortcode)

                # Check if the post contains a video
                if not post.is_video:
                    return None, "The Instagram post does not contain a video."

                # Redirect stdout to capture instaloader output
                original_stdout = sys.stdout
                sys.stdout = OutputCapture()

                try:
                    # Download the video
                    self.instagram.download_post(post, target=temp_dir)
                finally:
                    # Restore stdout and get the captured output
                    captured_output = sys.stdout.captured_text
                    sys.stdout = original_stdout

                # Look for the video file path in the captured output
                # The pattern is typically something like: [Post text] /path/to/file.mp4
                video_path_match = re.search(r'\] (.*?\.mp4)', captured_output)

                if video_path_match:
                    # Extract the video file path
                    video_path = video_path_match.group(1)

                    # Copy the file to the organized directory
                    try:
                        with open(video_path, 'rb') as src_file:
                            with open(file_path, 'wb') as dst_file:
                                dst_file.write(src_file.read())

                        # Update the cache metadata
                        self._update_cache_entry("instagram", shortcode, file_path)
                        return file_path, None
                    except FileNotFoundError:
                        return None, f"Video file not found at path: {video_path}"
                    except Exception as e:
                        return None, f"Error copying video file: {str(e)}"

                # If we couldn't find the video path in the output, try the old method
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp4'):
                        # Copy the file from the temporary directory to the organized directory
                        with open(os.path.join(temp_dir, file), 'rb') as src_file:
                            with open(file_path, 'wb') as dst_file:
                                dst_file.write(src_file.read())

                        # Update the cache metadata
                        self._update_cache_entry("instagram", shortcode, file_path)
                        return file_path, None

                return None, "Could not find the downloaded video file."

        except instaloader.exceptions.InstaloaderException as e:
            return None, f"Instagram download error: {str(e)}"
        except Exception as e:
            return None, f"Error downloading Instagram video: {str(e)}"

    async def download_tiktok_video(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Download a video from TikTok or retrieve from cache if available.

        Args:
            url: The URL of the TikTok video.

        Returns:
            A tuple containing (file_path, error_message).
            If successful, file_path will contain the path to the downloaded video and error_message will be None.
            If unsuccessful, file_path will be None and error_message will contain the error message.
        """
        try:
            # Extract the video ID from the URL
            # TikTok URL formats:
            # - https://www.tiktok.com/@username/video/1234567890123456789
            # - https://vm.tiktok.com/1234567890123456789/
            # - https://m.tiktok.com/v/1234567890123456789.html

            video_id = None

            if '/video/' in url:
                video_id = url.split('/video/')[1].split('/')[0].split('?')[0]
            elif 'vm.tiktok.com' in url:
                # For shortened URLs, we need to follow the redirect
                response = requests.head(url, allow_redirects=True)
                final_url = response.url
                if '/video/' in final_url:
                    video_id = final_url.split('/video/')[1].split('/')[0].split('?')[0]
            elif 'm.tiktok.com/v/' in url:
                video_id = url.split('/v/')[1].split('.')[0]

            if not video_id:
                return None, "Invalid TikTok URL format. Could not extract video ID."

            # Check if the video is in the cache
            if "tiktok" in self.cache_metadata and video_id in self.cache_metadata["tiktok"]:
                cache_entry = self.cache_metadata["tiktok"][video_id]
                file_path = cache_entry["file_path"]

                # If the file exists, update the last_accessed time and return the path
                if os.path.exists(file_path):
                    print(f"Using cached video for TikTok ID: {video_id}")
                    self._update_cache_entry("tiktok", video_id, file_path)
                    return file_path, None
                else:
                    # If the file doesn't exist, remove the entry from the cache
                    del self.cache_metadata["tiktok"][video_id]
                    self._save_cache_metadata()

            # If not in cache or file doesn't exist, download the video
            print(f"Downloading video for TikTok ID: {video_id}")
            file_path = os.path.join(self.tiktok_dir, f"{video_id}.mp4")

            # Initialize TikTokApi and create sessions
            api = TikTokApi()
            await api.create_sessions(num_sessions=1, headless=True)

            try:
                # Create a Video object with the URL
                video = api.video(url=url)

                # Get the video information
                await video.info()

                # Download the video content
                video_data = await video.bytes()

                # Save the video to file
                with open(file_path, 'wb') as f:
                    f.write(video_data)

                # Update the cache metadata
                self._update_cache_entry("tiktok", video_id, file_path)
                return file_path, None
            finally:
                # Always close the sessions to clean up resources
                await api.close_sessions()

        except Exception as e:
            return None, f"Error downloading TikTok video: {str(e)}"

    def download_tiktok_video_sync(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Synchronous wrapper for the asynchronous download_tiktok_video method.

        Args:
            url: The URL of the TikTok video.

        Returns:
            A tuple containing (file_path, error_message).
        """
        # First, check if the video is in the cache
        # Extract the video ID from the URL
        video_id = None
        try:
            if '/video/' in url:
                video_id = url.split('/video/')[1].split('/')[0].split('?')[0]
            elif 'vm.tiktok.com' in url:
                # For shortened URLs, we need to follow the redirect
                response = requests.head(url, allow_redirects=True)
                final_url = response.url
                if '/video/' in final_url:
                    video_id = final_url.split('/video/')[1].split('/')[0].split('?')[0]
            elif 'm.tiktok.com/v/' in url:
                video_id = url.split('/v/')[1].split('.')[0]

            if not video_id:
                return None, "Invalid TikTok URL format. Could not extract video ID."

            # Check if the video is in the cache
            if "tiktok" in self.cache_metadata and video_id in self.cache_metadata["tiktok"]:
                cache_entry = self.cache_metadata["tiktok"][video_id]
                file_path = cache_entry["file_path"]

                # If the file exists, update the last_accessed time and return the path
                if os.path.exists(file_path):
                    print(f"Using cached video for TikTok ID: {video_id}")
                    self._update_cache_entry("tiktok", video_id, file_path)
                    return file_path, None
                else:
                    # If the file doesn't exist, remove the entry from the cache
                    del self.cache_metadata["tiktok"][video_id]
                    self._save_cache_metadata()
        except Exception as e:
            # If there's an error checking the cache, log it and continue with the download
            print(f"Error checking cache: {str(e)}")

        # If the video is not in the cache or there was an error checking the cache,
        # we need to download it using the async method
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async download method in the new loop
            try:
                return loop.run_until_complete(self.download_tiktok_video(url))
            finally:
                # Clean up the loop
                loop.close()
                asyncio.set_event_loop(None)
        except Exception as e:
            # If there's any other error, return it
            error_message = str(e)
            # Don't return the coroutine object in the error message
            if "coroutine object" in error_message:
                error_message = "Error downloading TikTok video. Please try again later."
            return None, f"Error downloading TikTok video: {error_message}"

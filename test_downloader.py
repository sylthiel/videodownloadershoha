#!/usr/bin/env python3
"""
Test script for the video downloader functionality.
This script allows you to test the video downloading functionality without setting up the Telegram bot.
"""

import sys
from bots.video_downloader import VideoDownloader

def main():
    """Main function to test the video downloader."""
    if len(sys.argv) != 2:
        print("Usage: python test_downloader.py <video_url>")
        print("Examples:")
        print("  Instagram: python test_downloader.py https://www.instagram.com/p/SHORTCODE/")
        print("  TikTok: python test_downloader.py https://www.tiktok.com/@username/video/1234567890123456789")
        print("\nNote: Videos are cached for 24 hours. Run this script multiple times with the same URL to test the caching mechanism.")
        return

    url = sys.argv[1]

    print(f"Attempting to process video from: {url}")
    print("(If this video was recently downloaded, it will be retrieved from cache)")

    # Create a video downloader instance
    downloader = VideoDownloader()

    # Determine the platform and download the video or get it from cache
    if "instagram.com" in url:
        file_path, error = downloader.download_instagram_video(url)
    elif "tiktok.com" in url or "vm.tiktok.com" in url:
        file_path, error = downloader.download_tiktok_video_sync(url)
    else:
        file_path, error = None, "Unsupported platform. Please provide a link from Instagram or TikTok."

    if file_path:
        print(f"Video available at: {file_path}")
        print("Run this script again with the same URL to verify caching (should be much faster)")
    else:
        print(f"Error processing video: {error}")

if __name__ == "__main__":
    main()

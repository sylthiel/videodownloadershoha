# Video Downloader Telegram Bot

A Telegram bot that downloads videos from various social media platforms and sends them back to the user.

## Features

- Download videos from Instagram posts and reels
- Download videos from TikTok
- Caching mechanism to avoid re-downloading recently requested videos
- Easy-to-use Telegram interface
- Can be used in private chats or added to channels
- Support for command-based usage with `/download` command
- Modular design for adding support for more platforms

## Caching Mechanism

The bot includes a caching mechanism that:
- Stores downloaded videos for 24 hours
- Avoids re-downloading videos that have been requested recently
- Automatically cleans up old videos to save disk space
- Maintains a cache metadata file to track video information

This improves performance and reduces bandwidth usage when the same videos are requested multiple times.

## Project Structure

- `bots/` - Main package directory
  - `__init__.py` - Package initialization
  - `video_downloader.py` - Module for downloading videos from various platforms
  - `bot.py` - Telegram bot implementation
- `downloads/` - Directory for downloaded videos
  - `instagram/` - Downloaded Instagram videos
  - `tiktok/` - Downloaded TikTok videos
  - `cache_metadata.json` - Cache metadata file
- `main.py` - Entry point for running the bot
- `deployment.md` - Detailed deployment instructions

## Quick Start

1. Clone the repository
2. Install dependencies:
   ```bash
   uv pip install -e .
   ```
3. Set your Telegram bot token:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

   Or, if you've made the script executable:
   ```bash
   ./main.py
   ```

## Testing the Downloader

You can test the video downloading functionality without setting up the Telegram bot using the provided test script:

```bash
python test_downloader.py <video_url>
```

Or, if you've made the script executable:
```bash
./test_downloader.py <video_url>
```

Examples:

For Instagram:
```bash
python test_downloader.py https://www.instagram.com/p/SHORTCODE/
```

For TikTok:
```bash
python test_downloader.py https://www.tiktok.com/@username/video/1234567890123456789
```

This will download the video from the provided URL and save it to the appropriate directory (`downloads/instagram` or `downloads/tiktok`).

## Supported Platforms

Currently, the bot supports downloading videos from:
- Instagram (posts and reels)
- TikTok

Support for more platforms (YouTube Shorts, Twitter/X, etc.) will be added in future updates.

## Deployment

For detailed deployment instructions, including how to deploy using systemd or Docker, see [deployment.md](deployment.md).

## Requirements

- Python 3.12 or higher
- Dependencies listed in pyproject.toml

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Here are some ways you can contribute:
- Add support for more video platforms
- Improve error handling and user experience
- Add tests
- Improve documentation

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - For the Telegram bot API wrapper
- [instaloader](https://github.com/instaloader/instaloader) - For Instagram downloading functionality
- [TikTokApi](https://github.com/davidteather/TikTok-Api) - For TikTok downloading functionality
- [playwright](https://playwright.dev/) - For browser automation used by TikTokApi

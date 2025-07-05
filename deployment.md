# Deployment Guide for Video Downloader Telegram Bot

This guide provides instructions for deploying the Video Downloader Telegram Bot.

## Prerequisites

- Python 3.12 or higher
- `uv` package manager (recommended) or `pip`
- A Telegram account

## Step 1: Create a Telegram Bot

1. Open Telegram and search for the "BotFather" (@BotFather).
2. Start a chat with BotFather and send the command `/newbot`.
3. Follow the instructions to create a new bot:
   - Provide a name for your bot (e.g., "Video Downloader Bot").
   - Provide a username for your bot (must end with "bot", e.g., "video_downloader_bot").
4. BotFather will provide you with a token for your bot. Save this token as you will need it later.

## Step 2: Clone the Repository

```bash
git clone <repository-url>
cd bots
```

## Step 3: Install Dependencies

Using `uv` (recommended):

```bash
uv pip install -e .
```

Or using `pip`:

```bash
pip install -e .
```

### Install Playwright Browser Dependencies

The TikTok video downloading functionality requires Playwright for browser automation. After installing the Python dependencies, you need to install the browser dependencies:

```bash
python -m playwright install
```

This will download and install the necessary browser binaries (Chromium, Firefox, and WebKit) used by Playwright.

## Step 4: Set Environment Variables

Set the Telegram bot token as an environment variable:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

For persistent storage of the token, you can add this line to your shell profile file (e.g., `~/.bashrc`, `~/.zshrc`).

## Step 5: Run the Bot

You can run the bot using one of the following methods:

### Method 1: Using the main script

```bash
python main.py
```

### Method 2: Using the module path

```bash
python -m bots.bot
```

The bot should now be running and ready to receive messages.

## Step 6: Test the Bot

1. Open Telegram and search for your bot using the username you provided.
2. Start a chat with your bot and send the `/start` command.
3. Test the video downloading functionality:
   - Send an Instagram link (e.g., `https://www.instagram.com/reel/SHORTCODE/`)
   - Send a TikTok link (e.g., `https://www.tiktok.com/@username/video/1234567890123456789`)
   - Try using the `/download` command: `/download https://www.instagram.com/reel/SHORTCODE/`

## Deploying to a Server

For long-term deployment, you may want to run the bot on a server. Here are some options:

### Option 1: Using systemd (Linux)

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/telegram-video-bot.service
```

2. Add the following content:

```
[Unit]
Description=Telegram Video Downloader Bot
After=network.target

[Service]
User=<your-username>
WorkingDirectory=/path/to/bots
Environment="TELEGRAM_BOT_TOKEN=your_bot_token_here"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable telegram-video-bot.service
sudo systemctl start telegram-video-bot.service
```

### Option 2: Using Docker

1. Create a Dockerfile:

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -e .

ENV TELEGRAM_BOT_TOKEN=your_bot_token_here

CMD ["python", "main.py"]
```

2. Build and run the Docker container:

```bash
docker build -t telegram-video-bot .
docker run -d --name telegram-video-bot telegram-video-bot
```

## Troubleshooting

- If the bot doesn't respond, check if the `TELEGRAM_BOT_TOKEN` environment variable is set correctly.
- Check the logs for any error messages.
- Ensure that the dependencies are installed correctly.
- If you're having issues with Instagram downloads, make sure your IP is not rate-limited by Instagram.
- For TikTok download issues:
  - Verify that Playwright browser dependencies are installed correctly (`python -m playwright install`).
  - TikTok may block automated access from certain IP addresses or regions.
  - Try updating the TikTokApi package if you encounter persistent issues.
- If the bot doesn't work in a channel, make sure:
  - The bot has been added to the channel as an administrator.
  - The bot has the necessary permissions to post messages in the channel.

## Using the Bot in Channels

The bot can be added to Telegram channels to download videos posted in the channel:

1. Add the bot to your channel as an administrator:
   - Open your channel in Telegram
   - Go to channel info → Administrators → Add Administrator
   - Search for your bot by username and add it
   - Make sure the bot has permission to post messages

2. Use the bot in the channel:
   - The bot only responds to commands in channels, not to regular messages
   - Use the `/download` command followed by a video URL:
     ```
     /download https://www.instagram.com/reel/SHORTCODE/
     ```
   - The bot will download the video and post it as a reply to your command

3. Benefits of using the bot in a channel:
   - Automatically convert video links to actual videos for all channel subscribers
   - Create a channel archive of videos that won't disappear if the original source is deleted
   - Improve viewing experience for channel members

## Adding Support for More Platforms

To add support for more platforms (e.g., YouTube Shorts, Twitter/X, Facebook), you'll need to:

1. Implement the download functionality in the `VideoDownloader` class in `bots/video_downloader.py`.
2. Update the message handler in `bots/bot.py` to recognize and process links from the new platform.
3. Update the `/download` command handler to support the new platform.

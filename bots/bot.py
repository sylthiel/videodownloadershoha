"""
Telegram bot for downloading videos from social media platforms.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .video_downloader import VideoDownloader

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create a video downloader instance
downloader = VideoDownloader()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! I'm a video downloader bot. Send me a link to a video from Instagram, TikTok, or YouTube, "
        "and I'll download it for you.\n\n"
        "You can also use the /download command followed by a link:\n"
        "/download https://www.instagram.com/reel/SHORTCODE/\n"
        "/download https://www.youtube.com/watch?v=VIDEO_ID\n\n"
        "Currently supported platforms:\n"
        "- Instagram (posts and reels)\n"
        "- TikTok\n"
        "- YouTube (videos and shorts)"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Send me a link to a video from Instagram, TikTok, or YouTube, and I'll download it for you.\n\n"
        "You can also use the /download command followed by a link:\n"
        "/download https://www.instagram.com/reel/SHORTCODE/\n"
        "/download https://www.youtube.com/watch?v=VIDEO_ID\n\n"
        "Currently supported platforms:\n"
        "- Instagram (posts and reels)\n"
        "- TikTok\n"
        "- YouTube (videos and shorts)"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message."""
    message_text = update.message.text

    # Check if the message contains a URL
    if "instagram.com" in message_text:
        await process_instagram_link(update, message_text)
    elif "tiktok.com" in message_text or "vm.tiktok.com" in message_text:
        await process_tiktok_link(update, message_text)
    elif "youtube.com" in message_text or "youtu.be" in message_text:
        await process_youtube_link(update, message_text)
    else:
        await update.message.reply_text(
            "Please send me a link to a video from a supported platform.\n\n"
            "Currently supported platforms:\n"
            "- Instagram (posts and reels)\n"
            "- TikTok\n"
            "- YouTube (videos and shorts)"
        )


async def process_instagram_link(update: Update, url: str) -> None:
    """Process an Instagram link and send the downloaded video."""
    # Send a message to indicate that the bot is processing the request
    processing_message = await update.message.reply_text("Downloading video... This may take a moment.")

    try:
        # Download the video or get it from cache
        file_path, error = downloader.download_instagram_video(url)

        if file_path:
            # Send the video
            with open(file_path, "rb") as video_file:
                await update.message.reply_video(video=video_file)

            # Delete the processing message
            await processing_message.delete()

            # Don't delete the file as it's now cached
            # os.remove(file_path)  # This line is removed to enable caching
        else:
            # Send an error message
            await processing_message.edit_text(f"Error: {error}")

    except Exception as e:
        # Send an error message
        await processing_message.edit_text(f"An error occurred: {str(e)}")


async def process_tiktok_link(update: Update, url: str) -> None:
    """Process a TikTok link and send the downloaded video."""
    # Send a message to indicate that the bot is processing the request
    processing_message = await update.message.reply_text("Downloading TikTok video... This may take a moment.")

    try:
        # Download the video or get it from cache
        file_path, error = downloader.download_tiktok_video_sync(url)

        if file_path:
            # Send the video
            with open(file_path, "rb") as video_file:
                await update.message.reply_video(video=video_file)

            # Delete the processing message
            await processing_message.delete()

            # Don't delete the file as it's now cached
        else:
            # Send an error message
            await processing_message.edit_text(f"Error: {error}")

    except Exception as e:
        # Send an error message
        error_message = str(e)
        # Check if the error message contains a coroutine object
        if "coroutine object" in error_message:
            error_message = "Error processing TikTok video. Please try again later."
        await processing_message.edit_text(f"An error occurred: {error_message}")


async def process_youtube_link(update: Update, url: str) -> None:
    """Process a YouTube link and send the downloaded video."""
    # Send a message to indicate that the bot is processing the request
    processing_message = await update.message.reply_text("Downloading YouTube video... This may take a moment.")

    try:
        # Download the video or get it from cache
        file_path, error = downloader.download_youtube_video(url)

        if file_path:
            # Send the video
            with open(file_path, "rb") as video_file:
                await update.message.reply_video(video=video_file)

            # Delete the processing message
            await processing_message.delete()

            # Don't delete the file as it's now cached
        else:
            # Send an error message
            await processing_message.edit_text(f"Error: {error}")

    except Exception as e:
        # Send an error message
        await processing_message.edit_text(f"An error occurred: {str(e)}")


async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /download command."""
    # Check if the command has arguments
    if not context.args:
        await update.message.reply_text(
            "Please provide a link to download.\n"
            "Example: /download https://www.instagram.com/reel/SHORTCODE/"
        )
        return

    # Get the URL from the arguments
    url = context.args[0]

    # Process the URL based on the platform
    if "instagram.com" in url:
        await process_instagram_link(update, url)
    elif "tiktok.com" in url or "vm.tiktok.com" in url:
        await process_tiktok_link(update, url)
    elif "youtube.com" in url or "youtu.be" in url:
        await process_youtube_link(update, url)
    else:
        await update.message.reply_text(
            "Unsupported platform. Please provide a link from a supported platform.\n\n"
            "Currently supported platforms:\n"
            "- Instagram (posts and reels)\n"
            "- TikTok\n"
            "- YouTube (videos and shorts)"
        )


async def cleanup_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job to clean up the cache periodically."""
    logger.info("Running scheduled cache cleanup")
    downloader._cleanup_cache()


def main() -> None:
    """Start the bot."""
    # Get the token from environment variable
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return

    # Create a new downloader instance with cache clearing on startup
    global downloader
    downloader = VideoDownloader(clear_cache_on_startup=True)
    logger.info("Initialized video downloader with cache clearing")

    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("download", download_command))

    # Handle regular messages in private chats
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_message))

    # Handle channel posts with commands
    application.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & filters.COMMAND, 
        lambda update, context: download_command(update, context) 
            if hasattr(update, 'channel_post') and update.channel_post and hasattr(update.channel_post, 'text') 
               and update.channel_post.text.startswith('/download') 
            else None
    ))

    # Add job to clean up cache every 6 hours (21600 seconds)
    if application.job_queue:
        application.job_queue.run_repeating(cleanup_cache_job, interval=21600)
    else:
        logger.warning("JobQueue not available. Cache cleanup will not run automatically.")

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

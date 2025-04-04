from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import instaloader

TOKEN = '7129478028:AAGChwAV75-YgOAlkj_XWfU9nO0vc3mqiJY'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video link from YouTube, Facebook, or Instagram.")

def download_video_from_youtube_or_facebook(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        return f"Error downloading from YouTube/Facebook: {str(e)}"

def download_video_from_instagram(url):
    loader = instaloader.Instaloader()
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        filename = f"downloads/{post.title}.mp4"
        loader.download_post(post, target=filename)
        return filename
    except Exception as e:
        return f"Error downloading from Instagram: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # Sending "Downloading" text and storing message ID
    sent_message = await update.message.reply_text("Downloading video...")

    if 'youtube.com' in url or 'youtu.be' in url or 'facebook.com' in url or 'fb.watch' in url:
        file_path = download_video_from_youtube_or_facebook(url)

        if "Error" in file_path:
            await update.message.reply_text(file_path)
        else:
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)

    elif 'instagram.com' in url:
        file_path = download_video_from_instagram(url)

        if "Error" in file_path:
            await update.message.reply_text(file_path)
        else:
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
            
    else:
        await update.message.reply_text("Unsupported link. Please send a valid YouTube, Instagram, or Facebook video URL.")

    # Deleting the original message and "Downloading video..." message
    await update.message.delete()  # Delete the user's URL message
    await sent_message.delete()  # Delete the "Downloading video..." message

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

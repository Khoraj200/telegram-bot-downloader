from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import asyncio

TOKEN = '7129478028:AAGChwAV75-YgOAlkj_XWfU9nO0vc3mqiJY'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video link from YouTube, Facebook, or Instagram.")

def download_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        return str(e)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # Send "Downloading video..." message and store its reference
    sent_message = await update.message.reply_text("Downloading video...")

    if 'youtube.com' in url or 'youtu.be' in url or 'facebook.com' in url or 'fb.watch' in url:
        file_path = download_video(url)

        if "ERROR" in file_path:
            await update.message.reply_text(f"Failed to download video: {file_path}")
        else:
            # Send the video to the user
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)

    elif 'instagram.com' in url:
        await update.message.reply_text("Instagram video downloading is restricted. Try using a public video or third-party API.")
    else:
        await update.message.reply_text("Unsupported link.")

    # Delete both the user's original message and the "Downloading video..." message
    await update.message.delete()  # Delete the original URL message
    await sent_message.delete()    # Delete the "Downloading video..." message

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())

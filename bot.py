from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = '7129478028:AAGChwAV75-YgOAlkj_XWfU9nO0vc3mqiJY'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video link from YouTube, Facebook, or Instagram.")

def download_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'extract_audio': False,
        'noplaylist': True,  # This ensures only a single video is downloaded, not a playlist.
        'force_generic_extractor': False  # This ensures yt-dlp uses the best extractor for the URL
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if 'youtube.com' in url or 'youtu.be' in url or 'facebook.com' in url or 'fb.watch' in url:
        await update.message.reply_text("Downloading video...")
        file_path = download_video(url)
        await update.message.reply_video(video=open(file_path, 'rb'))
        os.remove(file_path)
        
        # Delete the user's message with the URL after uploading the video
        await update.message.delete()

    elif 'instagram.com' in url:
        await update.message.reply_text("Downloading Instagram video...")
        try:
            file_path = download_video(url)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
            
            # Delete the user's message with the URL after uploading the video
            await update.message.delete()
        except Exception as e:
            await update.message.reply_text(f"Error downloading Instagram video: {str(e)}")

    else:
        await update.message.reply_text("Unsupported link.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()

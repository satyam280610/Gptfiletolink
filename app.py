import os
from flask import Flask, send_from_directory, render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio
import uvicorn
from multiprocessing import Process

VIDEO_DIR = "videos"
BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.route("/stream/<video_id>")
def stream(video_id):
    return render_template("stream.html", video_id=video_id)

@app.route("/video/<video_id>")
def serve_video(video_id):
    return send_from_directory(VIDEO_DIR, f"{video_id}.mp4")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.video:
        video = update.message.video
        file_id = video.file_id
        file = await context.bot.get_file(file_id)
        file_path = f"{VIDEO_DIR}/{file_id}.mp4"
        await file.download_to_drive(file_path)
        stream_url = f"https://your-subdomain.up.railway.app/stream/{file_id}"
        await update.message.reply_text(f"Stream your video here: {stream_url}")

def run_flask():
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def main():
    p = Process(target=run_flask)
    p.start()

    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    await bot_app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

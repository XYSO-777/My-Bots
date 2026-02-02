import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# -------- yt-dlp download function ----------
def download_video(url: str):
    output = f"{DOWNLOAD_DIR}/%(title)s.%(ext)s"

    # First try Bangla
    cmd_bn = [
        "yt-dlp",
        "-f", "bv+ba[language=bn]/best",
        "-o", output,
        url
    ]

    result = subprocess.run(cmd_bn)

    # If fail → fallback
    if result.returncode != 0:
        cmd_default = [
            "yt-dlp",
            "-f", "best",
            "-o", output,
            url
        ]
        subprocess.run(cmd_default)

    # return latest file
    files = sorted(
        [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)],
        key=os.path.getmtime
    )

    return files[-1]


# -------- Telegram command ----------
async def yturl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("❌ Usage:\n/yturl VIDEO_LINK")
            return

        url = context.args[0]

        msg = await update.message.reply_text("⏳ Downloading...")

        filepath = download_video(url)

        await msg.edit_text("📤 Uploading...")

        await update.message.reply_video(video=open(filepath, "rb"))

        os.remove(filepath)

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("❌ Error occurred!")


# -------- Start bot ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("yturl", yturl))

print("Bot Running...")
app.run_polling()

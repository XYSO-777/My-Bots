import os
import subprocess
import glob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def normalize_url(url):
    if "shorts/" in url:
        vid = url.split("shorts/")[1].split("?")[0]
        return f"https://youtube.com/watch?v={vid}"
    return url


def download_video(url):
    url = normalize_url(url)

    output = f"{DOWNLOAD_DIR}/%(title)s.%(ext)s"

    cmd = [
        "yt-dlp",
        "-f", "bv[height<=720]+ba[language=bn]/bv[height<=720]+ba/best[height<=720]",
        "-o", output,
        url
    ]

    subprocess.run(cmd, check=True)

    files = glob.glob(f"{DOWNLOAD_DIR}/*")
    return max(files, key=os.path.getctime)


async def yturl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage:\n/yturl link")
            return

        msg = await update.message.reply_text("⏳ Downloading...")

        filepath = download_video(context.args[0])

        size = os.path.getsize(filepath) / (1024 * 1024)

        if size > 49:
            await msg.edit_text(f"❌ File too large ({size:.1f}MB)\nTelegram limit 50MB")
            os.remove(filepath)
            return

        await msg.edit_text("📤 Uploading...")

        await update.message.reply_video(open(filepath, "rb"))

        os.remove(filepath)

    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Download failed (format/audio not found)")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("yturl", yturl))

print("Bot running...")
app.run_polling()

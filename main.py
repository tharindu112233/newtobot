import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# === CONFIG ===
BOT_TOKEN = "8177277075:AAH2NLrE9SSDzdLZdJZ3z9gZSbqA7ntp690"
CHANNEL_ID = -1002900384042
OWNER_ID = 8309811640

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not allowed to use this bot.")
        return
    await update.message.reply_text("👋 Send me photos or videos and I’ll forward them directly to the channel (no captions).")

# Handle incoming media
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    # --- Video ---
    if update.message.video:
        await context.bot.send_video(chat_id=CHANNEL_ID, video=update.message.video.file_id)

    # --- Photo ---
    elif update.message.photo:
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=update.message.photo[-1].file_id)

    # --- Video link (http/https) ---
    elif update.message.text and update.message.text.startswith("http"):
        url = update.message.text
        file_name = "temp_video.mp4"
        try:
            await update.message.reply_text("⬇️ Downloading video, please wait...")
            r = requests.get(url, stream=True)
            with open(file_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            # Send directly to channel
            await context.bot.send_video(chat_id=CHANNEL_ID, video=open(file_name, "rb"))
            os.remove(file_name)
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to download: {e}")
            return
    else:
        await update.message.reply_text("⚠️ Please send a photo, video, or a video link.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_media))

    app.run_polling()

if __name__ == "__main__":
    main()

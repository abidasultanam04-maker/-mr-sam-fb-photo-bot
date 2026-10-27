import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from urllib.parse import quote

TOKEN = os.getenv("BOT_TOKEN")
API = "https://apimsaterbd.com/fb-profile.php?url="

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\nFacebook profile link পাঠাও।"
    )

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (update.message.text or "").strip()

    if "facebook.com/" not in url:
        await update.message.reply_text("❌ সঠিক Facebook লিংক পাঠাও।")
        return

    try:
        await update.message.reply_text("⏳ ছবি খোঁজা হচ্ছে...")
        response = requests.get(API + quote(url, safe=""), timeout=20)
        response.raise_for_status()
        data = response.json()

        def find_url(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and value.startswith("http"):
                        if any(x in key.lower() for x in ["image", "photo", "picture", "url"]):
                            return value
                    result = find_url(value)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_url(item)
                    if result:
                        return result
            return None

        photo = find_url(data)
        if photo:
            await update.message.reply_photo(photo=photo)
        else:
            await update.message.reply_text(
                "ছবির লিংক পাওয়া যায়নি। API response পরীক্ষা করতে হবে।"
            )

    except Exception:
        await update.message.reply_text(
            "❌ API কাজ করেনি অথবা ছবির লিংক পাওয়া যায়নি।"
        )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN সেট করা হয়নি।")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, get_photo)
    )
    app.run_polling()

if __name__ == "__main__":
    main()
  

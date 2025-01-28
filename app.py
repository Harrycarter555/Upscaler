import requests
from bs4 import BeautifulSoup
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Google Images se photos fetch karein
def fetch_images(query):
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    images = soup.find_all("img")
    return [img["src"] for img in images]

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Mujhe HD photos dhoondhne ke liye kuch search karein.")

# Image search command handler
def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Kuch search term dijiye, jaise `/search nature`.")
        return

    update.message.reply_text(f"Searching for '{query}'...")
    image_urls = fetch_images(query)

    if not image_urls:
        update.message.reply_text("Koi images nahi mili.")
        return

    # Send images to Telegram
    media_group = [InputMediaPhoto(url) for url in image_urls[:5]]  # Max 5 images
    update.message.reply_media_group(media=media_group)

def main():
    # Apna Telegram Bot API Token yahan dalen
    updater = Updater("7882023357:AAGSyfZxk_YqoGY-8Q4ueLawq8ZfDK-Sc1w", use_context=True)

    # Dispatcher ko initialize karein
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("search", search))

    # Bot ko start karein
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

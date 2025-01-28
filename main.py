from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher, CallbackQueryHandler

app = Flask(__name__)

# Global variable to store current page number
current_page = 0

# Google Images se photos fetch karein
def fetch_images(query, num_images=10):
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract image URLs
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            images.append(src)
            if len(images) >= num_images:
                break
    return images

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Mujhe HD photos dhoondhne ke liye kuch search karein.")

# Image search command handler
def search(update: Update, context: CallbackContext):
    global current_page
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Kuch search term dijiye, jaise `/search nature`.")
        return

    update.message.reply_text(f"Searching for '{query}'...")
    image_urls = fetch_images(query, num_images=10)  # Fetch 10 images

    if not image_urls:
        update.message.reply_text("Koi images nahi mili.")
        return

    # Send first 5 images
    media_group = [InputMediaPhoto(url) for url in image_urls[:5]]
    update.message.reply_media_group(media=media_group)

    # Send next 5 images with a "Next Page" button
    if len(image_urls) > 5:
        keyboard = [
            [InlineKeyboardButton("Next Page", callback_data=f"next_page_{query}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Aur photos dekhne ke liye 'Next Page' par click karein:", reply_markup=reply_markup)

# Callback handler for "Next Page" button
def button_callback(update: Update, context: CallbackContext):
    global current_page
    query = update.callback_query.data.split("_")[2]  # Extract query from callback data
    update.callback_query.answer()

    # Fetch next set of images
    image_urls = fetch_images(query, num_images=10)
    start_index = (current_page + 1) * 5
    end_index = start_index + 5

    if start_index >= len(image_urls):
        update.callback_query.message.reply_text("Aur photos nahi hain.")
        return

    # Send next 5 images
    media_group = [InputMediaPhoto(url) for url in image_urls[start_index:end_index]]
    update.callback_query.message.reply_media_group(media=media_group)

    # Update page number
    current_page += 1

    # Send "Next Page" button again if more images are available
    if end_index < len(image_urls):
        keyboard = [
            [InlineKeyboardButton("Next Page", callback_data=f"next_page_{query}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text("Aur photos dekhne ke liye 'Next Page' par click karein:", reply_markup=reply_markup)

# Flask route for Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Initialize bot and dispatcher
bot_token = "7882023357:AAGSyfZxk_YqoGY-8Q4ueLawq8ZfDK-Sc1w"
bot = Updater(bot_token, use_context=True).bot
dispatcher = Dispatcher(bot, None, workers=0)

# Command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))

# Callback handler for "Next Page" button
dispatcher.add_handler(CallbackQueryHandler(button_callback))

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

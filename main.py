from flask import Flask, request
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher, CallbackQueryHandler

app = Flask(__name__)

# Function to fetch images from Google using Selenium
def fetch_images(query, num_images=10):
    options = Options()
    options.add_argument("--headless")  # Run browser in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)  # Path to your chromedriver

    # Load Google Images
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver.get(search_url)
    time.sleep(2)  # Allow time for images to load

    # Extract image URLs
    image_urls = set()
    images = driver.find_elements("css selector", "img")
    for img in images:
        src = img.get_attribute("src")
        if src and src.startswith("http"):
            image_urls.add(src)
        if len(image_urls) >= num_images:
            break

    driver.quit()
    return list(image_urls)

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Mujhe HD photos dhoondhne ke liye kuch search karein.\nExample: /search nature")

# Search command handler
def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Search term dijiye. Example: /search nature")
        return

    update.message.reply_text(f"Searching for '{query}'...")
    image_urls = fetch_images(query, num_images=10)

    if not image_urls:
        update.message.reply_text("Koi images nahi mili.")
        return

    # Send first 5 images
    media_group = [InputMediaPhoto(url) for url in image_urls[:5]]
    update.message.reply_media_group(media=media_group)

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

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

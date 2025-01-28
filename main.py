from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher
import time

app = Flask(__name__)

# Selenium WebDriver setup
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode for running without GUI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path="./chromedriver")  # Path to ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Fetch images using Selenium
def fetch_images(query, num_images=10):
    driver = setup_driver()
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver.get(search_url)
    time.sleep(2)  # Wait for the page to load

    # Fetch image URLs
    image_urls = []
    images = driver.find_elements(By.CSS_SELECTOR, "img")
    for img in images:
        src = img.get_attribute("src")
        if src and src.startswith("http"):
            image_urls.append(src)
            if len(image_urls) >= num_images:
                break
    driver.quit()  # Close the browser
    return image_urls

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! HD photos search karne ke liye `/search` command ka use karein. Example: `/search nature`.")

# Search command handler
def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Please provide a search term. Example: `/search nature`.")
        return

    update.message.reply_text(f"Searching for '{query}'...")

    # Fetch image URLs
    image_urls = fetch_images(query, num_images=10)

    if not image_urls:
        update.message.reply_text("Koi images nahi mili. Please try another keyword.")
        return

    # Send images to the user
    media_group = [InputMediaPhoto(url) for url in image_urls[:5]]  # Send only 5 images
    update.message.reply_media_group(media=media_group)

    # Send additional message for more images
    if len(image_urls) > 5:
        update.message.reply_text("Aapko aur images chahiye toh `/search <query>` command dobara use karein.")

# Flask route for Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Bot initialization
bot_token = "7882023357:AAGSyfZxk_YqoGY-8Q4ueLawq8ZfDK-Sc1w"  # Replace with your bot's token
bot = Updater(bot_token, use_context=True).bot
dispatcher = Dispatcher(bot, None, workers=0)

# Add Telegram command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

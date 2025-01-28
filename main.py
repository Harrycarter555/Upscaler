from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher
import time

app = Flask(__name__)

# Selenium WebDriver setup
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    service = Service("./chromedriver")  # Update the path to your ChromeDriver
    return webdriver.Chrome(service=service, options=chrome_options)

# Fetch images from Google
def fetch_images(query, num_images=5):
    driver = setup_driver()
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver.get(search_url)
    time.sleep(2)  # Wait for page to load
    
    # Scroll down to load more images
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
    
    # Extract image URLs
    images = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
    image_urls = []
    for img in images:
        try:
            src = img.get_attribute("src")
            if src and src.startswith("http"):
                image_urls.append(src)
                if len(image_urls) >= num_images:
                    break
        except Exception as e:
            continue
    driver.quit()
    return image_urls

# /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome! HD images search karne ke liye `/search` ka use karein.\n\n"
        "Example: `/search engine`"
    )

# /search command
def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Please provide a search term. Example: `/search nature`.")
        return

    update.message.reply_text(f"Searching for '{query}'...")

    # Fetch images
    image_urls = fetch_images(query, num_images=5)

    if not image_urls:
        update.message.reply_text("Sorry, koi images nahi mili. Please try another query.")
        return

    # Send fetched images to user
    media_group = [InputMediaPhoto(url) for url in image_urls]
    update.message.reply_media_group(media=media_group)

# Flask route for Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Telegram bot setup
bot_token = "7882023357:AAGSyfZxk_YqoGY-8Q4ueLawq8ZfDK-Sc1w"  # Replace with your bot token
bot = Updater(bot_token, use_context=True).bot
dispatcher = Dispatcher(bot, None, workers=0)

# Command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

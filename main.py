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
    service = Service(executable_path="./chromedriver")  # Update with your ChromeDriver path
    return webdriver.Chrome(service=service, options=chrome_options)

# Function to fetch images from Google
def fetch_images(query, num_images=10):
    driver = setup_driver()
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver.get(search_url)
    time.sleep(2)  # Allow page to load
    
    # Scroll to load more images
    for _ in range(3):  # Adjust scrolling attempts based on need
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
    
    # Fetch image URLs
    images = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
    image_urls = []
    for img in images:
        try:
            img.click()  # Click to load the full image
            time.sleep(1)
            full_img = driver.find_element(By.CSS_SELECTOR, "img.n3VNCb")
            src = full_img.get_attribute("src")
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
    update.message.reply_text("Welcome! Photos search karne ke liye `/search` command ka use karein. Example: `/search nature`.")

# /search command
def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Please provide a search term. Example: `/search nature`.")
        return

    update.message.reply_text(f"Searching for '{query}'...")

    # Fetch images
    image_urls = fetch_images(query, num_images=10)

    if not image_urls:
        update.message.reply_text("Koi images nahi mili. Please try another keyword.")
        return

    # Send images
    media_group = [InputMediaPhoto(url) for url in image_urls[:5]]
    update.message.reply_media_group(media=media_group)

    # Inform user about additional images
    if len(image_urls) > 5:
        update.message.reply_text("Aur images ke liye `/search <query>` dobara use karein.")

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

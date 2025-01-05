import os
import requests
from flask import Flask, request, send_from_directory
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from PIL import Image

app = Flask(__name__)

# Load configuration from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set.")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable is not set.")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Define the start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome to the Image Upscaler Bot! Send me an image to upscale.')

# Upscaling Function using Pillow
def upscale_image(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            # Double the size of the image
            new_size = (img.width * 2, img.height * 2)
            upscaled_image = img.resize(new_size, Image.ANTIALIAS)
            # Save the upscaled image
            upscaled_image.save(output_path)
        return output_path
    except Exception as e:
        return str(e)

# Handle image messages
def handle_image(update: Update, context: CallbackContext):
    if not update.message.photo:
        update.message.reply_text("Please send an image.")
        return

    photo = update.message.photo[-1]
    file = bot.get_file(photo.file_id)
    input_path = f"{photo.file_id}.jpg"
    output_path = f"upscaled_{photo.file_id}.jpg"

    # Download the image
    file.download(input_path)

    # Perform upscaling
    upscaled_path = upscale_image(input_path, output_path)

    # Send back the upscaled image
    if os.path.exists(upscaled_path):
        with open(upscaled_path, 'rb') as img:
            update.message.reply_photo(photo=img)
        os.remove(input_path)
        os.remove(output_path)
    else:
        update.message.reply_text("Error while processing the image.")

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))

# Add a command handler for images
dispatcher.add_handler(CommandHandler('image', handle_image))

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok', 200

# Home route
@app.route('/')
def home():
    return 'Hello, World!'

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.getcwd(), 'favicon.ico')

# Webhook setup route
@app.route('/setwebhook', methods=['GET', 'POST'])
def setup_webhook():
    webhook_url = f'{WEBHOOK_URL}/webhook'  # Ensure this URL is correct
    response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook',
        data={'url': webhook_url}
    )
    if response.json().get('ok'):
        return "Webhook setup ok"
    else:
        return "Webhook setup failed"

if __name__ == '__main__':
    app.run(port=5000)

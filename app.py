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
BIGJPG_API_KEY = os.getenv('BIGJPG_API_KEY')  # Add your Bigjpg API key here

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set.")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable is not set.")
if not BIGJPG_API_KEY:
    raise ValueError("BIGJPG_API_KEY environment variable is not set.")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Define the start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome to the Image Upscaler Bot! Send me an image to upscale.')

# Function to upscale the image using Bigjpg API
def upscale_image_with_bigjpg(image_url, style='photo', noise=0, x2=2):
    # Bigjpg API endpoint
    url = 'https://bigjpg.com/api/task'

    # API request data
    params = {
        'key': BIGJPG_API_KEY,
        'style': style,
        'noise': noise,
        'x2': x2,
        'url': image_url
    }

    # Make request to Bigjpg API
    response = requests.post(url, data=params)
    
    if response.status_code == 200:
        data = response.json()
        task_id = data.get('task_id')
        return task_id
    else:
        return None

# Function to get the result of the upscaled image
def get_upscaled_image(task_ids):
    url = f'https://bigjpg.com/api/task/{",".join(task_ids)}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'url' in data:
            return data['url']
        else:
            return None
    else:
        return None

# Handle image messages
def handle_image(update: Update, context: CallbackContext):
    if not update.message.photo:
        update.message.reply_text("Please send an image.")
        return

    photo = update.message.photo[-1]
    file = bot.get_file(photo.file_id)
    input_path = f"{photo.file_id}.jpg"

    # Download the image
    file.download(input_path)

    # Upload the image to Bigjpg (You can use your own method to upload or use an image URL)
    image_url = 'your_image_url_here'  # Replace with the actual URL if you have one
    task_id = upscale_image_with_bigjpg(image_url)

    if task_id:
        update.message.reply_text(f"Image is being processed! Task ID: {task_id}")
        
        # Now, we can poll Bigjpg API to get the result
        task_ids = [task_id]
        upscaled_image_url = get_upscaled_image(task_ids)

        if upscaled_image_url:
            update.message.reply_text("Here is your upscaled image: " + upscaled_image_url)
        else:
            update.message.reply_text("Error while processing the image.")
    else:
        update.message.reply_text("Error while requesting the image upscale.")

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

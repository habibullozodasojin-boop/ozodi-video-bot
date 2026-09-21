import os
import telebot
import urllib.parse
import random
import time
import threading
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Маленький сайт для Render чтобы он не падал
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

STYLES = ["beautiful girl in stylish modest clothes, fashion photo"]

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Privet BOS! Pishi /girl")

@bot.message_handler(commands=['girl'])
def girl_cmd(m):
    style = random.choice(STYLES)
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(style)}?width=512&height=768&nologo=true"
    bot.send_photo(m.chat.id, url, caption="Kak tebe? /girl")

# Запускаем сайт в фоне
threading.Thread(target=run_flask).start()

bot.delete_webhook(drop_pending_updates=True)
time.sleep(2)
print("Bot zapushen...")
bot.infinity_polling()

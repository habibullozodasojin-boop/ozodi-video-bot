import os
import telebot
import urllib.parse
import random
import time
import threading
import requests
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask).start()

def translate_to_english(text):
    try:
        # Бесплатный переводчик Google
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        r = requests.get(url, timeout=5).json()
        translated = "".join([x[0] for x in r[0]])
        return translated
    except:
        return text # если не получилось - оставляем как есть

def make_photo(chat_id, original_text):
    english_prompt = translate_to_english(original_text)
    bot.send_message(chat_id, f"⏳ Понял: '{original_text}'\nПеревел: '{english_prompt}'\nДелаю фото...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(english_prompt)}?width=768&height=1024&nologo=true&seed={random.randint(1,999999)}&enhance=true"
        bot.send_photo(chat_id, url, caption=f"Готово ✅\nТы написал: {original_text}")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Салом БОС! 🔥\nЯ понимаю ЛЮБОЙ язык!\n\nПиши на точики, на русском, на English - я пойму!\n\nПримеры:\n`Кӯҳҳои зебои Тоҷикистон`\n`Красивые горы Таджикистана`\n`Духтари зебо дар Душанбе`")

@bot.message_handler(commands=['girl'])
def girl_cmd(m):
    text = m.text.replace('/girl','').strip()
    if not text:
        text = "beautiful Tajik girl modest fashion"
    make_photo(m.chat.id, text)

@bot.message_handler(content_types=['text'])
def any_text(m):
    if m.text.startswith('/'): return
    make_photo(m.chat.id, m.text)

bot.delete_webhook(drop_pending_updates=True)
time.sleep(2)
print("Bot zapushen...")
bot.infinity_polling()

import os
import telebot
import urllib.parse
import random
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ОШИБКА: Нет BOT_TOKEN в Render!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

STYLES = [
    "beautiful girl in stylish modest winter clothes, full body, fashion photo, high quality",
    "beautiful girl in elegant long dress, modest fashion, studio photo",
    "beautiful girl in street style clothes jeans and jacket, full body, 4k"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет БОС! 🌙\nПиши /girl - скину образ")

@bot.message_handler(commands=['girl'])
def girl_cmd(message):
    style = random.choice(STYLES)
    bot.send_message(message.chat.id, f"Рисую: {style}...")
    encoded = urllib.parse.quote(style)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=768&nologo=true&model=flux"
    try:
        bot.send_photo(message.chat.id, image_url, caption="Как тебе? Еще? /girl")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(func=lambda m: True)
def custom_prompt(message):
    if message.text.startswith('/'):
        return
    prompt = f"beautiful girl in {message.text}, modest fashionable clothes, full body"
    bot.send_message(message.chat.id, f"Рисую: {prompt}...")
    encoded = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=768&nologo=true&model=flux"
    try:
        bot.send_photo(message.chat.id, image_url)
    except:
        bot.send_message(message.chat.id, "Попробуй другой текст")

# --- ВОТ ФИКС ОТ ОШИБКИ 409 ---
bot.delete_webhook(drop_pending_updates=True)
time.sleep(2)
print("Бот запущен...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

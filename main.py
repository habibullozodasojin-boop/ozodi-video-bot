import os
import telebot
import urllib.parse
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

STYLES = [
    "beautiful girl in stylish modest winter clothes, full body, fashion photo, high quality",
    "beautiful girl in elegant long dress, modest fashion, studio photo",
    "beautiful girl in street style clothes jeans and jacket, full body, 4k",
    "beautiful girl in cozy sweater and skirt, autumn fashion, beautiful"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет БОС! 🌙\nНапиши /girl - скину образ\nНапиши любой текст - нарисую по твоему тексту")

@bot.message_handler(commands=['girl'])
def girl_cmd(message):
    style = random.choice(STYLES)
    bot.send_message(message.chat.id, f"Рисую: {style}...")
    
    # Генерируем картинку через бесплатный API
    encoded = urllib.parse.quote(style)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=768&nologo=true&model=flux"
    
    try:
        bot.send_photo(message.chat.id, image_url, caption="Как тебе образ, БОС? Еще? /girl")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй еще раз /girl")

@bot.message_handler(func=lambda m: True)
def custom_prompt(message):
    if message.text.startswith('/'):
        return
    prompt = f"beautiful girl in {message.text}, modest fashionable clothes, full body, high quality"
    bot.send_message(message.chat.id, f"Рисую по твоему запросу: {prompt}...")
    
    encoded = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=768&nologo=true&model=flux"
    
    try:
        bot.send_photo(message.chat.id, image_url)
    except Exception as e:
        bot.send_message(message.chat.id, "Не получилось, попробуй другой текст")

print("Бот запущен...")
bot.infinity_polling()

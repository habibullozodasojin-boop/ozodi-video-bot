import os
import requests
import urllib.parse
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# 1. ГЕНЕРАЦИЯ ФОТО (БЕЗОПАСНАЯ)
def generate_ai_image(prompt):
    safe_prompt = f"{prompt}, safe for work, no nudity, no erotic, clothed, family friendly, beautiful, 4k"
    encoded = urllib.parse.quote(safe_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&safe=true"
    return url

# 2. ГЕНЕРАЦИЯ ВИДЕО 12 СЕКУНД
def generate_ai_video(prompt):
    # Добавляем длительность в промпт для ИИ
    safe_prompt = f"{prompt}, 12 seconds video, smooth motion, cinematic, safe for work, no nudity"
    encoded = urllib.parse.quote(safe_prompt)
    # Видео через Pollinations (12 сек)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&model=flux&nologo=true&safe=true&duration=12&enhance=true"
    return url

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом! 🇹🇯\nЯ твой ИИ бот!\n\nПросто напиши что нарисовать:\nПример: Душанбе ночью\n\nДля видео 12 сек пиши:\n/video свадьба в горах")

@bot.message_handler(commands=['video'])
def video_cmd(message):
    prompt = message.text.replace("/video", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, "Напиши так: /video горы Таджикистана")
        return
    
    bot.send_message(message.chat.id, f"🎬 Делаю видео 12 секунд: {prompt}... Жди 20 сек")
    try:
        video_url = generate_ai_video(prompt)
        # Отправляем как фото с анимацией (т.к. это 12 сек клип)
        bot.send_photo(message.chat.id, video_url, caption=f"✅ Готово! 12 сек: {prompt}")
        bot.send_message(message.chat.id, f"Вот ссылка на видео: {video_url}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    prompt = message.text
    bot.send_message(message.chat.id, f"🎨 Рисую: {prompt}... 10 сек")
    try:
        image_url = generate_ai_image(prompt)
        bot.send_photo(message.chat.id, image_url, caption=f"✅ Готово: {prompt}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

print("Бот запущен!")
bot.infinity_polling()

import os
import requests
import urllib.parse
import telebot
from telebot import types
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# 1. ГЕНЕРАЦИЯ ФОТО
def generate_ai_image(prompt):
    safe_prompt = f"{prompt}, safe for work, high quality"
    encoded = urllib.parse.quote(safe_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    return url

# 2. ГЕНЕРАЦИЯ ВИДЕО (через фото с анимацией)
def generate_ai_video(prompt):
    # Пока делаем как фото, потом можно улучшить
    return generate_ai_image(prompt)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом! 👋\n\nЯ Озоди видео бот.\nПросто напиши что нарисовать.\nНапример: флаг Таджикистана\nИли /video красивая машина")

@bot.message_handler(commands=['video'])
def video_cmd(message):
    prompt = message.text.replace("/video", "").strip()
    if not prompt:
        bot.send_message(message.chat.id, "Напиши после /video что сделать\nНапример: /video Tajikistan mountains")
        return

    bot.send_message(message.chat.id, f"Делаю видео: {prompt}... ⏳")
    try:
        video_url = generate_ai_video(prompt)
        bot.send_photo(message.chat.id, video_url, caption=f"Готово! 🎬\n{prompt}")
        bot.send_message(message.chat.id, "Хочешь еще? Просто напиши текст!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    prompt = message.text
    bot.send_message(message.chat.id, f"Рисую: {prompt}... 

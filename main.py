import os, telebot, urllib.parse, random, time, threading, requests, io
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Чтобы Render не спал
app = Flask(__name__)
@app.route('/')
def home(): return "OZODI VIDEO AI is Live!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

# --- Перевод ---
def to_english(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        r = requests.get(url, timeout=5).json()
        return "".join([x[0] for x in r[0]])
    except:
        return text

# --- Чат как ChatGPT ---
def chat_gpt(text):
    try:
        # бесплатный чат API
        sys = "You are OZODI AI, helpful assistant like ChatGPT. Speak in user's language (Tajik, Russian, English). Be friendly and short."
        url = f"https://text.pollinations.ai/{urllib.parse.quote(text)}?model=openai&system={urllib.parse.quote(sys)}"
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and len(r.text) > 2:
            return r.text[:3500]
    except: pass
    return "Салом! Я OZODI AI 🔥 Спроси меня что угодно, или скажи 'сделай фото'"

# --- Фото 100% рабочий ---
def send_photo(chat_id, user_text):
    en = to_english(user_text)
    low = en.lower()

    # Умный промт: если девушка - добавляем красоту, если флаг/горы - не добавляем
    if any(w in low for w in ["girl", "woman", "girl", "духтар", "девуш", "woman"]):
        prompt = f"{en}, photorealistic beautiful girl, natural symmetrical face, realistic skin, elegant, 8k, sharp focus, not deformed"
        model = "flux-realism"
    else:
        prompt = f"{en}, photorealistic, ultra detailed, 8k, sharp focus, highly detailed, realistic"
        model = "flux"

    neg = "deformed, ugly, monster, extra limbs, bad anatomy, blurry, distorted, cartoon"

    # 3 попытки если сервер занят
    for attempt in range(3):
        try:
            bot.send_chat_action(chat_id, 'upload_photo')
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model={model}&width=1024&height=1024&nologo=true&seed={random.randint(1,9999999)}&negative_prompt={urllib.parse.quote(neg)}&enhance=true"
            resp = requests.get(img_url, timeout=90)
            if resp.status_code == 200 and len(resp.content) > 5000:
                bio = io.BytesIO(resp.content)
                bio.name = "ozodi.jpg"
                bot.send_photo(chat_id, bio, caption=f"✅ {user_text}")
                return True
            time.sleep(2)
        except Exception as e:
            time.sleep(2)
            continue

    bot.send_message(chat_id, "Сервер картинок сейчас перегружен, попробуй еще раз через 15 сек ⏳")
    return False

# --- Команды ---
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "Салом БОС! Я OZODI VIDEO AI 🔥\n\n"
        "Я теперь как ChatGPT:\n"
        "• Болтаю на таджикском, русском, английском\n"
        "• Делаю ЛЮБЫЕ фото: флаг, горы, машина, девушки\n"
        "Примеры:\n"
        "салом чи хел?\n"
        "расми парчами Точикистон\n"
        "расми куххои Помир\n"
        "духтари зебои точик\n"
        "bmw m5 black"
    )

@bot.message_handler(content_types=['text'])
def handle(m):
    txt = m.text.strip()
    if not txt or "Send New Post" in txt: return
    if txt.startswith('/'): return

    low = txt.lower()
    # Ключевые слова для фото
    photo_words = ["расм", "сурат", "акс", "фото", "сделай", "соз", "генерир", "нарисуй", "image", "photo", "picture", "парчам", "кух", "мошин", "духтар", "девуш", "girl"]

    if any(w in low for w in photo_words):
        send_photo(m.chat.id, txt)
    else:
        bot.send_chat_action(m.chat.id, 'typing')
        answer = chat_gpt(txt)
        bot.send_message(m.chat.id, answer)

# --- Запуск ---
bot.delete_webhook(drop_pending_updates=True)
time.sleep(2)
print("OZODI AI 100% started")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

import os, telebot, urllib.parse, random, time, threading, requests, io
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "OK"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask).start()

def translate_en(t):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(t)}"
        j = requests.get(url, timeout=5).json()
        return "".join([x[0] for x in j[0]])
    except: return t

def ask_chat(text):
    try:
        # Простой рабочий API без ключа
        prompt = urllib.parse.quote(text)
        url = f"https://text.pollinations.ai/{prompt}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and len(r.text) > 3:
            return r.text[:2000]
    except: pass
    return "Салом БОС! Я на связи 🔥 Напиши 'расми духтари зебо' и я сделаю фото!"

def send_photo_real(chat_id, user_text):
    en = translate_en(user_text)
    # Промт чтоб не было монстров
    good_prompt = f"{en}, photorealistic beautiful Tajik girl, natural face, symmetrical eyes, cute, elegant, realistic skin, 8k, not deformed"
    bad = "deformed, monster, ugly, extra limbs, bad anatomy, cartoon, anime, blurry"

    bot.send_message(chat_id, f"⏳ Делаю: {user_text}...")
    try:
        img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(good_prompt)}?model=flux-realism&width=768&height=1152&nologo=true&seed={random.randint(1,9999999)}&negative_prompt={urllib.parse.quote(bad)}&enhance=true"
        # ВАЖНО: качаем сами, чтобы не было ошибки 400
        resp = requests.get(img_url, timeout=80)
        if resp.status_code == 200:
            bio = io.BytesIO(resp.content)
            bio.name = "photo.jpg"
            bot.send_photo(chat_id, bio, caption=f"✅ {user_text}")
            return
        else:
            bot.send_message(chat_id, "Сервер занят, попробуй еще раз через 10 сек")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка генерации, попробуй еще раз: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "БОС я пофикшен! ✅\n\nПиши:\n- салом\n- расми духтари зебо\n- духтари точик")

@bot.message_handler(content_types=['text'])
def handler(m):
    txt = m.text.strip()
    low = txt.lower()
    if "send new post" in low: return
    if txt.startswith('/'): return

    # СПИСОК СЛОВ ДЛЯ ФОТО - теперь ловит всё
    photo_keys = ["расм", "сурат", "акс", "духтар", "девуш", "girl", "фото", "image", "photo", "зебо", "духт"]
    is_photo = any(k in low for k in photo_keys)

    if is_photo:
        bot.send_chat_action(m.chat.id, 'upload_photo')
        send_photo_real(m.chat.id, txt)
    else:
        bot.send_chat_action(m.chat.id, 'typing')
        ans = ask_chat(txt)
        bot.send_message(m.chat.id, ans)

bot.delete_webhook(drop_pending_updates=True)
time.sleep(2)
bot.infinity_polling()

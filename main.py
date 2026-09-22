import os, telebot, urllib.parse, random, time, threading, requests, io
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask).start()

BLOCKED = ["Send New Post to Subscribers"]

def translate_en(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        r = requests.get(url, timeout=5).json()
        return "".join([x[0] for x in r[0]])
    except: return text

def ask_chatgpt(text, chat_id):
    # Делаем как ChatGPT / Gemini - бесплатно через Pollinations
    system = "You are ChatGPT-like AI, friendly, smart. You speak Tajik, Russian, English. Answer in user's language. Keep short."
    try:
        # Используем бесплатный API чата
        url = f"https://text.pollinations.ai/{urllib.parse.quote(text)}"
        params = {"model": "openai", "system": system}
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200 and len(r.text) > 5:
            return r.text
        else:
            return "Салом! Я тут, БОС! Что хочешь спросить?"
    except Exception as e:
        return f"Я тут! Спроси что-нибудь или скажи 'сделай фото девушки'"

def make_photo(chat_id, original):
    en = translate_en(original)
    prompt = f"{en}, photorealistic, beautiful, natural symmetrical face, ultra detailed, 8k realistic photo, sharp, not deformed"
    neg = "deformed, ugly, monster, extra limbs, bad face, cartoon, anime, blurry, distorted"
    try:
        img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model=flux-realism&width=768&height=1152&nologo=true&seed={random.randint(1,999999)}&negative_prompt={urllib.parse.quote(neg)}&enhance=true"
        resp = requests.get(img_url, timeout=70)
        if resp.status_code == 200:
            bot.send_photo(chat_id, io.BytesIO(resp.content), caption=f"✅ {original}")
            return True
    except: pass
    return False

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Салом БОС! Я теперь как ChatGPT + Gemini 🔥\n\nЯ умею:\n1. Болтать на любом языке\n2. Делать фото\n\nНапиши:\n`Салом чи хел?`\n`Кто ты?`\n`Сделай фото красивой таджички`\n`Расм соз духтари зебо`")

@bot.message_handler(content_types=['text'])
def all_text(m):
    txt = m.text
    if any(b.lower() in txt.lower() for b in BLOCKED) or txt.startswith('/'): return
    if len(txt) < 2: return

    # Если просит фото - делаем фото
    photo_words = ["фото", "расм", "сурат", "акс", "image", "photo", "духтар", "девуш", "girl", "соз", "сделай", "генерир", "draw"]
    is_photo = any(w in txt.lower() for w in photo_words)

    if is_photo:
        bot.send_chat_action(m.chat.id, 'upload_photo')
        ok = make_photo(m.chat.id, txt)
        if not ok:
            ans = ask_chatgpt(txt, m.chat.id)
            bot.send_message(m.chat.id, ans)
    else:
        # Просто болтаем как ChatGPT
        bot.send_chat_action(m.chat.id, 'typing')
        answer = ask_chatgpt(txt, m.chat.id)
        bot.send_message(m.chat.id, answer)

bot.delete_webhook(drop_pending_updates=True)
time.sleep(2)
print("ChatGPT Bot zapushen...")
bot.infinity_polling()

import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import uuid
import imageio
import numpy as np
import requests
import urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

Thread(target=run_server, daemon=True).start()
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! Я OZODI AI SUPER BOT 🤖🔥\n\n"
        "Что я умею:\n"
        "1️⃣ Напиши текст - я нарисую ИИ фото (напр: 'свадьба в горах')\n"
        "2️⃣ Отправь фото - я сделаю из него видео 🎬\n"
        "3️⃣ /video твой текст - сделаю сразу ИИ видео!\n\n"
        "Попробуй!"
    )

def generate_ai_image(prompt):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
    r = requests.get(url, timeout=30)
    path = f"/tmp/{uuid.uuid4()}.jpg"
    with open(path, 'wb') as f:
        f.write(r.content)
    return path

def make_video_from_image(img_path, out_path):
    img = Image.open(img_path).convert("RGB")
    img.thumbnail((512, 512))
    w, h = img.size
    w = w - (w % 2)
    h = h - (h % 2)
    img = img.resize((w, h))
    frames = []
    for i in range(30):
        s = 1 + i * 0.02
        nw, nh = int(w*s), int(h*s)
        nw = nw - (nw % 2)
        nh = nh - (nh % 2)
        resized = img.resize((nw, nh))
        l = (nw - w)//2
        t = (nh - h)//2
        cropped = resized.crop((l, t, l+w, t+h))
        frames.append(np.array(cropped))
    imageio.mimsave(out_path, frames, fps=12, macro_block_size=2)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    if prompt.startswith("/video"):
        prompt = prompt.replace("/video","").strip()
        if not prompt:
            await update.message.reply_text("Напиши после /video что нарисовать. Напр: /video горы Таджикистана")
            return
        await update.message.reply_text(f"🎬 Делаю ИИ видео: {prompt} ...")
        try:
            img_path = generate_ai_image(prompt)
            out_path = f"/tmp/{uuid.uuid4()}.mp4"
            make_video_from_image(img_path, out_path)
            await update.message.reply_video(video=open(out_path,'rb'), caption=f"ИИ видео готово! ✅\n{prompt}")
            os.remove(img_path)
            os.remove(out_path)
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {e}")
        return

    # обычный текст -> ИИ фото
    await update.message.reply_text(f"🎨 Рисую: {prompt} ...")
    try:
        img_path = generate_ai_image(prompt)
        await update.message.reply_photo(photo=open(img_path,'rb'), caption=f"ИИ фото готово! ✅\n{prompt}\n\nХочешь видео из него? Отправь это фото мне обратно!")
        os.remove(img_path)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inp = f"/tmp/{uuid.uuid4()}.jpg"
    outp = f"/tmp/{uuid.uuid4()}.mp4"
    try:
        await update.message.reply_text("⏳ Делаю видео из твоего фото...")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(inp)
        make_video_from_image(inp, outp)
        await update.message.reply_video(video=open(outp, 'rb'), caption="Видео сохтан! ✅")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    finally:
        if os.path.exists(inp): os.remove(inp)
        if os.path.exists(outp): os.remove(outp)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CommandHandler("video", text_handler))
app.run_polling()

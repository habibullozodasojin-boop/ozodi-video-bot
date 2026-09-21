import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import uuid
import imageio
import numpy as np

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
    await update.message.reply_text("Салом! Отправь мне фото и я сделаю видео 🎬")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("⏳ Делаю видео...")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        inp = f"/tmp/{uuid.uuid4()}.jpg"
        outp = f"/tmp/{uuid.uuid4()}.mp4"
        await file.download_to_drive(inp)

        img = Image.open(inp).convert("RGB")
        w, h = img.size
        frames = []
        for i in range(30):
            s = 1 + i * 0.015
            nw, nh = int(w*s), int(h*s)
            resized = img.resize((nw, nh))
            l = (nw - w)//2
            t = (nh - h)//2
            cropped = resized.crop((l, t, l+w, t+h))
            frames.append(np.array(cropped))
        
        imageio.mimsave(outp, frames, fps=10, macro_block_size=1)
        await update.message.reply_video(video=open(outp, 'rb'), caption="Видео сохтан! ✅")
        os.remove(inp)
        os.remove(outp)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.run_polling()

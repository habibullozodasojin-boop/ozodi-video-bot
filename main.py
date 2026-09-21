import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image
import uuid

# Фикс для Render Web Service - открывает порт
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("Салом! Отправь мне фото и я сделаю из него видео!")

async def handle_photo(update: Update, context):
    try:
        await update.message.reply_text("Принял фото, делаю видео...")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        uid = str(uuid.uuid4())[:8]
        inp = f"/tmp/{uid}.jpg"
        out = f"/tmp/{uid}.mp4"

        await file.download_to_drive(inp)

        # Делаем видео из фото
        img = Image.open(inp)
        # Создаем кадры с зумом
        frames = []
        for i in range(30):
            scale = 1 + i * 0.02
            w, h = img.size
            new_w, new_h = int(w*scale), int(h*scale)
            resized = img.resize((new_w, new_h))
            left = (new_w - w)//2
            top = (new_h - h)//2
            cropped = resized.crop((left, top, left+w, top+h))
            frames.append(cropped)

        # Сохраняем как mp4 через PIL
        if frames:
            frames[0].save(out, save_all=True, append_images=frames[1:], duration=100, loop=0)
            # Переименовываем в mp4 если нужно, Telegram примет как видео
            await update.message.reply_video(video=open(out, 'rb'))
        else:
            await update.message.reply_text("Ошибка создания видео")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import uuid

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Салом бро! Я - Ozodi Video Bot. Отправь фото и я сделаю видео!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Делаю магию... 10 сек")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        uid = str(uuid.uuid4())[:8]
        inp = f"/tmp/{uid}.jpg"
        out = f"/tmp/{uid}.mp4"
        await file.download_to_drive(inp)
        from moviepy.editor import ImageClip, CompositeVideoClip
        clip = ImageClip(inp).set_duration(6)
        clip = clip.resize(lambda t: 1 + 0.05*t).set_position('center')
        bg = ImageClip(inp).set_duration(6).resize(height=1920).resize(width=1080)
        final = CompositeVideoClip([bg, clip], size=(1080, 1920)).set_duration(6)
        final.write_videofile(out, fps=24, codec='libx264', audio=False, logger=None)
        await update.message.reply_video(video=open(out, 'rb'), caption="Готово бро!")
        os.remove(inp)
        os.remove(out)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()

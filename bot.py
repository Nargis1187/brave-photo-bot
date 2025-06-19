import os
import io
from PIL import Image, ImageDraw, ImageFont
import requests
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8152184531:AAGD9lDOVq64yqrWbdP7R-XzuHc9GuZzSZ4"
REMOVE_BG_KEY = "Zgdmgp94VcWzGC8woY6joX5b"
TEMPLATE_PATH = "template.png"

bot = Bot(token=BOT_TOKEN)

def remove_bg(image_bytes):
    resp = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': image_bytes},
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVE_BG_KEY},
    )
    resp.raise_for_status()
    return io.BytesIO(resp.content)

def process_image(user_img, article):
    bg = Image.open(TEMPLATE_PATH).convert("RGBA")
    fg = Image.open(user_img).convert("RGBA")
    fg.thumbnail((700, 700), Image.LANCZOS)
    x = (bg.width - fg.width) // 2
    y = 100
    bg.paste(fg, (x, y), fg)
    draw = ImageDraw.Draw(bg)
    font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), article, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    tx = (bg.width - text_w) // 2
    ty = bg.height - text_h - 50
    draw.text((tx, ty), article, font=font, fill="black")
    buf = io.BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    return buf

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Кидай фотку товара и артикул в подписи!")
        return
    file = await update.message.photo[-1].get_file()
    photo = await file.download_as_bytearray()
    article = update.message.caption or 'NOARTICLE'
    img_nobg = remove_bg(io.BytesIO(photo))
    out = process_image(img_nobg, article)
    await update.message.reply_photo(photo=out)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption(), handle_msg))
    app.run_polling()

import os
import io
from PIL import Image, ImageDraw, ImageFont
import requests
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

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
    fg.thumbnail((700, 700), Image.ANTIALIAS)

    x = (bg.width - fg.width) // 2
    y = 100
    bg.paste(fg, (x, y), fg)

    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype("arial.ttf", 40)
    text_w, text_h = draw.textsize(article, font=font)
    tx = (bg.width - text_w) // 2
    ty = bg.height - text_h - 50
    draw.text((tx, ty), article, font=font, fill="black")

    buf = io.BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    return buf

def handle_msg(update: Update, ctx: CallbackContext):
    if not update.message.photo:
        update.message.reply_text("Кидай фотку товара и артикул в подписи!")
        return

    photo = update.message.photo[-1].get_file().download_as_bytearray()
    article = update.message.caption or 'NOARTICLE'
    img_nobg = remove_bg(io.BytesIO(photo))
    out = process_image(img_nobg, article)
    update.message.reply_photo(photo=out)

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo & Filters.caption, handle_msg))
    updater.start_polling()_

import os
import logging
import replicate
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا توکنان
TOKEN = os.getenv('BOT_TOKEN')
REPLICATE_API = os.getenv('REPLICATE_API_TOKEN')

# چالاککرنا توکنا Replicate د ناڤ سیستەمی دا
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API if REPLICATE_API else ""

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. پشکا سافیکرنا وێنەیان (Image Enhancement) ---
async def enhance_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not REPLICATE_API:
        await update.message.reply_text("❌ توکنا Replicate نەهاتیە دیتن.")
        return

    m = await update.message.reply_text("⏳ ژیریا دەستکرد کار ل سەر وێنەی دکەت... هیڤییە کێمەکێ چاڤەڕێ بە.")

    try:
        # داونلۆدکرنا وێنەی ژ تلگرامی
        file = await update.message.photo[-1].get_file()
        photo_path = "input_image.jpg"
        await file.download_to_drive(photo_path)

        # رەوانەکرنا وێنەی بۆ Replicate (مۆدێلا CodeFormer)
        with open(photo_path, "rb") as image_file:
            output = replicate.run(
                "sczhou/codeformer:7de2ea4a3562d285371f11f973473b2195e57d84f12d659ad76644b423f07306",
                input={
                    "image": image_file,
                    "upscale": 2,
                    "face_upsample": True,
                    "background_enhance": True
                }
            )

        # فرێکرنا وێنەیێ سافی بو بکارهێنەری
        await update.message.reply_photo(photo=output, caption="✅ وێنەیێ تە ب شێوازەکێ واقعى هاتە سافیکرن.")
        await m.delete()
        
        # رەشکرنا وێنەیێ کاتی
        if os.path.exists(photo_path):
            os.remove(photo_path)

    except Exception as e:
        logging.error(f"Error: {e}")
        await m.edit_text(f"ببورە، کێشەیەک هەبوو. پشتڕاست بە کو ئەکاونتێ تە یێ Replicate یێ کارایه.")

# --- ٢. پشکا دروستکرنا وێنەیێن نوو ---
async def generate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("تکایە وەسفەکێ ب ئینگلیزی بنڤێسه.\nوەک: `/generate a Kurdish man in traditional clothes`", parse_mode='Markdown')
        return

    m = await update.message.reply_text("🎨 وێنەیێ تە دهێتە دروستکرن... کێمەکێ ل هیڤیێ بە.")
    try:
        output = replicate.run(
            "stability-ai/sdxl:7762d33929e21071190c44d57077312f0d18292830f6534570081d596645391d",
            input={"prompt": prompt}
        )
        await update.message.reply_photo(photo=output[0], caption=f"✨ ئەڤە ژی وێنەیێ تە:\n`{prompt}`")
        await m.delete()
    except Exception as e:
        logging.error(e)
        await m.edit_text("ببورە، کێشەیەک هەبوو د دروستکرنا وێنەی دا.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلاڤ! 👋 ب خێر هاتی بۆ بوتێ وێنەیان.\n\n"
        "🖼 **بۆ سافیکرنێ:** وێنەکێ لێل بفرێکه.\n"
        "🎨 **بۆ دروستکرنێ:** فەرمانا /generate دگەل وەسفەکێ بکاربینە."
    )

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرن"),
        BotCommand("generate", "دروستکرنا وێنەی")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, enhance_image))
    
    print("Photo AI Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

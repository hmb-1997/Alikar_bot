import os
import logging
import replicate
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا توکنان
TOKEN = os.getenv('BOT_TOKEN')
REPLICATE_API = os.getenv('REPLICATE_API_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. پشکا سافیکرنا وێنەیان (Image Enhancement) ---
async def enhance_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not REPLICATE_API:
        await update.message.reply_text("ببورە، توکنا Replicate نینە.")
        return

    photo = await update.message.photo[-1].get_file()
    image_url = photo.file_path
    
    m = await update.message.reply_text("⏳ ژیریا دەستکرد کار ل سەر وێنەی دکەت... کێمەکێ ل هیڤیێ بە.")

    try:
        # بەکارئینانا مۆدێلا CodeFormer بۆ سافیکرن و جوانکرنا وێنەی
        output = replicate.run(
            "sczhou/codeformer:7de2ea4a3562d285371f11f973473b2195e57d84f12d659ad76644b423f07306",
            input={"image": image_url, "upscale": 2, "face_upsample": True, "background_enhance": True}
        )
        await update.message.reply_photo(photo=output, caption="✅ وێنەیێ تە ب شێوازەکێ واقعى هاتە سافیکرن.")
        await m.delete()
    except Exception as e:
        logging.error(e)
        await m.edit_text("ببورە، کێشەیەک هەبوو د سافیکرنا وێنەی دا.")

# --- ٢. پشکا دروستکرنا وێنەیێن نوو (AI Image Generation) ---
async def generate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("تکایە وەسفەکێ بنڤێسه. وەک: /generate a realistic house in the mountains")
        return

    m = await update.message.reply_text("🎨 وێنەیێ تە دهێتە دروستکرن...")
    try:
        # بەکارئینانا مۆدێلا Stable Diffusion بۆ دروستکرنا وێنەی
        output = replicate.run(
            "stability-ai/sdxl:7762d33929e21071190c44d57077312f0d18292830f6534570081d596645391d",
            input={"prompt": prompt}
        )
        await update.message.reply_photo(photo=output[0], caption="✨ ئەڤە ژی وێنەیێ تە.")
        await m.delete()
    except:
        await m.edit_text("کێشەیەک هەبوو.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلاڤ! 👋\nوێنەکێ لێل (Blurry) بفرێکه دا بۆ تە سافی بکەم، یان فەرمانا /generate بەکاربینە بۆ دروستکرنا وێنەی.")

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
    
    # هەر وێنەیەک بفرێخن، بوت دێ سافی کەت
    app.add_handler(MessageHandler(filters.PHOTO, enhance_image))
    
    print("Photo AI Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

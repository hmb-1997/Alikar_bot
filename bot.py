import os
import logging
import requests
import io
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا توکنا بوتێ تلگرامی
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. فۆنکشنا دروستکرنا وێنەی (AI Generation) ---
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # کۆمکرنا وەسفێ بکارهێنەری
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("تکایە وەسفەکێ ب ئینگلیزی بنڤێسه.\nنموونه: `/generate a futuristic city in Kurdistan`", parse_mode='Markdown')
        return

    m = await update.message.reply_text("🎨 ژیریا دەستکرد کار ل سەر وێنەیێ تە دکەت... کێمەکێ چاڤەڕێ بە.")

    try:
        # بەکارئینانا API یا بێبەرامبەر یا Pollinations
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
        
        # فرێکرنا وێنەی بۆ تلگرامی ب رێکا لینکی
        await update.message.reply_photo(photo=image_url, caption=f"✨ ئەڤە ژی وێنەیێ تە ل سەر وەسفێ:\n`{prompt}`", parse_mode='Markdown')
        await m.delete()
    except Exception as e:
        logging.error(e)
        await m.edit_text("ببورە، کێشەیەک هەبوو د دروستکرنا وێنەی دا.")

# --- ٢. فۆنکشنا سافیکرنا وێنەی (Image Enhancement) ---
# تێبینی: چونکی سافیکرن پێدڤی ب سێرڤەرێن گران هەیە، ئەز دێ رێکەکا فێڵبازی (Filter) بۆ دانم
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ سوپاس بۆ وێنەی! ئەز نوکە وەک بوتەکێ زیرەک دشێم وێنەیان دروست بکەم. بۆ دروستکرنێ فەرمانا /generate بەکاربینە.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سڵاڤ! 👋 ب خێر هاتی بۆ بوتێ ژیریا دەستکرد.\n\n"
        "🎨 **بۆ دروستکرنا هەر وێنەیەکی:**\n"
        "فەرمانا /generate بەکاربینە و وەسفێ خۆ ب ئینگلیزی بنڤێسه.\n\n"
        "نموونه:\n`/generate a cute cat in a hat`",
        parse_mode='Markdown'
    )

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرن"),
        BotCommand("generate", "دروستکرنا وێنەی ب AI")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_image))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    
    print("AI Image Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

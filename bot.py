import os
import logging
import requests
import urllib.parse
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا تۆکنێ
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- فۆنکشنا دروستکرنا وێنەیێن ب هێز (AI Generation) ---
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("✨ **تکایە وەسفەکێ بنڤێسه.**\nنموونه: `/ai a realistic Kurdish man in traditional clothes, 4k high detail`", parse_mode='Markdown')
        return

    m = await update.message.reply_text("🚀 **ژیریا دەستکرد دەست ب کار بوو... کێمەکێ ل هیڤیێ بە.**")

    try:
        # بەکارئینانا مۆدێلا FLUX کو نوکە ب هێزترین مۆدێلا جیهانییە
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
        
        # فرێکرنا وێنەی ب کوالیتیا بەرز
        await update.message.reply_photo(
            photo=image_url, 
            caption=f"✅ **وێنەیێ تە ئامادەیە**\n📝 وەسف: `{prompt}`",
            parse_mode='Markdown'
        )
        await m.delete()
    except Exception as e:
        logging.error(e)
        await m.edit_text("ببورە، سێرڤەر نوکە یێ قەلەبالغە. دووبارە تاقی بکەوه.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **سڵاڤ! ب خێر هاتی بۆ بوتێ فۆتۆشۆپا زیرەک (AI).**\n\n"
        "🎨 ئەز دشێم هەر وێنەیەکێ د سەرێ تە دا بیت دروست بکەم.\n"
        "تەنێ فەرمانا `/ai` بنڤێسه و وەسفەکێ ب ئینگلیزی بدە.\n\n"
        "نموونه:\n`/ai a futuristic car in the streets of Duhok`",
        parse_mode='Markdown'
    )

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرن"),
        BotCommand("ai", "دروستکرنا وێنەی ب AI")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ai", generate_image))
    
    print("AI Photoshop Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

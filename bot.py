import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا تۆکنی ژ ڕێلوەی
TOKEN = os.getenv('BOT_TOKEN')

# رێکخستنا لۆگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. فرمانێن سەرەکی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"سلاڤ {user_name} برايێ هێژا 👋\n"
        "بخێر هاتی بۆ بوتێ **ئالیکارێ بادینان**.\n\n"
        "📜 **فرمانێن سەرەکی:**\n"
        "💰 /currency - بهایێ دراڤی\n"
        "🕌 /prayer - دەمێن بانگی\n"
        "🌤 /weather - کێشوهەوا\n"
        "🎓 /education - قوتابی و مەلازێم\n"
        "📖 /adhkar - زیکر و ئایین\n"
        "🔄 /translate - رێنماییا وەرگێڕانێ"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# --- ٢. فرمانێن خزمەتگۆزاری ---

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "💰 **بهایێ دراڤی ل بازاڕێن بادینان:**\n\n💵 100 دۆلار ⮕ 150,500 دینار\n🇮🇷 1 ملیۆن تمەن ⮕ 2,450 دینار\n🇹🇷 100 لێرە ⮕ 4,400 دینار"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🕌 **دەمێن بانگی ل دهۆکێ:**\n\n🌅 سپێدە: 04:35\n☀️ نیڤڕۆ: 12:12\n🌆 ئێڤاری: 03:48\n🌙 مەغرب: 06:35\n🌌 عیشا: 07:55"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🌤 **کەشوهەوا ل دەڤەرا بادینان:**\n\n📍 دهۆک: 32°C\n📍 زاخۆ: 34°C\n📍 ئامێدی: 28°C"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔗 ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎓 **پشکا قوتابیان:**\nبۆ دیتنا ئەنجامان کلیک بکە.", reply_markup=reply_markup)

async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📖 **زیکرێن رۆژانە:**\n\n🔹 زیکرێ سپێدێ\n🔹 زیکرێ ئێڤاری\n\n🌙 *هەر رۆژ دێ چیرۆکەکا ئایینی هێتە بەلاڤکرن.*"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def translate_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 **خزمەتگۆزاریا وەرگێڕانێ:**\nتەنێ پەیڤ یان رستەکێ ب بادینی یان هەر زمانەکێ دی بۆ من فرێبکه، ئەز دێ دەملدەست بۆ تە وەرگێڕمە سەر عەرەبی و ئینگلیزی.")

# --- ٣. مێشکێ وەرگێڕانێ (Handling Translation) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # نیشاندانا نامەیا (جارێ چەبکە...) دا بکارهێنەر چەبیت
    waiting_msg = await update.message.reply_text("⏳ ل هیڤیێ بە، دهێتە وەرگێڕان...")

    try:
        # وەرگێڕان بۆ عەرەبی و ئینگلیزی
        # تێبینی: 'auto' دێ ب خۆ زمانێ دەقی ناسیت (بادینی بیت یان هەر تشتەک)
        translated_ar = GoogleTranslator(source='auto', target='ar').translate(user_text)
        translated_en = GoogleTranslator(source='auto', target='en').translate(user_text)

        result = (
            f"✅ **ئەنجامێ وەرگێڕانێ:**\n\n"
            f"🇸🇦 **عەرەبی:**\n`{translated_ar}`\n\n"
            f"🇺🇸 **ئینگلیزی:**\n`{translated_en}`"
        )
        await waiting_msg.edit_text(result, parse_mode='Markdown')
    
    except Exception as e:
        await waiting_msg.edit_text("ببورە، کێشەیەک د وەرگێڕانێ دا چێبوو. دووبارە تاقی بکەوه.")

# --- دەستپێکرنا بوتی ---

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    app = Application.builder().token(TOKEN).build()

    # فرمانێن Slash
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))
    app.add_handler(CommandHandler("translate", translate_info))

    # هەر نامەیەکا دەقی بیت و فرمان نەبیت، دێ وەرگێڕیت
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

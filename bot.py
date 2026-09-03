import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا تۆکنی ژ ڕێلوەی
TOKEN = os.getenv('BOT_TOKEN')

# رێکخستنا لۆگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- پشکا رێکخستنا لیستا فرمانان (Menu Commands) ---
async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی (دۆلار، تمەن)"),
        BotCommand("prayer", "دەمێن بانگی ل دهۆکێ"),
        BotCommand("weather", "کەشوهەوا ل بادینان"),
        BotCommand("education", "پشکا قوتابی و مەلازێمان"),
        BotCommand("adhkar", "زیکر و بابەتێن ئایینی"),
        BotCommand("translate", "رێنماییا وەرگێڕانێ")
    ]
    await application.bot.set_my_commands(commands)

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
    await update.message.reply_text("🔄 **خزمەتگۆزاریا وەرگێڕانێ:**\nتەنێ پەیڤ یان رستەکێ بنڤێسه، ئەز دێ بۆ تە وەرگێڕمە سەر عەرەبی و ئینگلیزی.")

# --- ٣. مێشکێ وەرگێڕانێ ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    waiting_msg = await update.message.reply_text("⏳ ل هیڤیێ بە، دهێتە وەرگێڕان...")

    try:
        # وەرگێڕان ب بەکارهێنانی 'ku' بۆ کوردی
        translated_ar = GoogleTranslator(source='ku', target='ar').translate(user_text)
        translated_en = GoogleTranslator(source='ku', target='en').translate(user_text)

        result = (
            f"✅ **ئەنجامێ وەرگێڕانێ:**\n\n"
            f"🇸🇦 **ب عەرەبی:**\n`{translated_ar}`\n\n"
            f"🇺🇸 **ب ئینگلیزی:**\n`{translated_en}`"
        )
        await waiting_msg.edit_text(result, parse_mode='Markdown')
    
    except Exception as e:
        logging.error(f"Translation Error: {e}")
        await waiting_msg.edit_text("ببورە، کێشەیەک د وەرگێڕانێ دا چێبوو.")

# --- دەستپێکرنا بوتی ---

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    # ل ڤێرە post_init هاتیە زێدەکرن بۆ رێکخستنا لیستا فرمانان
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))
    app.add_handler(CommandHandler("translate", translate_info))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running with Menu Commands...")
    app.run_polling()

if __name__ == '__main__':
    main()

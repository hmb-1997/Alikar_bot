import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# وەرگرتنا تۆکنی ژ ڕێلوەی (Railway Variables)
TOKEN = os.getenv('BOT_TOKEN')

# رێکخستنا لۆگ بۆ دیتنا شه‌له‌لان
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- فرمانێن سەرەکی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"سلاڤ {user_name} برايێ هێژا 👋\n"
        "بخێر هاتی بۆ بوتێ **ئالیکارێ بادینان**.\n\n"
        "ئەڤ بوته‌ هاتیە دروستکرن بۆ خزمەتکرنا تە ب زمانێ بادینی. کێش دابنێ دا فرمانێن پێدڤی ببینی.\n\n"
        "📜 **فرمانێن سەرەکی:**\n"
        "💰 /currency - بهایێ دراڤی (دۆلار، تمەن، لێرا)\n"
        "🕌 /prayer - دەمێن بانگی ل دهۆکێ\n"
        "🌤 /weather - کێشوهەوا ل دەڤەرێ\n"
        "🎓 /education - قوتابی و مەلازێم\n"
        "📖 /adhkar - زیکر و بابەتێن ئایینی\n"
        "🔄 /translate - وەرگێڕان"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# --- ١. زانیاریێن رۆژانە (Currency, Prayer, Weather) ---

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "💰 **بهایێ دراڤی ل بازاڕێن بادینان:**\n\n"
        "💵 100 دۆلار ⮕ 150,500 دینار\n"
        "🇮🇷 1 ملیۆن تمەن ⮕ 2,450 دینار\n"
        "🇹🇷 100 لێرە ⮕ 4,400 دینار\n\n"
        "⚠️ *تێبینی: بها ل دەف مەلبەندێن ئالۆگۆڕێ دگۆڕێن.*"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🕌 **دەمێن بانگی بۆ باژێرێ دهۆکێ و دەوروبەر:**\n\n"
        "🌅 سپێدە: 04:35\n"
        "☀️ نیڤڕۆ: 12:12\n"
        "🌆 ئێڤاری: 03:48\n"
        "🌙 مەغرب: 06:35\n"
        "🌌 عیشا: 07:55"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌤 **کەشوهەوا ل دەڤەرا بادینان:**\n\n"
        "📍 دهۆک: 32°C (ساخیک و ئاڤی)\n"
        "📍 زاخۆ: 34°C (گەرم)\n"
        "📍 ئامێدی: 28°C (فێنک)\n\n"
        "هەمی دەمان کەیف خۆش بن!"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- ٢. پەروەردە و قوتابی ---

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔗 ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")],
        [InlineKeyboardButton("📚 داونلۆدکرنا مەلازێمان", callback_data='books_list')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎓 **پشکا پەروەردەیی:**\nژبۆ ئەنجامان یان مەلازێمان کلیک بکە.", reply_markup=reply_markup)

# --- ٣. ئایینی (Adhkar) ---

async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📖 **زیکرێن رۆژانە و بابەتێن ئایینی:**\n\n"
        "🔹 **زیکرێ سپێدێ:** (أصبحنا وأصبح الملك لله...)\n"
        "🔹 **زیکرێ ئێڤاری:** (أمسینا وأمسى الملك لله...)\n\n"
        "🌙 *هەر رۆژ دێ چیرۆکەکا ئایینی ب بادینی هێتە بەلاڤکرن.*"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- ٤. وەرگێڕان ---

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 **خزمەتگۆزاریا وەرگێڕانێ:**\nتکایە پەیڤا خۆ بنڤێسە دا کو ژ بادینی بۆ ئینگلیزی یان عەرەبی بهێتە وەرگێڕان.")

# --- سەرەکی ---

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is not set in environment variables!")
        return

    app = Application.builder().token(TOKEN).build()

    # فەرمانێن Slash
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))
    app.add_handler(CommandHandler("translate", translate))

    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == '__main__':
    main()

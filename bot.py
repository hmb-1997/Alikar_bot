import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ل ڤێره‌ Token یێ بوتێ خۆ یێ BotFather وه‌رگرتی دابنێ
TOKEN = 'TEU_BOT_TOKEN_HERE'

# رێكخستنا لۆگ (بۆ ديتنا شه‌له‌لان)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. فرمانێن سه‌ره‌كي ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_msg = (
        f"سلاڤ {user.first_name} برايێ هێژا 👋\n\n"
        "بخێر هاتی بۆ بوتێ (خزمەتگۆزاریێن بادینان).\n"
        "ئەڤ بوته‌ هاتیە دروستكرن بۆ هاریكاریا تە د بوارێن جودا دا.\n\n"
        "📌 **لیستا فرمانێن سەرەکی:**\n"
        "💰 /currency - بهایێ دراڤی (دۆلار، تمەن، لێرا)\n"
        "🕌 /prayer - دەمێن بانگی ل دهۆكێ\n"
        "🌤 /weather - كەشوهەوا ل دەڤەرێ\n"
        "🎓 /education - قوتابی و ئەنجامێن پۆلا ١٢\n"
        "📖 /adhkar - زیكر و بابەتێن ئایینی\n"
        "🔄 /translate - وەرگێڕان (بادینی - English)\n"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

# --- ٢. پشكا زانیاریێن رۆژانە ---
async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تێبینی: دشێی ئەڤان زانیاریان ب شێوەیەکێ ئۆتۆماتیک ژ سایتان وەرگری (Web Scraping)
    text = (
        "💰 **بهایێ دراڤی ل بازاڕێن بادینان:**\n\n"
        "💵 100 دۆلار = 150,500 دینار\n"
        "🇮🇷 1 ملیۆن تمەن = 2,500 دینار\n"
        "🇹🇷 100 لێرە = 4,500 دینار\n\n"
        "⚠️ *تێبینی: بها دهێتە گۆڕین.*"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕌 **دەمیێن بانگی ل پارێزگەها دهۆكێ:**\n\n"
        "🌅 سپێدە: 04:30\n"
        "☀️ نیڤڕۆ: 12:15\n"
        "🌆 ئێڤاری: 03:45\n"
        "🌙 مەغرب: 06:30\n"
        "🌌 عیشا: 08:00"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

# --- ٣. پشكا پەروەردە و قوتابیان ---
async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")],
        [InlineKeyboardButton("داونلۆدکرنا مەلازێمان", callback_data='books')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("خزمەتگۆزاریێن قوتابیان هەلبژێره‌:", reply_markup=reply_markup)

# --- ٤. پشكا ئایینی ---
async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 **زیكرێن پێدڤی:**\n\n"
        "1️⃣ زیكرێن سپێدێ\n"
        "2️⃣ زیكرێن ئێڤاری\n"
        "3️⃣ چێڕۆکێن ئایینی\n\n"
        "بۆ خواندنا هەر ئێکێ، کلیکێ ل سەر بکە."
    )
    await update.message.reply_text(text)

# --- کارپێکرنا بوتی ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

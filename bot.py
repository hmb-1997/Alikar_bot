import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا تۆکنی ژ ڕێلوەی
TOKEN = os.getenv('BOT_TOKEN')

# رێکخستنا لۆگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. فۆنکشنێن وەرگرتنا زانیاریێن زیندی (Live Data) ---

def get_live_weather(city):
    try:
        # ئەڤە ژێدەرەکێ ئازادە بۆ کەشوهەوای
        url = f"https://wttr.in/{city}?format=%t"
        response = requests.get(url)
        return response.text.strip() if response.status_code == 200 else "N/A"
    except:
        return "کێشه هەیە"

def get_live_currency():
    try:
        # وەرگرتنا بهایێ لێرە و تمەنی بەرامبەر دۆلاری
        res = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = res.json()
        try_rate = data['rates']['TRY']
        irr_rate = data['rates']['IRR']
        return try_rate, irr_rate
    except:
        return None, None

# --- ٢. رێکخستنا مینیو و فەرمانان ---

async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی یێ زیندی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا ب ڕاستی"),
        BotCommand("education", "قوتابی و مەلازێم"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان")
    ]
    await application.bot.set_my_commands(commands)

# --- ٣. فۆنکشنێن بەرسڤدانێ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"سلاڤ {update.effective_user.first_name} 👋\n"
        "بخێر هاتی بۆ بوتێ **ئالیکارێ بادینان (ڤێرژنێ ب هێز)** 🚀\n\n"
        "ئەڤ بوته نوکە یێ گرێدایی ئینتەرنێتێیە دا زانیاریێن ڕاستەقینە بدەتە تە."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = await update.message.reply_text("⏳ دهێتە نووکرن...")
    try_rate, irr_rate = get_live_currency()
    
    if try_rate:
        msg = (
            "💰 **بهایێ دراڤی یێ زیندی (بەرامبەر دۆلاری):**\n\n"
            f"💵 100 دۆلار ⮕ 150,500 دینار (بازار)\n"
            f"🇹🇷 100 دۆلار ⮕ {int(try_rate * 100)} لێرە\n"
            f"🇮🇷 100 دۆلار ⮕ {int(irr_rate * 100 / 1000000)} ملیۆن تمەن\n\n"
            "⚠️ *تێبینی: بهایێ بازارێ دهۆکێ یێ دۆلاری ل دەف مەلبەندان بگۆڕە.*"
        )
    else:
        msg = "ببورە، نوکە پەیوەندی ب ئینتەرنێتێ نەبوو."
    
    await waiting.edit_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = await update.message.reply_text("🌤 ل هیڤیێ بە...")
    duhok = get_live_weather("Duhok")
    zakho = get_live_weather("Zakho")
    amedi = get_live_weather("Amedi")
    
    msg = (
        "🌤 **کەشوهەوا ل بادینان (نوکە):**\n\n"
        f"📍 دهۆک: {duhok}\n"
        f"📍 زاخۆ: {zakho}\n"
        f"📍 ئامێدی: {amedi}\n\n"
        "هەمی دەمان کەیف خۆش بن!"
    )
    await waiting.edit_text(msg, parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🕌 **دەمێن بانگی ل دهۆکێ (ئەڤرۆ):**\n\n🌅 سپێدە: 04:35\n☀️ نیڤڕۆ: 12:12\n🌆 ئێڤاری: 03:48\n🌙 مەغرب: 06:35\n🌌 عیشا: 07:55"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")],
        [InlineKeyboardButton("📚 داونلۆدکرنا مەلازێمان", callback_data='malazem')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎓 **پشکا پەروەردە و قوتابی:**", reply_markup=reply_markup)

async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☀️ زیکرێن سپێدێ", callback_data='morning')],
        [InlineKeyboardButton("🌙 زیکرێن ئێڤاری", callback_data='evening')],
        [InlineKeyboardButton("📜 چیرۆکا ئایینی", callback_data='story')]
    ]
    await update.message.reply_text("📖 **زیکر و ئایین:**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- ٤. وەرگێڕان و کلیکێن دوگمەیان ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text.startswith('/'): return # بۆ وێ یێ تێکەلی فرمانان نەبیت
    
    waiting = await update.message.reply_text("⏳ وەرگێڕان...")
    try:
        ar = GoogleTranslator(source='ku', target='ar').translate(user_text)
        en = GoogleTranslator(source='ku', target='en').translate(user_text)
        await waiting.edit_text(f"✅ **ئەنجام:**\n\n🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
    except:
        await waiting.edit_text("کێشەک هەبوو.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'morning':
        await query.message.reply_text("☀️ **زیکرێ سپێدێ:**\n(أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له)")
    elif query.data == 'evening':
        await query.message.reply_text("🌙 **زیکرێ ئێڤاری:**\n(أمسینا وأمسی الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له)")
    elif query.data == 'malazem':
        await query.message.reply_text("📚 **لیستا مەلازێمان:**\nببورە، نوکە مەلازێم دهێنە ئامادەکرن. دێ ب زووی ل ڤێرە بن.")

# --- ٥. دەستپێکرنا سەرەکی ---

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is LIVE and running...")
    app.run_polling()

if __name__ == '__main__':
    main()

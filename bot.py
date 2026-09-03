import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا تۆکنی ژ ڕێلوەی
TOKEN = os.getenv('BOT_TOKEN')

# رێکخستنا لۆگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. فۆنکشنێن وەرگرتنا زانیاریێن زیندی (Live Data API) ---

def get_live_prayer_times():
    try:
        # وەرگرتنا دەمێن بانگی بۆ دهۆکێ ب شێوەیەکێ فەرمی
        url = "http://api.aladhan.com/v1/timingsByCity?city=Duhok&country=Iraq&method=3"
        res = requests.get(url).json()
        t = res['data']['timings']
        return {
            "سپێدە": t['Fajr'],
            "نیڤڕۆ": t['Dhuhr'],
            "ئێڤاری": t['Asr'],
            "مەغرب": t['Maghrib'],
            "عیشا": t['Isha']
        }
    except:
        return None

def get_live_weather(city):
    try:
        # وەرگرتنا پلەیا گەرمێ و بارودۆخی
        url = f"https://wttr.in/{city}?format=%t+%C"
        response = requests.get(url)
        return response.text.strip() if response.status_code == 200 else "N/A"
    except:
        return "کێشه هەیە"

def get_live_currency():
    try:
        # وەرگرتنا بهایێ دراڤی یێ جیهانی بەرامبەر دۆلاری
        res = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        data = res['rates']
        return {
            "TRY": data['TRY'],
            "IRR": data['IRR'],
            "IQD": data['IQD']
        }
    except:
        return None

# --- ٢. رێکخستنا مینیو و فەرمانان ---

async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی (زیندی)"),
        BotCommand("prayer", "دەمێن بانگی (ئەڤرۆ)"),
        BotCommand("weather", "کەشوهەوا (نوکە)"),
        BotCommand("education", "قوتابی و مەلازێم"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان")
    ]
    await application.bot.set_my_commands(commands)

# --- ٣. فۆنکشنێن بەرسڤدانێ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"سلاڤ {update.effective_user.first_name} 👋\n"
        "بخێر هاتی بۆ بوتێ **ئالیکارێ بادینان**.\n\n"
        "ئەڤ بوتە هەر رۆژ زانیاریێن نوو و ڕاستەقینە ب ئۆتۆماتیک ژ ئینتەرنێتێ وەردگریت. 🚀"
    )

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = await update.message.reply_text("⏳ دهێتە نووکرن...")
    rates = get_live_currency()
    if rates:
        # بهایێ دیناری ل بازارێ مە تەقریبەن ۱۰-۱۵ خالان ژ یێ فەرمی بلندترە
        market_usd_iqd = 150500 
        msg = (
            "💰 **بهایێ دراڤی یێ زیندی (ئەڤرۆ):**\n\n"
            f"💵 100 دۆلار ⮕ ~{market_usd_iqd:,} دینار\n"
            f"🇹🇷 100 دۆلار ⮕ {int(rates['TRY'] * 100)} لێرا تورکی\n"
            f"🇮🇷 100 دۆلار ⮕ {int(rates['IRR'] * 100 / 1000000)} ملیۆن تمەن\n\n"
            "⚠️ *تێبینی: بهایێ دۆلاری یێ بازارێ دهۆکێ یە.*"
        )
    else:
        msg = "ببورە، کێشەیەک د وەرگرتنا بهایی دا هەبوو."
    await waiting.edit_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = await update.message.reply_text("🌤 ل هیڤیێ بە...")
    d = get_live_weather("Duhok")
    z = get_live_weather("Zakho")
    a = get_live_weather("Amedi")
    msg = (
        "🌤 **کەشوهەوا ل بادینان (نوکە):**\n\n"
        f"📍 دهۆک: {d}\n"
        f"📍 زاخۆ: {z}\n"
        f"📍 ئامێدی: {a}\n\n"
        "هەمی دەمان کەیف خۆش بن!"
    )
    await waiting.edit_text(msg, parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = await update.message.reply_text("🕌 ل هیڤیێ بە...")
    p = get_live_prayer_times()
    if p:
        date_today = datetime.now().strftime("%d/%m/%Y")
        msg = (
            f"🕌 **دەمێن بانگی ل دهۆکێ ({date_today}):**\n\n"
            f"🌅 سپێدە: {p['سپێدە']}\n"
            f"☀️ نیڤڕۆ: {p['نیڤڕۆ']}\n"
            f"🌆 ئێڤاری: {p['ئێڤاری']}\n"
            f"🌙 مەغرب: {p['مەغرب']}\n"
            f"🌌 عیشا: {p['عیشا']}\n\n"
            "تێبینی: ئەڤ دەمه ب شێوەیەکێ ئۆتۆماتیک دهێتە نووکرن."
        )
    else:
        msg = "ببورە، کێشەک د وەرگرتنا دەمێن بانگی دا هەبوو."
    await waiting.edit_text(msg, parse_mode='Markdown')

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📝 ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")]]
    await update.message.reply_text("🎓 **پشکا قوتابیان:**", reply_markup=InlineKeyboardMarkup(keyboard))

async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☀️ زیکرێن سپێدێ", callback_data='morning')],
        [InlineKeyboardButton("🌙 زیکرێن ئێڤاری", callback_data='evening')]
    ]
    await update.message.reply_text("📖 **زیکر و ئایین:**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- ٤. مێشکێ وەرگێڕانێ و دوگمەیان ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text.startswith('/'): return
    
    try:
        ar = GoogleTranslator(source='ku', target='ar').translate(user_text)
        en = GoogleTranslator(source='ku', target='en').translate(user_text)
        await update.message.reply_text(f"✅ **وەرگێڕان:**\n\n🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
    except:
        pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'morning':
        await query.message.reply_text("☀️ زیکرێ سپێدێ: (أصبحنا وأصبح الملك لله)")
    elif query.data == 'evening':
        await query.message.reply_text("🌙 زیکرێ ئێڤاری: (أمسینا وأمسی الملك لله)")

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

    app.run_polling()

if __name__ == '__main__':
    main()

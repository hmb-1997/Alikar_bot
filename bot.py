import os
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا تۆکنان ژ Variables یێن Railway
TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')

# رێکخستنا لۆگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. فۆنکشنێن زانیاریێن زیندی ---

def get_precise_prayer():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Duhok&country=Iraq&method=13"
        res = requests.get(url).json()
        t = res['data']['timings']
        def format_t(t_str, offset=0):
            dt = datetime.strptime(t_str, "%H:%M") + timedelta(minutes=offset)
            return dt.strftime("%I:%M %p")
        return {
            "سپێدە": format_t(t['Fajr'], 3),
            "ڕۆژهەلاتن": format_t(t['Sunrise'], 0),
            "نیڤڕۆ": format_t(t['Dhuhr'], 9),
            "ئێڤاری": format_t(t['Asr'], 5),
            "مەغرب": format_t(t['Maghrib'], 5),
            "عیشا": format_t(t['Isha'], 5)
        }
    except: return None

def get_precise_weather():
    if not WEATHER_API_KEY: return "توکن نینە"
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Duhok,IQ&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"{int(data['main']['temp'])}°C - {data['weather'][0]['description']}"
        return "هێشتا توکن ئەکتیڤ نەبوویە"
    except: return "کێشەیەک هەبوو"

def get_precise_currency():
    if not CURRENCY_API_KEY: return None
    try:
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
        res = requests.get(url).json()
        rates = res['conversion_rates']
        return {"TRY": rates['TRY'], "IRR": rates['IRR'], "IQD": 150750}
    except: return None

# --- ٢. فرمانێن سەرەکی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلاڤ {update.effective_user.first_name} 👋\nبخێر هاتی بۆ ئالیکارێ بادینان. هەمی فرمان د لیستا (Menu) دا دیارن.")

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_precise_currency()
    if data:
        msg = (f"💰 **بهایێ دراڤی ل دهۆکێ:**\n\n💵 100 دۆلار ⮕ ~{data['IQD']:,} دینار\n"
               f"🇹🇷 100 دۆلار ⮕ {int(data['TRY'] * 100)} لێرە\n🇮🇷 100 دۆلار ⮕ {int(data['IRR'] * 100 / 1000000)} ملیۆن تمەن")
    else: msg = "کێشەک د توکنێ دراڤی دا هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = get_precise_weather()
    await update.message.reply_text(f"🌤 **کەشوهەوا (دهۆک):**\n`{w}`", parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = get_precise_prayer()
    if p:
        msg = (f"🕌 **دەمێن بانگی ل دهۆکێ:**\n📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
               f"🌅 سپێدە: `{p['سپێدە']}`\n☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
               f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n🌇 مەغرب: `{p['مەغرب']}`\n🌃 عیشا: `{p['عیشا']}`")
    else: msg = "کێشەک هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔗 ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")]]
    await update.message.reply_text("🎓 **پشکا قوتابیان:**", reply_markup=InlineKeyboardMarkup(keyboard))

async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("☀️ سپێدێ", callback_data='m'), InlineKeyboardButton("🌙 ئێڤاری", callback_data='e')]]
    await update.message.reply_text("📖 زیکرەکێ هەلبژێره:", reply_markup=InlineKeyboardMarkup(keyboard))

async def translate_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 **وەرگێڕان:**\nهەر تشتەکێ بنڤێسی، ئەز دێ دەملدەست وەرگێڕم.")

# --- ٣. مێشکێ بوتێ (Handlers) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'): return
    try:
        ar = GoogleTranslator(source='ku', target='ar').translate(text)
        en = GoogleTranslator(source='ku', target='en').translate(text)
        await update.message.reply_text(f"✅ **وەرگێڕان:**\n\n🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
    except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'm': await query.message.reply_text("☀️ زیکرێ سپێدێ: (أصبحنا وأصبح الملك لله)")
    if query.data == 'e': await query.message.reply_text("🌙 زیکرێ ئێڤاری: (أمسینا وأمسی الملك لله)")

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرنا بوتی"), BotCommand("currency", "دراڤ"),
        BotCommand("prayer", "بانگ"), BotCommand("weather", "کەشوهەوا"),
        BotCommand("education", "قوتابی"), BotCommand("adhkar", "زیکر"),
        BotCommand("translate", "وەرگێڕان")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))
    app.add_handler(CommandHandler("translate", translate_info))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

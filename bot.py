import os
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا توکنان ژ Railway
TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')

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
            return f"{int(data['main']['temp'])}°C - {data['weather'][0]['main']}"
        return "ل هیڤیا ئەکتیڤبوونا توکنێ بە"
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
    user = update.effective_user.first_name
    await update.message.reply_text(f"سلاڤ {user} 👋\nبخێر هاتی بۆ ئالیکارێ بادینان. هەر تشتەکێ بنڤێسی ئەز دێ بۆ تە وەرگێڕم.")

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = get_precise_prayer()
    if p:
        msg = (f"🕌 **دەمێن بانگی ل دهۆکێ:**\n📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
               f"🌅 سپێدە: `{p['سپێدە']}`\n☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
               f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n🌇 مەغرب: `{p['مەغرب']}`\n🌃 عیشا: `{p['عیشا']}`")
    else: msg = "کێشەک هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_precise_currency()
    if data:
        msg = (f"💰 **بهایێ دراڤی ل دهۆکێ:**\n\n💵 100 دۆلار ⮕ ~{data['IQD']:,} دینار\n"
               f"🇹🇷 100 دۆلار ⮕ {int(data['TRY'] * 100)} لێرە\n🇮🇷 100 دۆلار ⮕ {int(data['IRR'] * 100 / 1000000)} ملیۆن تمەن")
    else: msg = "کێشەک د توکنێ دراڤی دا هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = get_precise_weather()
    await update.message.reply_text(f"🌤 **کەشوهەوا (دهۆک):**\n`{w}`", parse_mode='Markdown')

async def translate_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 **وەرگێڕان:**\nپێدڤی ب چ فرمانان نینە، تەنێ هەر تشتەکێ تە دڤێت بنڤێسه و بفرێکه، ئەز دێ دەملدەست وەرگێڕم.")

# --- ٣. مێشکێ وەرگێڕانێ ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'): return
    
    waiting = await update.message.reply_text("⏳ دهێتە وەرگێڕان...")
    try:
        translated_ar = GoogleTranslator(source='ku', target='ar').translate(text)
        translated_en = GoogleTranslator(source='ku', target='en').translate(text)
        result = (f"✅ **ئەنجامێ وەرگێڕانێ:**\n\n🇸🇦 **عەرەبی:**\n`{translated_ar}`\n\n🇺🇸 **ئینگلیزی:**\n`{translated_en}`")
        await waiting.edit_text(result, parse_mode='Markdown')
    except:
        await waiting.edit_text("ببوره، کێشەیەک د وەرگێڕانێ دا هەبوو.")

# --- ٤. دوگمە و رێکخستنا مینیو ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'm': await query.message.reply_text("☀️ زیکرێ سپێدێ: (أصبحنا وأصبح الملك لله)")
    if query.data == 'e': await query.message.reply_text("🌙 زیکرێ ئێڤاری: (أمسینا وأمسی الملك لله)")

async def post_init(application: Application):
    # ل ڤێرە فەرمانا translate زێدە بوو دا د مینیو دا دیار بیت
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("translate", translate_help))
    app.add_handler(CommandHandler("adhkar", lambda u, c: u.message.reply_text("📖 زیکرەکێ هەلبژێره:", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("☀️ سپێدێ", callback_data='m'), InlineKeyboardButton("🌙 ئێڤاری", callback_data='e')]]))))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()

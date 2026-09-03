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

# --- ١. فۆنکشنێن وەرگرتنا زانیاریێن زیندی (Live Data) ---

def get_precise_prayer():
    try:
        # بەکارئینانا میتۆدێ ١٣ (Diyanet) کو بۆ دهۆکێ باشترینە
        url = "http://api.aladhan.com/v1/timingsByCity?city=Duhok&country=Iraq&method=13"
        res = requests.get(url).json()
        t = res['data']['timings']
        
        # رێکخستنا دەمی: ئەگەر دەم خەلەت بوو، ل ڤێرە خولەکان کێم یان زێدە بکە
        def format_t(t_str, offset=0):
            dt = datetime.strptime(t_str, "%H:%M") + timedelta(minutes=offset)
            return dt.strftime("%I:%M %p")

        return {
            "سپێدە": format_t(t['Fajr'], 0),
            "ڕۆژهەلاتن": format_t(t['Sunrise'], 0),
            "نیڤڕۆ": format_t(t['Dhuhr'], 0),
            "ئێڤاری": format_t(t['Asr'], 0),
            "مەغرب": format_t(t['Maghrib'], 2), # زێدەکرنا ٢ خولەکان بۆ مەغربێ دهۆکێ
            "عیشا": format_t(t['Isha'], 2)
        }
    except:
        return None

def get_precise_weather():
    if not WEATHER_API_KEY: return "توکن نینە"
    try:
        # وەرگرتنا کەشوهەوای ب رێکا توکنا تە ژ OpenWeatherMap
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Duhok&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        temp = data['main']['temp']
        desc = data['weather'][0]['main']
        return f"{int(temp)}°C - {desc}"
    except:
        return "کێشەک هەبوو"

def get_precise_currency():
    if not CURRENCY_API_KEY: return None
    try:
        # وەرگرتنا بهایێ دراڤی ب رێکا توکنا تە ژ ExchangeRate-API
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
        res = requests.get(url).json()
        rates = res['conversion_rates']
        
        # بهایێ تەخمینی یێ دۆلاری ل بازارێ دهۆکێ
        usd_iqd = 150750 
        return {
            "TRY": rates['TRY'],
            "IRR": rates['IRR'],
            "IQD": usd_iqd
        }
    except:
        return None

# --- ٢. رێکخستنا مینیو و فەرمانان ---

async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی (زیندی)"),
        BotCommand("prayer", "دەمێن بانگی (ورد)"),
        BotCommand("weather", "کەشوهەوا (ورد)"),
        BotCommand("education", "قوتابی و مەلازێم"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان")
    ]
    await application.bot.set_my_commands(commands)

# --- ٣. فۆنکشنێن بەرسڤدانێ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلاڤ {update.effective_user.first_name} 👋\nبخێر هاتی بۆ ئالیکارێ بادینان. نوکە بوتێ تە یێ گرێدایی API یێن فەرمی یە.")

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("⏳ دهێتە نووکرن...")
    data = get_precise_currency()
    if data:
        msg = (
            "💰 **بهایێ دراڤی ل بازارێ دهۆکێ:**\n\n"
            f"💵 100 دۆلار ⮕ ~{data['IQD']:,} دینار\n"
            f"🇹🇷 100 دۆلار ⮕ {int(data['TRY'] * 100)} لێرە\n"
            f"🇮🇷 100 دۆلار ⮕ {int(data['IRR'] * 100 / 1000000)} ملیۆن تمەن"
        )
    else: msg = "کێشەک د توکنی دا هەبوو."
    await wait.edit_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("🌤 ل هیڤیێ بە...")
    w = get_precise_weather()
    await wait.edit_text(f"🌤 **کەشوهەوا ل دهۆکێ (نوکە):**\n`{w}`", parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("🕌 ل هیڤیێ بە...")
    p = get_precise_prayer()
    if p:
        msg = (
            f"🕌 **دەمێن بانگی ل دهۆکێ ({datetime.now().strftime('%d/%m')}):**\n\n"
            f"🌅 سپێدە: `{p['سپێدە']}`\n"
            f"☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n"
            f"🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
            f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n"
            f"🌇 مەغرب: `{p['مەغرب']}`\n"
            f"🌃 عیشا: `{p['عیشا']}`"
        )
    else: msg = "کێشەک د سێرڤەری دا هەبوو."
    await wait.edit_text(msg, parse_mode='Markdown')

async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("☀️ سپێدێ", callback_data='morning'), InlineKeyboardButton("🌙 ئێڤاری", callback_data='evening')]]
    await update.message.reply_text("📖 زیکرەکێ هەلبژێره:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text.startswith('/'): return
    try:
        ar = GoogleTranslator(source='ku', target='ar').translate(user_text)
        en = GoogleTranslator(source='ku', target='en').translate(user_text)
        await update.message.reply_text(f"✅ **وەرگێڕان:**\n\n🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
    except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'morning': await query.message.reply_text("☀️ زیکرێ سپێدێ: (أصبحنا وأصبح الملك لله)")
    if query.data == 'evening': await query.message.reply_text("🌙 زیکرێ ئێڤاری: (أمسینا وأمسی الملك لله)")

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("adhkar", adhkar))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

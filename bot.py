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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. دەمێن بانگی (ب رێکخستنا ورد بۆ دهۆکێ) ---
def get_precise_prayer():
    try:
        # بەکارئینانا میتۆدێ ١٣ و وەرگرتنا داتایان
        url = "http://api.aladhan.com/v1/timingsByCity?city=Duhok&country=Iraq&method=13"
        res = requests.get(url).json()
        t = res['data']['timings']
        
        def format_t(t_str, offset_minutes=0):
            dt = datetime.strptime(t_str, "%H:%M") + timedelta(minutes=offset_minutes)
            return dt.strftime("%I:%M %p")

        # رێکخستنا خولەکان دا کو درست دگەل وێنەیێ تە بگونجێت
        return {
            "سپێدە": format_t(t['Fajr'], 3),      # 04:13
            "ڕۆژهەلاتن": format_t(t['Sunrise'], 0), # 05:45
            "نیڤڕۆ": format_t(t['Dhuhr'], 9),     # 12:16
            "ئێڤاری": format_t(t['Asr'], 5),       # 03:51
            "مەغرب": format_t(t['Maghrib'], 5),    # 06:39
            "عیشا": format_t(t['Isha'], 5)         # 08:03
        }
    except Exception as e:
        logging.error(f"Prayer Error: {e}")
        return None

# --- ٢. کەشوهەوایێ ورد (ب لۆگکرنا کێشەیان) ---
def get_precise_weather():
    if not WEATHER_API_KEY: return "توکن نینە"
    try:
        # گۆڕینا http بۆ https و زێدەکرنا دهۆک، عیراق
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Duhok,IQ&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"{int(temp)}°C - {desc}"
        else:
            logging.error(f"Weather API Error: {data.get('message')}")
            return "هێشتا توکن ئەکتیڤ نەبوویە"
    except Exception as e:
        logging.error(f"Weather Exception: {e}")
        return "کێشەیەکا تەکنیکی هەبوو"

# --- ٣. دراڤێ بازارێ دهۆکێ ---
def get_precise_currency():
    if not CURRENCY_API_KEY: return None
    try:
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
        res = requests.get(url).json()
        rates = res['conversion_rates']
        
        # بهایێ دۆلاری ل بازارێ دهۆکێ (تەخمینی)
        usd_iqd = 150750 
        return {
            "TRY": rates['TRY'],
            "IRR": rates['IRR'],
            "IQD": usd_iqd
        }
    except:
        return None

# --- فرمانێن بوتی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلاڤ {update.effective_user.first_name} 👋\nبخێر هاتی بۆ ئالیکارێ بادینان. نوکە زانیاریێن ورد بۆ تە دهێن.")

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_precise_currency()
    if data:
        msg = (
            "💰 **بهایێ دراڤی ل بازارێ دهۆکێ:**\n\n"
            f"💵 100 دۆلار ⮕ ~{data['IQD']:,} دینار\n"
            f"🇹🇷 100 دۆلار ⮕ {int(data['TRY'] * 100)} لێرە\n"
            f"🇮🇷 100 دۆلار ⮕ {int(data['IRR'] * 100 / 1000000)} ملیۆن تمەن"
        )
    else: msg = "کێشەک د توکنا دراڤی دا هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = get_precise_weather()
    await update.message.reply_text(f"🌤 **کەشوهەوا ل دهۆکێ (نوکە):**\n`{w}`", parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = get_precise_prayer()
    if p:
        msg = (
            f"🕌 **دەمێن بانگی ل دهۆکێ (واقعی):**\n"
            f"📅 رێکەفت: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"🌅 سپێدە: `{p['سپێدە']}`\n"
            f"☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n"
            f"🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
            f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n"
            f"🌇 مەغرب: `{p['مەغرب']}`\n"
            f"🌃 عیشا: `{p['عیشا']}`"
        )
    else: msg = "کێشەک د وەرگرتنا دەمان دا هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان")
    ])

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)) # وەرگێڕان ل ڤێرە زێدە بکە
    app.run_polling()

if __name__ == '__main__':
    main()

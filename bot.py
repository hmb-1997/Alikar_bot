import os
import logging
import requests
import yt_dlp
import shutil
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا توکنان
TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- پشکا پاقژکرنا ئۆتۆماتیک (Auto-Cleanup) ---

def clear_downloads():
    folder = 'downloads'
    if os.path.exists(folder):
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            logging.info("فۆڵده‌ر هاتە پاقژکرن.")
        except Exception as e:
            logging.error(f"Error cleaning: {e}")

async def cleanup_job(context: ContextTypes.DEFAULT_TYPE):
    clear_downloads()

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
        return "توکن ل هیڤیا ئەکتیڤبوونێ یە"
    except: return "کێشەیەک هەبوو"

def get_precise_currency():
    if not CURRENCY_API_KEY: return None
    try:
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
        res = requests.get(url).json()
        rates = res['conversion_rates']
        return {"TRY": rates['TRY'], "IRR": rates['IRR'], "IQD": 150750}
    except: return None

# --- ٢. مێشکێ داونلۆدکەری ---

def download_media(url, mode='video'):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'format': 'best[ext=mp4]/best' if mode == 'video' else 'bestaudio/best',
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == 'audio':
            filename = os.path.splitext(filename)[0] + '.mp3'
        return filename

# --- ٣. فرمانێن سەرەکی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلاڤ {update.effective_user.first_name} 👋\nبخێر هاتی! بوت کارا یە و هەر ١٠ خۆله‌کان داتایان ڕەش دکەت.")

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = get_precise_prayer()
    if p:
        msg = (f"🕌 **دەمێن بانگی ل دهۆکێ:**\n📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
               f"🌅 سپێدە: `{p['سپێدە']}`\n☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
               f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n🌇 مەغرب: `{p['مەغرب']}`\n🌃 عیشا: `{p['عیشا']}`")
        await update.message.reply_text(msg, parse_mode='Markdown')

async def currency_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_precise_currency()
    if data:
        msg = (f"💰 **بهایێ دراڤی ل دهۆکێ:**\n\n💵 100 دۆلار ⮕ ~{data['IQD']:,} دینار\n"
               f"🇹🇷 100 دۆلار ⮕ {int(data['TRY'] * 100)} لێرە\n🇮🇷 100 دۆلار ⮕ {int(data['IRR'] * 100 / 1000000)} ملیۆن تمەن")
        await update.message.reply_text(msg, parse_mode='Markdown')

# --- ٤. مێشکێ بوتێ (Handling Text & Links) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'): return
    if "http" in text:
        context.user_data['url'] = text
        kb = [[InlineKeyboardButton("🎬 Video", callback_data='v'), InlineKeyboardButton("🎵 MP3", callback_data='a')]]
        await update.message.reply_text("🎥 تە چ داونلۆد دڤێت؟", reply_markup=InlineKeyboardMarkup(kb))
    else:
        try:
            ar = GoogleTranslator(source='ku', target='ar').translate(text)
            en = GoogleTranslator(source='ku', target='en').translate(text)
            await update.message.reply_text(f"✅ **وەرگێڕان:**\n\n🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
        except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = context.user_data.get('url')
    if query.data in ['v', 'a']:
        m = await query.message.reply_text("⏳ دهێتە داونلۆدکرن...")
        try:
            mode = 'video' if query.data == 'v' else 'audio'
            path = download_media(url, mode)
            with open(path, 'rb') as f:
                if mode == 'video': await query.message.reply_video(f)
                else: await query.message.reply_audio(f)
            if os.path.exists(path): os.remove(path)
            await m.delete()
        except: await m.edit_text("ببورە، داونلۆد نەبوو.")
    elif query.data == 'morning': await query.message.reply_text("☀️ زیکرێ سپێدێ: (أصبحنا وأصبح الملك لله)")
    elif query.data == 'evening': await query.message.reply_text("🌙 زیکرێ ئێڤاری: (أمسینا وأمسی الملك لله)")

# --- ٥. رێکخستنا مینیو و پاقژکرنا ئۆتۆماتیک ---

async def post_init(application: Application):
    clear_downloads()
    if application.job_queue:
        application.job_queue.run_repeating(cleanup_job, interval=600, first=10)
    
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرن"),
        BotCommand("currency", "بهایێ دراڤی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا"),
        BotCommand("adhkar", "زیکر و ئایین")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency_cmd))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", lambda u, c: u.message.reply_text(f"🌤 {get_precise_weather()}")))
    app.add_handler(CommandHandler("adhkar", lambda u, c: u.message.reply_text("📖 زیکرەکێ هەلبژێره:", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("☀️ سپێدێ", callback_data='morning'), InlineKeyboardButton("🌙 ئێڤاری", callback_data='evening')]]))))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()

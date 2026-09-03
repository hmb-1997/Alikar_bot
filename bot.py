import os
import logging
import requests
import yt_dlp
import html
import shutil  # بۆ ڕەشکرنا فۆڵده‌ران ب ئاسانی
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
    """ڕەشکرنا هەمی فایلێن ناڤ فۆڵده‌رێ downloads دا کو سێرڤەر تژی نەبیت"""
    folder = 'downloads'
    if os.path.exists(folder):
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            logging.info("فۆڵده‌رێ داونلۆدێ ب سەرکەفتی هاتە پاقژکرن.")
        except Exception as e:
            logging.error(f"Error cleaning folder: {e}")

async def cleanup_job(context: ContextTypes.DEFAULT_TYPE):
    """ئەڤ فۆنکشنی هه‌ر ١٠ خۆله‌کان جارەکێ کار دکەت"""
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

# --- ٢. مێشکێ داونلۆدکەری ---

def download_media(url, mode='video'):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    if mode == 'video':
        ydl_opts['format'] = 'best[ext=mp4]/best'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == 'audio':
            filename = os.path.splitext(filename)[0] + '.mp3'
        return filename

# --- ٣. فرمانێن سەرەکی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلاڤ {update.effective_user.first_name} 👋\nبخێر هاتی! بوت نوکە یێ ب هێزە و هەر ١٠ خۆله‌کان داتایان سه‌فه‌ر دکەت.")

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = get_precise_prayer()
    if p:
        msg = (f"🕌 **دەمێن بانگی ل دهۆکێ:**\n📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
               f"🌅 سپێدە: `{p['سپێدە']}`\n☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
               f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n🌇 مەغرب: `{p['مەغرب']}`\n🌃 عیشا: `{p['عیشا']}`")
    else: msg = "کێشەک هەبوو."
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- ٤. مێشکێ بوتێ (Handling Text & Links) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'): return
    
    if "http" in text:
        context.user_data['last_url'] = text
        keyboard = [[InlineKeyboardButton("🎬 ڤیدیۆ (Video)", callback_data='dl_vid')],
                    [InlineKeyboardButton("🎵 دەنگ (MP3)", callback_data='dl_aud')]]
        await update.message.reply_text("🎥 لینک هاتە دیتن! تە چ جۆرە داونلۆد دڤێت؟", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        try:
            ar = GoogleTranslator(source='ku', target='ar').translate(text)
            en = GoogleTranslator(source='ku', target='en').translate(text)
            await update.message.reply_text(f"✅ **وەرگێڕان:**\n\n🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
        except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data in ['dl_vid', 'dl_aud']:
        url = context.user_data.get('last_url')
        status_msg = await query.message.reply_text("⏳ دهێتە داونلۆدکرن...")
        try:
            mode = 'video' if query.data == 'dl_vid' else 'audio'
            file_path = download_media(url, mode)
            with open(file_path, 'rb') as f:
                if mode == 'video': await query.message.reply_video(video=f)
                else: await query.message.reply_audio(audio=f)
            os.remove(file_path)
            await status_msg.delete()
        except: await status_msg.edit_text("ببورە، داونلۆد نەبوو.")

# --- ٥. رێکخستنا مینیو و پاقژکرنا ئۆتۆماتیک ---

async def post_init(application: Application):
    # ده‌سپێكێ فۆڵده‌ری پاقژ بكه‌
    clear_downloads()
    
    # رێکخستنا کارێ (Job) هه‌ر ١٠ خۆله‌کان جارەکێ
    application.job_queue.run_repeating(cleanup_job, interval=600, first=10)
    
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا"),
        BotCommand("adhkar", "زیکر و ئایین")
    ])

def main():

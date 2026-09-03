import os
import logging
import requests
import yt_dlp
import html
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
            return f"{int(data['main']['temp'])}°C - {data['weather'][0]['description']}"
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

# --- ٢. مێشکێ داونلۆدکەری (Social Media Downloader) ---

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
    await update.message.reply_text(f"سلاڤ {update.effective_user.first_name} 👋\nبخێر هاتی بۆ ئالیکارێ بادینان.\n\n✅ بۆ وەرگێڕانێ: تێکست بفرێکه.\n✅ بۆ داونلۆدێ: لینکێ ڤیدیۆیێ بفرێکه یان فەرمانا /download بەکاربینە.")

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

async def download_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 **داونلۆدکەر:**\nتکایە لینکێ ڤیدیۆیێ (YouTube, TikTok, Instagram) بفرێکه دا بۆ تە داونلۆد بکەم.")

# --- ٤. مێشکێ بوتێ (Handling Text & Links) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'): return
    
    if "http" in text:
        context.user_data['last_url'] = text
        keyboard = [
            [InlineKeyboardButton("🎬 ڤیدیۆ (Video)", callback_data='dl_vid')],
            [InlineKeyboardButton("🎵 دەنگ (MP3)", callback_data='dl_aud')]
        ]
        await update.message.reply_text("🎥 لینک هاتە دیتن! تە چ جۆرە داونلۆد دڤێت؟", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        waiting = await update.message.reply_text("⏳ دهێتە وەرگێڕان...")
        try:
            ar = GoogleTranslator(source='ku', target='ar').translate(text)
            en = GoogleTranslator(source='ku', target='en').translate(text)
            await waiting.edit_text(f"✅ **ئەنجام:**\n\n🇸🇦 عەرەبی: `{ar}`\n🇺🇸 ئینگلیزی: `{en}`", parse_mode='Markdown')
        except:
            await waiting.edit_text("ببوره، کێشەیەک هەبوو.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'm': await query.message.reply_text("☀️ زیکرێ سپێدێ: (أصبحنا وأصبح الملك لله)")
    elif query.data == 'e': await query.message.reply_text("🌙 زیکرێ ئێڤاری: (أمسینا وأمسی الملك لله)")
    
    elif query.data in ['dl_vid', 'dl_aud']:
        url = context.user_data.get('last_url')
        if not url:
            await query.message.reply_text("ببورە، لینک نەهاتە دیتن. دووبارە لینکێ بفرێکه.")
            return

        status_msg = await query.message.reply_text("⏳ دهێتە داونلۆدکرن... کێمەکێ ل هیڤیێ بە.")
        mode = 'video' if query.data == 'dl_vid' else 'audio'
        
        try:
            file_path = download_media(url, mode)
            with open(file_path, 'rb') as f:
                if mode == 'video':
                    await query.message.reply_video(video=f, caption="✅ ڤیدیۆیا تە ئامادەیە.")
                else:
                    await query.message.reply_audio(audio=f, caption="✅ فایلێ دەنگی ئامادەیە.")
            os.remove(file_path)
            await status_msg.delete()
        except Exception as e:
            logging.error(f"DL Error: {e}")
            await status_msg.edit_text("ببورە، داونلۆد نەبوو. رەنگە قەبارە یێ مەزن بیت (پتر ژ 50MB) یان لینک یێ پاراستی بیت.")

# --- ٥. رێکخستنا مینیو و سەرەکی ---

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان"),
        BotCommand("download", "داونلۆدکرنا ڤیدیۆیان")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", lambda u, c: u.message.reply_text(f"🌤 کەشوهەوا: {get_precise_weather()}")))
    app.add_handler(CommandHandler("download", download_cmd))
    app.add_handler(CommandHandler("adhkar", lambda u, c: u.message.reply_text("📖 زیکرەکێ هەلبژێره:", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("☀️ سپێدێ", callback_data='m'), InlineKeyboardButton("🌙 ئێڤاری", callback_data='e')]]))))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()

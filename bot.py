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

# --- پشکا پاقژکرنا سێرڤەری ---
def clear_downloads():
    folder = 'downloads'
    if os.path.exists(folder):
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path): os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e: logging.error(f"Cleanup error: {e}")

async def cleanup_job(context: ContextTypes.DEFAULT_TYPE):
    clear_downloads()

# --- ١. زانیاریێن زیندی ---
def get_precise_prayer():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Duhok&country=Iraq&method=13"
        res = requests.get(url).json()
        t = res['data']['timings']
        def format_t(t_str, offset=0):
            dt = datetime.strptime(t_str, "%H:%M") + timedelta(minutes=offset)
            return dt.strftime("%I:%M %p")
        return {"سپێدە": format_t(t['Fajr'], 3), "ڕۆژهەلاتن": format_t(t['Sunrise'], 0), "نیڤڕۆ": format_t(t['Dhuhr'], 9),
                "ئێڤاری": format_t(t['Asr'], 5), "مەغرب": format_t(t['Maghrib'], 5), "عیشا": format_t(t['Isha'], 5)}
    except: return None

# --- ٢. داونلۆدکەرا ڤیدیۆیان (Improved) ---
def download_media(url, mode='video'):
    if not os.path.exists('downloads'): os.makedirs('downloads')
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'format': 'best[ext=mp4]/best' if mode == 'video' else 'bestaudio/best',
        # ئەڤ هێڵە بۆ کێمکرنا بلۆکا یوتوبێیە
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return os.path.splitext(filename)[0] + '.mp3' if mode == 'audio' else filename

# --- ٣. فرمانێن بەرسڤدانێ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سڵاڤ {update.effective_user.first_name} 👋\nبوت یێ ئامادەیە! هەر تشتەکێ تە ڤیا هەلبژێره.")

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = get_precise_prayer()
    if p:
        msg = (f"🕌 **دەمێن بانگی ل دهۆکێ:**\n📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
               f"🌅 سپێدە: `{p['سپێدە']}`\n☀️ ڕۆژهەلاتن: `{p['ڕۆژهەلاتن']}`\n🕛 نیڤڕۆ: `{p['نیڤڕۆ']}`\n"
               f"🕒 ئێڤاری: `{p['ئێڤاری']}`\n🌇 مەغرب: `{p['مەغرب']}`\n🌃 عیشا: `{p['عیشا']}`")
        await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith('/'): return
    if "http" in text:
        context.user_data['url'] = text
        kb = [[InlineKeyboardButton("🎬 Video", callback_data='v'), InlineKeyboardButton("🎵 MP3", callback_data='a')]]
        await update.message.reply_text("🎥 چ جۆرە داونلۆد؟", reply_markup=InlineKeyboardMarkup(kb))
    else:
        try:
            ar = GoogleTranslator(source='ku', target='ar').translate(text)
            en = GoogleTranslator(source='ku', target='en').translate(text)
            await update.message.reply_text(f"🇸🇦: `{ar}`\n🇺🇸: `{en}`", parse_mode='Markdown')
        except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = context.user_data.get('url')
    if query.data in ['v', 'a']:
        m = await query.message.reply_text("⏳ دهێتە داونلۆدکرن... (ئەگەر ڤیدیۆ یوتوب بیت رەنگە کێمەکێ درێژ بکێشیت)")
        try:
            mode = 'video' if query.data == 'v' else 'audio'
            path = download_media(url, mode)
            with open(path, 'rb') as f:
                if mode == 'video': await query.message.reply_video(f)
                else: await query.message.reply_audio(f)
            if os.path.exists(path): os.remove(path)
            await m.delete()
        except Exception as e:
            await m.edit_text("ببورە، داونلۆد نەبوو. (رەنگە لینک یێ پاراستی بیت یان سێرڤەرێ یوتوبێ یێ قەلەبالغ بیت).")

async def post_init(application: Application):
    clear_downloads()
    if application.job_queue:
        application.job_queue.run_repeating(cleanup_job, interval=600, first=10)
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرن"), BotCommand("prayer", "بانگ"),
        BotCommand("currency", "دراڤ"), BotCommand("weather", "کەشوهەوا")
    ])

# --- پشکا سەرەکی (Main) ---
def main():
    if not TOKEN: return
    # دروستکرنا ئەپڵیکەیشنێ
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # زێدەکرنا فرمانان (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("currency", lambda u, c: u.message.reply_text("💰 بهایێ دراڤی دهێتە نووکرن...")))
    app.add_handler(CommandHandler("weather", lambda u, c: u.message.reply_text("🌤 کەشوهەوا دهێتە نووکرن...")))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # دەستپێکرنا بوتی
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from deep_translator import GoogleTranslator

# وەرگرتنا تۆکنی ژ ڕێلوەی
TOKEN = os.getenv('BOT_TOKEN')

# رێکخستنا لۆگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ١. رێکخستنا لیستا فرمانان (Menu) ---
async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("currency", "بهایێ دراڤی"),
        BotCommand("prayer", "دەمێن بانگی"),
        BotCommand("weather", "کەشوهەوا"),
        BotCommand("education", "پەروەردە و قوتابی"),
        BotCommand("adhkar", "زیکر و ئایین"),
        BotCommand("translate", "وەرگێڕان")
    ]
    await application.bot.set_my_commands(commands)

# --- ٢. فۆنکشنێن سەرەکی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"سلاڤ {user_name} 👋\n"
        "بخێر هاتی بۆ بوتێ **ئالیکارێ بادینان**.\n\n"
        "ئەز دشێم د گەلەک بواران دا هاریکاریا تە بکەم. ژ کەرەما خۆ فرمانەکێ هەلبژێره."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "💰 **بهایێ دراڤی ل بازارێ دهۆکێ:**\n\n💵 100 دۆلار ⮕ 150,500\n🇮🇷 1 ملیۆن تمەن ⮕ 2,450\n🇹🇷 100 لێرە ⮕ 4,400"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🕌 **دەمێن بانگی (دهۆک):**\n\n🌅 سپێدە: 04:35\n☀️ نیڤڕۆ: 12:12\n🌆 ئێڤاری: 03:48\n🌙 مەغرب: 06:35\n🌌 عیشا: 07:55"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🌤 **کەشوهەوا ل بادینان:**\n\n📍 دهۆک: 32°C\n📍 زاخۆ: 34°C\n📍 ئامێدی: 28°C"
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- پشکا زیکران ب دوگمە (Adhkar with Buttons) ---
async def adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("☀️ زیکرێن سپێدێ", callback_data='morning_adhkar')],
        [InlineKeyboardButton("🌙 زیکرێن ئێڤاری", callback_data='evening_adhkar')],
        [InlineKeyboardButton("📜 چیرۆکا ئایینی", callback_data='religious_story')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📖 **پشکا زیکر و ئایین:**\nژ کەرەما خۆ ئێکێ هەلبژێره:", reply_markup=reply_markup)

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔗 ئەنجامێن پۆلا ١٢", url="https://www.azmoonakan.org")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎓 **پشکا قوتابیان:**", reply_markup=reply_markup)

# --- ٣. وەرگێڕان (Handling Translation) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    waiting_msg = await update.message.reply_text("⏳ دهێتە وەرگێڕان...")
    try:
        translated_ar = GoogleTranslator(source='ku', target='ar').translate(user_text)
        translated_en = GoogleTranslator(source='ku', target='en').translate(user_text)
        result = f"✅ **ئەنجام:**\n\n🇸🇦 **Ar:** `{translated_ar}`\n🇺🇸 **En:** `{translated_en}`"
        await waiting_msg.edit_text(result, parse_mode='Markdown')
    except:
        await waiting_msg.edit_text("ببورە، کێشەیەک د وەرگێڕانێ دا هەیه.")

# --- ٤. مێشکێ بوتێ (Handling Button Clicks) ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'morning_adhkar':
        text = "☀️ **زیکرێن سپێدێ:**\n\n- أصْبَحْنَا وَأَصْبَحَ المُلْكُ لِلَّهِ.\n- اللَّهُمَّ بِكَ أَصْبَحْنَا، وَبِكَ أَمْسَيْنَا.\n- آية الكرسي.\n- (3 جاران) قُلْ هُوَ اللَّهُ أَحَدٌ، والمعوذتين."
        await query.message.reply_text(text)
    
    elif query.data == 'evening_adhkar':
        text = "🌙 **زیکرێن ئێڤاری:**\n\n- أَمْسَيْنَا وَأَمْسَى المُلْكُ لِلَّهِ.\n- اللَّهُمَّ بِكَ أَمْسَيْنَا، وَبِكَ أَصْبَحْنَا.\n- آية الكرسي.\n- (3 جاران) قُلْ هُوَ اللَّهُ أَحَدٌ، والمعوذتين."
        await query.message.reply_text(text)
    
    elif query.data == 'religious_story':
        text = "📜 **چیرۆکەکا کورت:**\nپێغەمبەر (سلاڤ لێ بن) دبێژیت: (خَيْرُ النَّاسِ أَنْفَعُهُمْ لِلنَّاسِ) - باشترین مرۆڤ ئەوێ پتر مفای بگەهینتە خەلکی."
        await query.message.reply_text(text)

# --- ٥. کارپێکرنا سەرەکی ---
def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("prayer", prayer))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("education", education))
    app.add_handler(CommandHandler("adhkar", adhkar))
    
    # بۆ وەرگرتنا کلیکێن سەر دوگمەیان
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # بۆ وەرگێڕانا دەقان
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == '__main__':
    main()

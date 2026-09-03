import os
import logging
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا تۆکنی ژ Railway
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- پشکا مێشکێ زخره‌فێ (٤٠ ستایلێن Pro) ---

def decorate_pro(name):
    styles = []
    
    # ١-٥: فۆنتێن ئینگلیزی (بێ کێشە و تاقیکری)
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    f1 = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋Ｍ𝐍𝐎𝐏𝐐𝐑𝐒𝐓Ｕ𝐕𝐖𝐗Ｙ𝐙"
    f2 = "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"
    f3 = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟𝐸𝐹𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    f4 = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔙𝔚𝔛𝔜ℨ"
    f5 = "𝕒𝒷𝕔𝒹𝕖𝒻𝕘𝒽𝕚𝒿𝓀𝓁𝓂𝕟𝕠𝕡𝕢𝓇𝕤𝕥𝓊𝓋𝕨𝓍𝓎𝓏𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"

    trans1 = str.maketrans(lower + upper, f1)
    trans2 = str.maketrans(lower + upper, f2)
    trans3 = str.maketrans(lower + upper, f3)
    trans4 = str.maketrans(lower + upper, f4)
    trans5 = str.maketrans(lower + upper, f5)

    styles.append(name.translate(trans1))
    styles.append(name.translate(trans2))
    styles.append(name.translate(trans3))
    styles.append(name.translate(trans4))
    styles.append(name.translate(trans5))

    # ٦-٤٠: شێوازێن ب هێما (Symbols & Frames)
    patterns = [
        "꧁ {} ꧂", "『 {} 』", "★ {} ★", "☆ {} ☆", "⚡ {} ⚡", "ツ {} ツ", "〆 {} 〆",
        "亗 {} 亗", "『VİP』{}", "♛ {} ♛", "🔥 {} 🔥", "✨ {} ✨", "💎 {} 💎", "🌹 {} 🌹",
        "👑 {} 👑", "⚔️ {} ⚔️", "💠 {} 💠", "╰ {} ╯", "『GM』{}", "☯ {} ☯", "☾ {} ☽",
        "⚓ {} ⚓", "░ {} ░", "▓ {} ▓", "🚫 {} 🚫", "『PRO』{}", "💀 {} 💀", "👻 {} 👻",
        "👽 {} 👽", "『K』{}", "༺ {} ༻", "↜ {} ↝", "⌁ {} ⌉", "︻ {} ︼", "『A』{}",
        "⫷ {} ⫸", "⫹ {} ⫺", "◤ {} ◥", "☬ {} ☬", "◈ {} ◈"
    ]
    
    for p in patterns:
        styles.append(p.format(name))
        
    return styles[:45] # ٤٠-٤٥ ستایل

# --- فرمانێن سەرەکی (Commands) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 **سڵاڤ {user}! ب خێر هاتی.**\n\n"
        "⌨️ تەنێ ناڤێ خۆ (عەرەبی یان ئینگلیزی) بفرێكه.\n"
        "ئەز دێ ب **٤٠ شێوازێن پڕۆ** بۆ تە زخره‌ف کەم.\n\n"
        "✨ کلیک ل سەر ناڤی بکە دێ کۆپی بیت.",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 **رێنمایى:**\n"
        "١. ناڤێ خۆ بنڤێسه.\n"
        "٢. ستایلەکێ هەلبژێره.\n"
        "٣. کلیک بکە و 'Paste' بکە ل سەر پرۆفایلێ خۆ.",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if len(name) > 25:
        await update.message.reply_text("❌ ناڤ زۆر درێژە!")
        return

    wait_msg = await update.message.reply_text("💎 **دهێتە زخره‌فکرن...**")
    
    styles = decorate_pro(name)
    
    response = f"✅ **زخره‌فا ناڤێ:** `{name}`\n\n"
    for i, s_text in enumerate(styles, 1):
        response += f"{i}. `{s_text}`\n"
    
    try:
        await wait_msg.edit_text(response, parse_mode='Markdown')
    except:
        # ئەگەر ژمارەیا پیتان زۆر بوو، دێ کەینە دوو بەش
        await wait_msg.edit_text(response[:4000], parse_mode='Markdown')
        await update.message.reply_text(response[4000:], parse_mode='Markdown')

# --- دروستکرنا مینیو (Professional Menu) ---
async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("help", "رێنمایى و هاریكاری")
    ]
    await application.bot.set_my_commands(commands)

def main():
    if not TOKEN: return
    
    # Application Builder دگەل مینیو
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Decoration Pro Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

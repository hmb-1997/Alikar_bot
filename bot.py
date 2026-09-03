import os
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا تۆکنی ژ Railway
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- پشکا مێشکێ زخره‌فێ ---
def decorate_name(name):
    bold = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
    italic = "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    s = [
        name.translate(str.maketrans(normal, bold)),
        name.translate(str.maketrans(normal, italic)),
        f"꧁ {name} ꧂",
        f"『 {name} 』",
        f"★ {name} ★",
        f"♛ {name} ♛",
        f"🔥 {name} 🔥",
        f"✨ {name} ✨",
        f"👑 {name} 👑"
    ]
    return s[:15] # بۆ نموونه ١٥ ستایل

# --- فرمانێن بوتی (Commands) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **سڵاڤ! ب خێر هاتی بۆ بوتێ زخره‌فا بادینان.**\n\n"
        "⌨️ تەنێ ناڤێ خۆ بفرێكه دا بۆ تە زخره‌ف کەم.\n"
        "📜 یان فەرمانا /decorate و پاشان ناڤی بنڤێسه.",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ **چەوا بوتێ زخره‌فێ بەکاردێ؟**\n\n"
        "١. ناڤەکێ بنڤێسه و بفرێکه.\n"
        "٢. بوت دێ لیستەکا ستایلان دەتە تە.\n"
        "٣. کلیک ل سەر هەر ئێکێ بکە دێ کۆپی بیت.",
        parse_mode='Markdown'
    )

async def decorate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)
    if not name:
        await update.message.reply_text("❌ تکایە ناڤەکێ ل تەنیشت فرمانێ بنڤێسه.\nنموونه: `/decorate Honar`", parse_mode='Markdown')
        return
    await process_decoration(update, name)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_decoration(update, update.message.text)

async def process_decoration(update: Update, name: str):
    if len(name) > 25:
        await update.message.reply_text("❌ ناڤ زۆر درێژە!")
        return
    
    styles = decorate_name(name)
    response = f"💎 **زخره‌فا ناڤێ:** `{name}`\n\n"
    for s_text in styles:
        response += f"`{s_text}`\n"
    await update.message.reply_text(response, parse_mode='Markdown')

# --- ئەڤ پشکە لیستێ (Menu) درست دکەت ---
async def post_init(application: Application):
    commands = [
        BotCommand("start", "دەسپێکرنا بوتی"),
        BotCommand("decorate", "زخره‌فکرنا ناڤەکێ"),
        BotCommand("help", "رێنمایى و هاریكاری")
    ]
    await application.bot.set_my_commands(commands)

def main():
    if not TOKEN: return
    # زێدەکرنا post_init دا لیستە کار بکەت
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("decorate", decorate_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot with professional menu is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

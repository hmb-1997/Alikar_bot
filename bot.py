import os
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا تۆکنی
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- مێشکێ زخره‌فا VIP و PRO (تایبەت بۆ ئینگلیزی و عەرەبی) ---

def get_pro_decorations(name):
    # فۆنتێن پێشکەفتی یێن ئینگلیزی
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    normal = lower + upper
    
    # ١. فۆنتێ Bold Pro
    f1 = "𝐚𝐛𝐜𝐝 e f g h i j k l m n o p q r s t u v w x y z 𝐀 𝐁 𝐂 𝐃 𝐄 𝐅 𝐆 𝐇 𝐈 𝐉 𝐊 𝐋 𝐌 𝐍 𝐎 𝐏 𝐙 𝐑 𝐒 𝐓 𝐔 𝐕 𝐖 𝐗 𝐘 𝐙".replace(" ","")
    # ٢. فۆنتێ Italic Pro
    f2 = "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"
    # ٣. فۆنتێ Bubble (بازنەیی)
    f3 = "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
    # ٤. فۆنتێ Squares (چوارگۆشە)
    f4 = "🄰🄱🄲🄳🄴🄵🄿🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🄰🄱🄲🄳🄴🄵🄿🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
    # ٥. فۆنتێ Old English
    f5 = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"

    # وەرگێڕان بۆ فۆنتان (تەنێ ئەگەر ئینگلیزی بیت)
    n1 = name.translate(str.maketrans(normal, f1))
    n2 = name.translate(str.maketrans(normal, f2))
    n3 = name.translate(str.maketrans(normal, f3))
    n4 = name.translate(str.maketrans(normal, f4))
    n5 = name.translate(str.maketrans(normal, f5))

    # لیستا ٥٠ زخره‌فێن شاهانە
    styles = [
        f"꧁༒☬ {n1} ☬༒꧂",
        f"『VİP』{n1}〆",
        f"亗 {n1} 亗",
        f"〆{n2}〆",
        f"🔥 {n1} 🔥",
        f"♛ {n5} ♛",
        f"༺ {n1} ༻",
        f"⚔️ {n2} ⚔️",
        f"💎 {n4} 💎",
        f"🔱 {n1} 🔱",
        f"⫷ {n2} ⫸",
        f"◤ {n1} ◥",
        f"☬ {n3} ☬",
        f"〖 {n1} 〗",
        f"【 {n2} 】",
        f"〔 {n4} 〕",
        f"⚡ {n1} ⚡",
        f"👑 {n2} 👑",
        f"⚓ {n3} ⚓",
        f"『PRO』{n1}",
        f"☣️ {n1} ☣️",
        f"░ {n1} ░",
        f"▓ {n2} ▓",
        f"☾ {n1} ☽",
        f"☯️ {n5} ☯️",
        f"⛓️ {n1} ⛓️",
        f"💀 {n1} 💀",
        f"👻 {n2} 👻",
        f"👽 {n3} 👽",
        f"👾 {n1} 👾",
        f"🤖 {n1} 🤖",
        f"🦁 {n1} 🦁",
        f"🦅 {n1} 🦅",
        f"🦂 {n2} 🦂",
        f"🐍 {n1} 🐍",
        f"🦋 {n2} 🦋",
        f"✨ {n1} ✨",
        f"🌈 {n2} 🌈",
        f"❄️ {n4} ❄️",
        f"🌟 {n1} 🌟",
        f"『GM』{n1}",
        f"╰ {n2} ╯",
        f"« {n1} »",
        f"◈ {n1} ◈",
        f"🧿 {n1} 🧿",
        f"🚀 {n1} 🚀",
        f"🧨 {n2} 🧨",
        f"🥊 {n1} 🥊",
        f"🎮 {n4} 🎮",
        f"🎯 {n1} 🎯"
    ]
    
    return styles

# --- فرمانێن بوتی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **ب خێر هاتی بۆ بوتێ زخره‌فا VIP!**\n\n"
        "⌨️ ناڤێ خۆ بفرێكه (ئینگلیزی یان عەرەبی).\n"
        "ئەز دێ ب ستایلێن **Pro و Gaming** بۆ تە زخره‌ف کەم.",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if len(name) > 20:
        await update.message.reply_text("❌ ناڤ زۆر درێژە!")
        return

    m = await update.message.reply_text("💎 دهێتە زخره‌فکرن ب ستایلێن VIP...")
    
    styles = get_pro_decorations(name)
    
    response = f"✅ **زخره‌فا VIP بۆ ناڤێ:** `{name}`\n\n"
    for i, st in enumerate(styles, 1):
        response += f"{i}. `{st}`\n"
    
    # پارچەکرنا نامێ ئەگەر زۆر درێژ بوو
    if len(response) > 4000:
        await m.edit_text(response[:4000], parse_mode='Markdown')
        await update.message.reply_text(response[4000:], parse_mode='Markdown')
    else:
        await m.edit_text(response, parse_mode='Markdown')

async def post_init(application: Application):
    await application.bot.set_my_commands([BotCommand("start", "دەسپێکرنا بوتی")])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

import os
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا تۆکنی
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- مێشکێ زخره‌فێ (٤٠+ ستایلێن پڕۆ) ---

def decorate_pro(name):
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    normal = lower + upper
    
    # فۆنتێن ئینگلیزی (هەمی پیت ب درستی هاتینە رێکخستن)
    f1 = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆Ｈ𝐈𝐉𝐊𝐋ＭＮ𝐎𝐏𝐐𝐑𝐒Ｔ𝐔𝐕𝐖Ｘ𝐘𝐙"
    f2 = "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀ＮＯ𝑃𝑄𝑅𝑆ＴＵＶ𝑊ＸＹＺ"
    f3 = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟𝐸𝐹𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    f4 = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
    f5 = "𝕒𝒷𝕔𝒹𝕖𝒻𝕘𝒽𝕚𝒿𝓀𝓁𝓂𝕟𝕠𝕡𝕢𝓇𝕤𝕥𝓊𝓋𝕨𝓍𝓎𝓏𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"

    s = [
        name.translate(str.maketrans(normal, f1)),
        name.translate(str.maketrans(normal, f2)),
        name.translate(str.maketrans(normal, f3)),
        name.translate(str.maketrans(normal, f4)),
        name.translate(str.maketrans(normal, f5))
    ]

    # شێوازێن ب نیشان و هێمایێن Gaming & Pro
    patterns = [
        "꧁ {} ꧂", "『 {} 』", "★ {} ★", "⚡ {} ⚡", "ツ {} ツ", "〆 {} 〆",
        "亗 {} 亗", "『VİP』{}", "♛ {} ♛", "🔥 {} 🔥", "✨ {} ✨", "💎 {} 💎",
        "👑 {} 👑", "⚔️ {} ⚔️", "💠 {} 💠", "╰ {} ╯", "『GM』{}", "☯ {} ☯",
        "⚓ {} ⚓", "░ {} ░", "▓ {} ▓", "🚫 {} 🚫", "『PRO』{}", "💀 {} 💀",
        "👻 {} 👻", "👽 {} 👽", "༺ {} ༻", "↜ {} ↝", "⌁ {} ⌉", "︻ {} ︼",
        "⫷ {} ⫸", "⫹ {} ⫺", "◤ {} ◥", "☬ {} ☬", "◈ {} ◈", "『A』{}",
        "『S』{}", "『Z』{}", "『X』{}", "『M』{}", "『K』{}"
    ]
    
    for p in patterns:
        s.append(p.format(name))
        
    return s[:45]

# --- فرمانێن بەرسڤدانێ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **ب خێر هاتی بۆ بوتێ زخره‌فا بادینان (ڤێرژنێ پڕۆ)!**\n\n"
        "⌨️ تەنێ ناڤێ خۆ بفرێكه دا ب **٤٠ شێوازێن جودا** بۆ تە زخره‌ف کەم.\n\n"
        "✨ کلیک ل سەر ناڤی بکە دێ کۆپی بیت.",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if len(name) > 25:
        await update.message.reply_text("❌ ئەڤ ناڤە زۆر درێژە!")
        return

    m = await update.message.reply_text("💎 **دهێتە زخره‌فکرن...**")
    
    styles = decorate_pro(name)
    response = f"✅ **زخره‌فا ناڤێ:** `{name}`\n\n"
    for i, st in enumerate(styles, 1):
        response += f"{i}. `{st}`\n"
    
    try:
        await m.edit_text(response, parse_mode='Markdown')
    except:
        await m.edit_text(response[:4000], parse_mode='Markdown')
        await update.message.reply_text(response[4000:], parse_mode='Markdown')

async def post_init(application: Application):
    await application.bot.set_my_commands([BotCommand("start", "دەسپێکرنا بوتی")])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == '__main__':
    main()

import os
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# وەرگرتنا تۆکنی ژ Railway
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- پشکا مێشکێ زخره‌فێ (Decoration Logic) ---

def decorate_name(name):
    styles = []
    
    # هندەک ژ نه‌خشێن ئینگلیزی (English Fonts)
    map_bold = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝐚ｂ𝐜𝐝𝐞𝐟𝐠𝐡𝐢ｊｋｌ𝐦𝐧ｏ𝐩ｑ𝐫𝐬𝐭𝐮𝐯𝐰ｘ𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆Ｈ𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏Ｑ𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")
    map_italic = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝘢ｂ𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡")
    map_script = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵")
    map_gothic = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉 or ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔗𝔙𝔚𝔛𝔜ℨ")

    # درستکرنا لیستەکا نه‌خشان (Borders & Symbols)
    patterns = [
        "★ {} ★", "☆ {} ☆", "꧁ {} ꧂", "『 {} 』", "【 {} 】", "⚡ {} ⚡",
        "ツ {} ツ", "〆 {} 〆", "亗 {} 亗", "『VİP』{}", "♛ {} ♛", "🔥 {} 🔥",
        "✨ {} ✨", "💎 {} 💎", "🌹 {} 🌹", "👑 {} 👑", "⚔️ {} ⚔️", "💠 {} 💠",
        "╰ {} ╯", "『GM』{}", "☯ {} ☯", "☾ {} ☽", "⚚ {} ⚚", "⚓ {} ⚓",
        "『S』{}", "░ {} ░", "▓ {} ▓", "『A』{}", "🚫 {} 🚫", "💢 {} 💢",
        "『PRO』{}", "👾 {} 👾", "💀 {} 💀", "👻 {} 👻", "👽 {}  culinary",
        "『K』{}", "『H』{}", "『O』{}", "『N』{}", "『A』{}", "『R』{}"
    ]

    # زێدەکرنا فۆنتان
    styles.append(name.translate(map_bold))
    styles.append(name.translate(map_italic))
    styles.append(name.translate(map_script))
    styles.append(name.translate(map_gothic))

    # تێکەلکرنا نه‌خشان دگه‌ل ناڤی
    for p in patterns:
        styles.append(p.format(name))
    
    # ئەگەر عەرەبی بیت، هندەک هندەک نیشانێن جودا
    styles.append(f"ـہہـ٨ـــ٨ـ {name} ـہہـ٨ـــ٨ـ")
    styles.append(f"«۩» {name} «۩»")
    styles.append(f"•]•• {name} ••[•")
    styles.append(f"◈ {name} ◈")
    
    return styles[:50] # ڤه‌گه‌ڕاندنا ٥٠ ستایڵان

# --- فرمانێن بوتی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **ب خێر هاتی بۆ بوتێ زخره‌فا بادینان!**\n\n"
        "تەنێ ناڤێ خۆ ب ئینگلیزی یان عەرەبی بفرێكه، ئەز دێ ب ٥٠ شێوازێن پڕۆ و سەرنجڕاکێش بۆ تە زخره‌ف کەم.\n\n"
        "نموونه: `Honar` یان `هونەر`",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if len(name) > 30:
        await update.message.reply_text("❌ ئەڤ ناڤە زۆر درێژە!")
        return

    m = await update.message.reply_text("💎 دهێتە زخره‌فکرن...")
    
    styles = decorate_name(name)
    
    # رێکخستنا ئەنجامی ب شێوازەکێ کو بکارهێنەر ب کلیکەکێ کۆپی بکەت
    response = "✅ **ئەڤە ژی ٥٠ شێوازێن زخره‌فکری:**\n(کلیکێ ل سەر هەر ئێکێ بکە بۆ کۆپیکرنێ)\n\n"
    for s in styles:
        response += f"`{s}`\n"
    
    try:
        await m.edit_text(response, parse_mode='Markdown')
    except:
        # ئەگەر تێكست زۆر درێژ بوو، دێ کەینە دوو نامە
        await m.edit_text(response[:4000], parse_mode='Markdown')
        await update.message.reply_text(response[4000:], parse_mode='Markdown')

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "دەسپێکرنا بوتی")
    ])

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Decoration Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

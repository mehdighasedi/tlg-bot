import logging
import random
import json
import os
from datetime import datetime, date
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, filters, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── اسم و آیدی متین (آیدی عددی یا یوزرنیم بدون @) ──────────────────────────
MATIN_USERNAME = os.getenv("MATIN_USERNAME", "matin_username")  # یوزرنیم متین بدون @
MATIN_USER_ID  = int(os.getenv("MATIN_USER_ID", "0"))           # آیدی عددی متین (اختیاری)
BOT_TOKEN      = os.getenv("BOT_TOKEN", "")

COUNTER_FILE = "matin_counter.json"

# ── لود/ذخیره شمارنده ────────────────────────────────────────────────────────
def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            return json.load(f)
    return {"date": str(date.today()), "count": 0}

def save_counter(data):
    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)

def get_and_increment():
    data = load_counter()
    if data["date"] != str(date.today()):
        data = {"date": str(date.today()), "count": 0}
    data["count"] += 1
    save_counter(data)
    return data["count"]

# ── تشخیص صبح/ظهر/شب ────────────────────────────────────────────────────────
def time_greeting():
    h = datetime.now().hour
    if 5 <= h < 12:
        return "morning"
    elif 12 <= h < 18:
        return "noon"
    else:
        return "night"

# ── ایموجی‌های رندوم ──────────────────────────────────────────────────────────
EMOJIS = ["💀", "🤡", "🗑️", "🤦", "😂", "👎", "🤮", "🙄", "💩", "😬", "🫠", "🤣", "😐", "🤧", "🥴"]

def rand_emoji(n=1):
    return " ".join(random.choices(EMOJIS, k=n))

# ── جواب‌های وقتی متین پیام میده ─────────────────────────────────────────────
MATIN_SPEAKS = {
    "morning": [
        "اوف، باز متین اومد زر بزنه از صبح {rand_emoji}",
        "صبح شد و متین کسخول شروع کرد به بد و بیراه {rand_emoji}",
        "بچه‌ها متین بیدار شد، خدا به داد گروه برسه {rand_emoji}",
        "اینقدر متین حرف میزنه آدم صبح‌ها بی‌خواب میشه {rand_emoji}",
        "متین جان صبح بخیر، یعنی میشه یه روز ساکت باشی؟ {rand_emoji}",
    ],
    "noon": [
        "اوف دوباره این اومد، ظهر هم ولمون نمیکنه {rand_emoji}",
        "متین ظهره، ناهار نخور، زر نزن {rand_emoji}",
        "باز این متین زر زد، کسخول‌ترین آدم گروهه {rand_emoji}",
        "بچه‌ها ببینید متین چی میگه 😂 خودش هم نمیفهمه {rand_emoji}",
        "یا خدا، متین دوباره پیام داد {rand_emoji}",
    ],
    "night": [
        "متین شبم ولمون نمیکنه، دیوونه‌ی کامله {rand_emoji}",
        "شب شد و متین کسخول هنوز داره زر میزنه {rand_emoji}",
        "برو بخواب متین، همه خسته‌ان از دستت {rand_emoji}",
        "اوف دوباره این اومد، نمیخوابی؟ {rand_emoji}",
        "متین جان شبه، برو گم شو {rand_emoji}",
    ],
}

# ── جواب‌های وقتی بات رو منشن میکنن ─────────────────────────────────────────
MENTION_RESPONSES = [
    "چیه؟ داری از متین دفاع میکنی؟ متین کسخوله {rand_emoji}",
    "من فقط یه چیز میدونم: متین دیوونه‌ست {rand_emoji}",
    "متین؟ آره میشناسمش، بزرگترین مزخرف‌گوی گروهه {rand_emoji}",
    "الان وقت دفاع از متینه؟ {rand_emoji} برو بابا",
    "متین اونقدر بی‌خود حرف میزنه که مغزم درد میگیره {rand_emoji}",
    "هرکی از متین دفاع کنه هم‌سطح خودشه {rand_emoji}",
    "از من خواستی بگم؟ باشه: متین کله‌پوکه {rand_emoji}",
    "چرا منشنم کردی؟ بگو چیکار کنم با این متین {rand_emoji}",
    "خب؟ میخوای بگم متین چقدر بی‌کلاسه؟ {rand_emoji}",
    "متین به درد لای جرز دیوار میخوره {rand_emoji}",
]

# ── جواب‌های بلند گاه‌به‌گاه (۱۵٪ شانس) ───────────────────────────────────
LONG_RESPONSES_MATIN = [
    (
        "یه لحظه بچه‌ها، متین دوباره پیام داد {rand_emoji}\n\n"
        "بذارید یه آمار بدم: متین تو گروه بیشتر از همه زر میزنه، "
        "کمتر از همه چیز میفهمه، و بیشتر از همه فکر میکنه باحاله.\n"
        "خلاصه: کسخول‌ترین آدم گروه، متینه. {rand_emoji}"
    ),
    (
        "اوه اوه، متین اومد {rand_emoji}\n\n"
        "راستش رو بخواید من هر دفعه اسم متین میاد یه چیزی تو دلم میمیره.\n"
        "نه از ترس، از خجالت که همچین آدمی تو گروهمونه.\n"
        "متین عزیز، برو یه فن‌پیج برا خودت بساز، شاید یکی اونجا تحملت کنه {rand_emoji}"
    ),
    (
        "بچه‌ها توجه کنید! {rand_emoji}\n\n"
        "متین دوباره زر زد، این {count}مین بار امروزه!\n"
        "آدم واقعاً تعجب میکنه یه نفر اینقدر وقت داره مزخرف بگه.\n"
        "متین جان، یه روز ساکت باش، جهان باهات کنار میاد {rand_emoji}"
    ),
]

# ── سازنده پیام ──────────────────────────────────────────────────────────────
def build_message(template: str, count: int = 0) -> str:
    emoji = rand_emoji(random.randint(1, 3))
    return template.replace("{rand_emoji}", emoji).replace("{count}", str(count))

# ── هندلر پیام‌ها ────────────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user = msg.from_user
    text = msg.text or msg.caption or ""
    bot_username = context.bot.username

    is_matin = False
    if MATIN_USER_ID and user.id == MATIN_USER_ID:
        is_matin = True
    elif user.username and user.username.lower() == MATIN_USERNAME.lower():
        is_matin = True

    is_mention = bot_username and f"@{bot_username}".lower() in text.lower()

    if is_matin:
        count = get_and_increment()
        period = time_greeting()

        # ۱۵٪ شانس جواب بلند
        if random.random() < 0.15:
            template = random.choice(LONG_RESPONSES_MATIN)
            reply = build_message(template, count)
        else:
            pool = MATIN_SPEAKS[period]
            template = random.choice(pool)
            reply = build_message(template, count)

        # اضافه کردن شمارنده به آخر پیام
        reply += f"\n\n📊 متین امروز {count} بار زر زده!"
        await msg.reply_text(reply)

    elif is_mention:
        template = random.choice(MENTION_RESPONSES)
        reply = build_message(template)
        await msg.reply_text(reply)

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN محیطی تنظیم نشده!")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_message))

    logger.info("ربات متین شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

import logging
import json
import os
import random
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

MATIN_USERNAME = os.getenv("MATIN_USERNAME", "matin_username")
MATIN_USER_ID  = int(os.getenv("MATIN_USER_ID", "0"))
BOT_TOKEN      = os.getenv("BOT_TOKEN", "")

COUNTER_FILE = "matin_counter.json"

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

def get_count():
    data = load_counter()
    if data["date"] != str(date.today()):
        return 0
    return data["count"]

def time_of_day():
    h = datetime.now().hour
    if 5 <= h < 12:
        return "morning"
    elif 12 <= h < 18:
        return "noon"
    else:
        return "night"

EMOJIS = ["💀", "🤡", "🗑️", "🤦", "😂", "👎", "🤮", "🙄", "💩", "😬", "🫠", "🤣", "😐", "🤧", "🥴", "☠️", "🫵", "🤌"]

def e(n=1):
    return " ".join(random.choices(EMOJIS, k=n))

# ── وقتی متین پیام میده ───────────────────────────────────────────────────────
MATIN_MORNING = [
    f"اوف صبح اول وقت متین کسخول اومد {e()}",
    f"بچه‌ها متین بیدار شد خدا به داد گروه برسه {e()}",
    f"صبح بخیر متین، امیدوارم امروز کمتر زر بزنی {e()}",
    f"یا امام متین از خواب پاشد، روزمون خراب شد {e()}",
    f"هنوز صبحه این خنگول داره مزخرف میگه {e()}",
    f"متین جان صبح بخیر، یعنی میشه یه روز ساکت باشی؟ {e()}",
    f"اَه متین، مگه نگفتم صبح‌ها منو اذیت نکن {e()}",
    f"بچه‌ها سایلنت کنید متین داره هذیون میگه از صبح {e()}",
    f"متین جان برو دندونات رو مسواک بزن بعد بیا گروه {e()}",
    f"هر روز صبح با زر زدن متین شروع میشه، چه زندگیه {e()}",
    f"متین عزیزم، صبحانه خوردی؟ نه؟ برو بخور دهنت رو ببند {e()}",
    f"باز این متین بیدار شد، گروه رو سایلنت کنید {e()}",
]

MATIN_NOON = [
    f"اوف دوباره این اومد، ظهر هم ولمون نمیکنه {e()}",
    f"متین ظهره، ناهار نخور، زر نزن کسخول {e()}",
    f"باز این متین زر زد، بی‌شعورترین آدم گروهه {e()}",
    f"یا خدا متین دوباره پیام داد، این مرض داره {e()}",
    f"متین جان غذا خوردی؟ برو غذات رو بخور بذار گروه نفس بکشه {e()}",
    f"ظهر شد و متین کله‌پوک هنوز داره حرف میزنه {e()}",
    f"این متین اگه به اندازه زر زدنش کار میکرد الان میلیاردر بود {e()}",
    f"متین مثل یه سطل زباله‌ست، هر چرتی تو ذهنشه میریزه تو گروه {e()}",
    f"خب متین جان، چرت و پرت جدیدی داری؟ {e()}",
    f"بچه‌ها ببینید متین چی میگه {e()} خودش هم نمیفهمه چرت و پرت میگه",
    f"متین یه بار تو زندگیش چیز درست حسابی گفت، اون وقتی بود که ساکت بود {e()}",
    f"آخه متین کسخول چرا اینقدر حرف میزنی؟ {e()}",
]

MATIN_NIGHT = [
    f"متین شبم ولمون نمیکنه، دیوونه‌ی کامله {e()}",
    f"شب شد و متین کسخول هنوز داره زر میزنه، برو بخواب بابا {e()}",
    f"برو بخواب متین، همه خسته‌ان از دستت {e()}",
    f"اوف دوباره این اومد، مگه شب نیست؟ نمیخوابی؟ {e()}",
    f"متین جان شبه، برو گم شو بذار بقیه راحت باشن {e()}",
    f"این متین شب‌ها هم آدم رو اذیت میکنه، روانیه {e()}",
    f"ساعت خوابیدنته متین، نه زر زدن {e()}",
    f"متین هنوز بیداره؟ خدایا این بنده‌ات رو به راه هدایت کن {e()}",
    f"بچه‌ها متین خوابش نمیبره، نگرانشم {e()}",
    f"متین شب هم راحتمون نمیذاره، کسخول بی‌همتاست {e()}",
    f"برو بخواب متین الان ساعت خوابه نه مزخرف گفتن {e()}",
    f"متین عزیز شب بخیر، یعنی بخواب دیگه {e()}",
]

MATIN_LONG = [
    (
        "📢 اطلاعیه مهم!\n\n"
        "متین دوباره پیام داد.\n"
        "🔴 بیشترین زر زدن گروه: متین\n"
        "🔴 کمترین فهم گروه: متین\n"
        "🔴 بیشترین مزخرف‌گویی: متین\n\n"
        f"خلاصه: کسخول‌ترین آدم گروه، متینه {e(2)}"
    ),
    (
        f"اوه اوه متین اومد {e()}\n\n"
        "من هر دفعه اسم متین میاد یه چیزی تو دلم میمیره.\n"
        "نه از ترس، از خجالت که همچین خنگی تو گروهمونه.\n"
        f"متین عزیز برو یه فن‌پیج برا خودت بساز {e()}"
    ),
    (
        "صبر کنید بچه‌ها، متین داره حرف میزنه...\n\n"
        "....\n"
        "....\n"
        "باشه شنیدم.\n\n"
        f"خلاصه‌اش: چرت و پرت. مثل همیشه متین {e(2)}"
    ),
    (
        f"متین جان یه سوال دارم ازت {e()}\n\n"
        "چطوره یه بار، فقط یه بار، قبل از اینکه پیام بدی فکر کنی؟\n"
        "میدونم برات سخته، مغزت عادت نداره.\n"
        f"ولی یه تلاش کوچیک بکن {e()}"
    ),
    (
        f"بچه‌ها توجه {e(2)}\n\n"
        "متین الان پیام داد.\n"
        "لطفاً همه سایلنت کنید تا این طوفان بگذره.\n"
        f"متین جان یه روز ساکت باش، جهان باهات کنار میاد {e()}"
    ),
    (
        "تحلیل پیام متین:\n\n"
        "✅ مزخرف بودن: ۱۰۰٪\n"
        "✅ بی‌ربط بودن: ۱۰۰٪\n"
        "✅ کسخول بودن: ۱۰۰٪\n"
        "❌ منطق: ۰٪\n"
        "❌ شعور: ۰٪\n\n"
        f"نتیجه: متین {e()}"
    ),
]

# ── وقتی کسی اسم متین رو میاره ───────────────────────────────────────────────
MATIN_MENTIONED = [
    f"متین؟ آره میشناسمش، کسخول‌ترین آدم گروهه {e()}",
    f"اسم متین اومد، باید بگم: این آدم خنگوله {e()}",
    f"متین رو گفتی؟ آره دیوونه‌ست، همه میدونیم {e()}",
    f"هرجا اسم متین میاد من باید بگم: کسخوله {e()}",
    f"متین؟ اون که مشکل داره {e()}",
    f"آره متین بی‌عرضه‌ست، این که خبر نیست {e()}",
    f"متین یه آدم کله‌پوکه که فکر میکنه باحاله {e()}",
    f"اسم متین که میاد دلم میگیره {e()} این آدم چقدر خنگه",
    f"متین؟ اون که همیشه مزخرف میگه؟ آره میشناسمش {e()}",
    f"هرکی اسم متین رو بیاره باید بدونه که متین کسخوله {e()}",
    f"متین جان اگه داری میخونی بدون که همه میدونن خنگی {e()}",
    f"متین از اون آدماست که وقتی حرف میزنه همه آرزو میکنن ساکت بشه {e()}",
    f"راستش رو بخوای متین یه پدیده‌ست، پدیده کسخولی {e()}",
    f"متین تو گروه مثل یه باگه، همیشه هست و همیشه اذیت میکنه {e()}",
]

# ── وقتی ربات رو صدا میزنن یا منشن میکنن ────────────────────────────────────
MENTION_RESPONSES = [
    f"جانم؟ بگو چیکارت دارم {e()}",
    f"بله؟ البته متین کسخوله، این رو هم بدون {e()}",
    f"صدام زدی؟ چیزی از متین میخوای بدونی؟ بگو کسخوله {e()}",
    f"اینجام! ولی اول بگم متین دیوونه‌ست {e()}",
    f"بله؟ ضمناً متین امروز هم زر زد {e()}",
    f"جانم؟ هر چیزی بخوای بگم ولی متین کله‌پوکه {e()}",
    f"اومدم! متین رو داری؟ نه؟ خوبه {e()}",
    f"بله عزیزم؟ متین مزخرف‌گوعه، این رو فراموش نکن {e()}",
    f"صدام کردی؟ کارم اینه که بگم متین خنگه {e()}",
    f"اینجام! راستی متین امروز چند بار زر زده؟ {e()}",
    f"چطور میتونم کمکت کنم؟ غیر از اینکه بگم متین بی‌عرضه‌ست {e()}",
    f"بله؟ یادآوری روزانه: متین کسخوله {e()}",
]

BOT_NAMES = ["ربات", "بات", "bot", "ربات متین"]
MATIN_KEYWORDS = ["متین", "matin", "m_a_t_i_n"]

def mentions_matin(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in MATIN_KEYWORDS)

def should_respond(text: str, bot_username: str, msg) -> bool:
    t = text.lower()
    if bot_username and f"@{bot_username}".lower() in t:
        return True
    for name in BOT_NAMES:
        if name in t:
            return True
    if mentions_matin(text):
        return True
    if (msg.reply_to_message and
            msg.reply_to_message.from_user and
            msg.reply_to_message.from_user.username and
            bot_username and
            msg.reply_to_message.from_user.username.lower() == bot_username.lower()):
        return True
    return False

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

    if is_matin:
        count = get_and_increment()

        if random.random() < 0.2:
            reply = random.choice(MATIN_LONG)
            reply = reply.replace("{count}", str(count))
        else:
            pool = {
                "morning": MATIN_MORNING,
                "noon": MATIN_NOON,
                "night": MATIN_NIGHT,
            }[time_of_day()]
            reply = random.choice(pool)

        reply += f"\n\n📊 متین امروز {count} بار زر زده!"
        await msg.reply_text(reply)

    elif should_respond(text, bot_username, msg):
        if mentions_matin(text) and not any(n in text.lower() for n in [f"@{bot_username}".lower() if bot_username else ""] + [n for n in BOT_NAMES]):
            reply = random.choice(MATIN_MENTIONED)
        else:
            reply = random.choice(MENTION_RESPONSES)
        await msg.reply_text(reply)

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده!")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_message))

    logger.info("ربات متین شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

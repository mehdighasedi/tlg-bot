import logging
import json
import os
import random
from datetime import datetime, date
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, ChatMemberHandler, filters, ContextTypes
)
from roasts import ALL_ROASTS

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

E = ["💀","🤡","🗑️","🤦","😂","👎","🤮","🙄","💩","😬","🫠","🤣","😐","🤧","🥴","☠️","🫵","🤌","👻","🧠","🪣","🐒","🤪"]

def e(n=1):
    return " ".join(random.choices(E, k=n))

JOIN_MESSAGES = [
    f"سلام بچه‌ها! {e(2)}\nمنم ربات متین، اومدم اینجا یه وظیفه مهم دارم:\nهر وقت متین کسخول پیام داد، بهش فحش بدم.\nخلاصه: متین بدبخت شد {e(2)}",
    f"اومدم! {e()}\nربات متین در خدمت گروهه.\nوظیفه‌ام اینه که هر وقت متینِ کله‌پوک دهن باز کرد، ببندمش.\nمتین عزیز اگه میخونی: سلام، بدبخت شدی {e(2)}",
    f"به به! ربات متین وارد شد!\nاز این به بعد متین هر چی بگه جواب میگیره.\nبچه‌ها خوش باشید، متین نه {e(3)}",
    f"درود بر گروه! {e()}\nمن ربات متینم، تخصصم:\n✅ فحش دادن به متین\n✅ مسخره کردن متین\n✅ یادآوری اینکه متین کسخوله\n❌ دفاع از متین\n\nآماده‌ام {e(2)}",
]

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
    f"متین عزیزم صبحانه خوردی؟ نه؟ برو بخور دهنت رو ببند {e()}",
    f"باز این متین بیدار شد، گروه رو سایلنت کنید {e()}",
    f"کاش متین صبح‌ها دیرتر بیدار میشد {e()}",
    f"صبح شد و اولین کسی که زر زد متین بود، تعجب نکردم {e()}",
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
    f"متین یه بار تو زندگیش چیز درست حسابی گفت، اون وقتی بود که ساکت بود {e()}",
    f"آخه متین کسخول چرا اینقدر حرف میزنی؟ {e()}",
    f"متین هر بار پیام میده یه سلول مغزی از من میمیره {e()}",
    f"اگه مزخرف گفتن المپیک داشت متین طلا میگرفت {e()}",
    f"متین جان لطفاً یه روز مرخصی بده به گروه {e()}",
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
    f"شب شد ولی متین هنوز داره غلط میکنه {e()}",
    f"همه دارن میخوابن فقط متین کسخول بیداره {e()}",
]

MATIN_LONG = [
    f"📢 اطلاعیه مهم!\n\nمتین دوباره پیام داد.\n🔴 بیشترین زر زدن: متین\n🔴 کمترین فهم: متین\n🔴 بیشترین مزخرف: متین\n🔴 بی‌عرضه‌ترین: متین\n\nخلاصه: کسخول‌ترین آدم گروه، متینه {e(2)}",
    f"اوه اوه متین اومد {e()}\n\nمن هر دفعه اسم متین میاد یه چیزی تو دلم میمیره.\nنه از ترس، از خجالت که همچین خنگی تو گروهمونه.\nمتین عزیز برو یه فن‌پیج برا خودت بساز {e()}",
    f"صبر کنید بچه‌ها، متین داره حرف میزنه...\n\n....\n....\nباشه شنیدم.\n\nخلاصه‌اش: چرت و پرت. مثل همیشه متین {e(2)}",
    f"تحلیل پیام متین:\n\n✅ مزخرف بودن: ۱۰۰٪\n✅ بی‌ربط بودن: ۱۰۰٪\n✅ کسخول بودن: ۱۰۰٪\n❌ منطق: ۰٪\n❌ شعور: ۰٪\n❌ مغز: ۰٪\n\nنتیجه: متین {e(3)}",
    f"کارنامه متین:\n\n📌 تعداد مزخرفات: خیلی زیاد\n📌 تعداد حرف‌های درست: صفر\n📌 تعداد باری که کسی تحملش کرده: نزدیک به صفر\n📌 میزان خنگی: خارج از محدوده اندازه‌گیری\n\nمتین تو یه نوع هنر داری، هنر کسخول بودن {e(2)}",
    f"یه لحظه {e()}\n\nالان متین پیام داد.\nمیخوام همه یه دقیقه سکوت کنیم.\nنه به احترام متین،\nبلکه از تعجب که این آدم هنوز داره زر میزنه.\n\nمتین کسخول، این هنر توئه {e()}",
    f"📊 نمودار متین:\n\nزر زدن: ████████████ ۱۰۰٪\nشعور: ░░░░░░░░░░░░ ۰٪\nمنطق: ░░░░░░░░░░░░ ۰٪\nادب: ░░░░░░░░░░░░ ۰٪\nفایده: ░░░░░░░░░░░░ ۰٪\n\nنتیجه: متین {e(2)}",
    f"🏆 جوایز امروز:\n\n🥇 پرمزخرف‌ترین: متین\n🥇 کم‌شعورترین: متین\n🥇 پرحرف‌ترین: متین\n🥇 بی‌ربط‌ترین: متین\n\nتبریک متین، جارو زدی! {e(2)}",
]

BOT_NAMES = ["ربات", "بات", "bot", "ربات متین"]
MATIN_KEYWORDS = ["متین", "matin", "m_a_t_i_n"]

def mentions_matin(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in MATIN_KEYWORDS)

def is_reply_to_bot(msg, bot_username: str) -> bool:
    return (
        msg.reply_to_message and
        msg.reply_to_message.from_user and
        msg.reply_to_message.from_user.username and
        bot_username and
        msg.reply_to_message.from_user.username.lower() == bot_username.lower()
    )

def is_direct_call(text: str, bot_username: str) -> bool:
    t = text.lower()
    if bot_username and f"@{bot_username}".lower() in t:
        return True
    return any(name in t for name in BOT_NAMES)

def should_respond(text: str, bot_username: str, msg) -> bool:
    if is_direct_call(text, bot_username):
        return True
    if mentions_matin(text):
        return True
    if is_reply_to_bot(msg, bot_username):
        return True
    return False

async def handle_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if not result:
        return
    new_status = result.new_chat_member.status
    old_status = result.old_chat_member.status
    if new_status in ("member", "administrator") and old_status not in ("member", "administrator"):
        await context.bot.send_message(chat_id=result.chat.id, text=random.choice(JOIN_MESSAGES))

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
        else:
            pool = {"morning": MATIN_MORNING, "noon": MATIN_NOON, "night": MATIN_NIGHT}[time_of_day()]
            reply = random.choice(pool)
        reply += f"\n\n📊 متین امروز {count} بار زر زده!"
        await msg.reply_text(reply)

    elif should_respond(text, bot_username, msg):
        # ریپلای روی پیام ربات یا هر ترایگر دیگه → از لیست هزارتایی
        reply = random.choice(ALL_ROASTS)
        await msg.reply_text(reply)

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده!")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatMemberHandler(handle_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_message))

    logger.info("ربات متین شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

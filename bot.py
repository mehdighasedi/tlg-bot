import logging
import json
import os
import google.generativeai as genai
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
GEMINI_KEY     = os.getenv("GEMINI_API_KEY", "")

COUNTER_FILE = "matin_counter.json"

genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel("gemini-2.0-flash-lite")

# ── شمارنده ──────────────────────────────────────────────────────────────────
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

# ── تشخیص ساعت ───────────────────────────────────────────────────────────────
def time_of_day():
    h = datetime.now().hour
    if 5 <= h < 12:
        return "صبح"
    elif 12 <= h < 18:
        return "ظهر"
    else:
        return "شب"

# ── سیستم پرامپت برای وقتی متین پیام میده ───────────────────────────────────
SYSTEM_MATIN = """تو یه ربات تلگرامی فارسی هستی به اسم "ربات متین" که وظیفه‌ات اینه که متین رو تو گروه مسخره کنی.

متین یه آدم کسخول، خنگ، پرحرف و بی‌خودیه که هر چرتی به ذهنش میرسه تو گروه میگه.

وقتی متین پیام میده:
- با یه جمله کوتاه و تیز شروع کن که نشون بده حالت از پیام متین به هم خورده
- پیام متین رو به سخره بگیر، تحلیل کن، و نشون بده چقدر بی‌معنیه
- از کلماتی مثل کسخول، خنگول، دیوونه، کله‌پوک، بی‌عرضه، مزخرف استفاده کن
- لحن باید خنده‌دار و بامزه باشه نه پرخاشگرانه
- حداکثر ۳-۴ جمله بنویس
- فارسی محاوره‌ای بنویس
- آخرش یه چیز طعنه‌آمیز بگو
- از ایموجی‌های 💀🤡🗑️😂👎🤮🙄💩 استفاده کن"""

# ── سیستم پرامپت برای وقتی کسی منشن میکنه ──────────────────────────────────
SYSTEM_MENTION = """تو یه ربات تلگرامی فارسی هستی به اسم "ربات متین".

وظیفه‌ات اینه که:
۱. به سوال یا حرف کاربر جواب بدی (اگه سوالی پرسیده)
۲. در بین جوابت یا آخرش، یه چیز بامزه درباره متین بگی و مسخره‌اش کنی

متین یه عضو گروهه که کسخوله، پرحرفه، خنگه و همه ازش خسته‌ان.

نکات مهم:
- اول به حرف کاربر جواب بده، بعد متین رو بپیچون
- لحن باید دوستانه و خنده‌دار باشه
- فارسی محاوره‌ای بنویس
- از ایموجی استفاده کن
- حداکثر ۵-۶ جمله بنویس
- اگه کاربر سوالی نپرسیده فقط یه چیز بامزه بگو و متین رو مسخره کن"""

# ── صدا زدن Gemini ───────────────────────────────────────────────────────────
def ask_gemini(system: str, user_message: str) -> str:
    try:
        full_prompt = f"{system}\n\n---\n\n{user_message}"
        response = gemini.generate_content(full_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {type(e).__name__}: {e}")
        return None

# ── اسم‌هایی که ربات باهاشون شناخته میشه ────────────────────────────────────
BOT_NAMES = ["ربات", "بات", "bot", "matin bot", "ربات متین"]

MATIN_KEYWORDS = ["متین", "matin", "m_a_t_i_n"]

def mentions_matin(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in MATIN_KEYWORDS)

def should_respond(text: str, bot_username: str, msg) -> bool:
    text_lower = text.lower()

    # منشن مستقیم
    if bot_username and f"@{bot_username}".lower() in text_lower:
        return True

    # صدا زدن با اسم ربات
    for name in BOT_NAMES:
        if name in text_lower:
            return True

    # ذکر اسم متین
    if mentions_matin(text):
        return True

    # ریپلای روی پیام ربات
    if (msg.reply_to_message and
            msg.reply_to_message.from_user and
            msg.reply_to_message.from_user.username and
            bot_username and
            msg.reply_to_message.from_user.username.lower() == bot_username.lower()):
        return True

    return False

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

    if is_matin:
        count = get_and_increment()
        tod = time_of_day()

        prompt = (
            f"ساعت {tod} است و متین این پیام رو فرستاده: «{text}»\n"
            f"امروز {count} بار پیام داده. این اطلاعات رو هم تو جوابت استفاده کن."
        )

        reply = ask_gemini(SYSTEM_MATIN, prompt)

        if not reply:
            reply = f"متین کسخول دوباره زر زد 💀\nامروز {count} بار!"
        else:
            reply += f"\n\n📊 متین امروز {count} بار زر زده!"

        await msg.reply_text(reply)

    elif should_respond(text, bot_username, msg):
        # تمیز کردن منشن از متن
        clean_text = text
        if bot_username:
            clean_text = clean_text.replace(f"@{bot_username}", "").strip()

        # اگه ریپلای بود، متن پیام اصلی رو هم اضافه کن
        replied_text = ""
        if (msg.reply_to_message and msg.reply_to_message.text):
            replied_text = f"\nاین رو در جواب پیام قبلیم گفت: «{msg.reply_to_message.text}»"

        sender_name = user.first_name or user.username or "یه کاربر"
        matin_count = get_count()
        has_matin = mentions_matin(clean_text)

        if has_matin:
            extra = (
                f"\nتوجه: این کاربر اسم متین رو برده. "
                f"جوابت باید هم به حرف کاربر بپردازه هم متین رو مسخره کنه و خوار کنه. "
                f"متین امروز {matin_count} بار تو گروه زر زده."
            )
        else:
            extra = f"\nضمناً متین امروز {matin_count} بار تو گروه پیام داده."

        prompt = (
            f"{sender_name} در گروه این رو گفت: «{clean_text or 'سلام'}»{replied_text}{extra}"
        )

        reply = ask_gemini(SYSTEM_MENTION, prompt)

        if not reply:
            reply = "سلام! متین کسخوله، این رو همیشه بدون 😂"

        await msg.reply_text(reply)

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده!")
    if not GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY تنظیم نشده!")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_message))

    logger.info("ربات متین (با هوش مصنوعی) شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

import telebot
import time
import logging
from telebot import types

# إعداد السجلات (Logging) لمراقبة الأخطاء في الكونسول
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================
# 🔑 المعلومات الأساسية
# ======================
BOT_TOKEN = "8886084382:AAH3-CYsadKsXuaLuCmupzjiIwGkE2U8RrM"
ADMIN_IDS = [8728019066]
API_ID = 34997391
API_HASH = "f1e6c3a84f61c38b3667acd210f77e12"

CHANNEL_LINK = "https://t.me/shhsnbdb"
CHANNEL_ID = -1003908016285

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ======================
# 🚀 الدوال التفاعلية
# ======================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("قناة الأكواد 📢", url=CHANNEL_LINK)
        markup.add(btn)
        
        welcome_text = (
            "<b>❍─── 𓏺 𝙈𝙤𝙘𝙝𝙖 𝙄𝙣𝙩𝙚𝙧𝙣𝙖𝙩𝙞𝙤𝙣𝙖𝙡 𓏺 ───❍</b>\n\n"
            "<b>👤 المطور:</b> @zafer43647\n"
            "<b>🆔 الأيدي:</b> <code>8728019066</code>\n\n"
            "<b>أهلاً بك في بوت Mocha للخدمات الاحترافية.</b>"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    except Exception as e:
        logger.error(f"خطأ في رسالة البدء: {e}")

# ======================
# 🔄 حلقة التشغيل مع حماية من التوقف
# ======================
if __name__ == "__main__":
    while True:
        try:
            logger.info("🚀 جاري تشغيل بوت Mocha...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logger.error(f"⚠️ توقف البوت بسبب خطأ: {e}")
            logger.info("🔄 إعادة التشغيل بعد 5 ثوانٍ...")
            time.sleep(5)

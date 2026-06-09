import sqlite3
import telebot
import random
import os
from telebot import types

# ======================
# ⚙️ إعدادات المطور (ضع بياناتك هنا)
# ======================
# يفضل استخدام os.getenv لقراءة البيانات من إعدادات السيرفر (Environment Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_هنا")
ADMIN_IDS = [8728019066] # أيدي المطور
DB_PATH = "bot.db"

# ======================
# 🔗 إعدادات القنوات والروابط
# ======================
CHANNEL_LINK = "https://t.me/shhsnbdb"
CHANNEL_ID = -1003908016285

# ======================
# 🔌 إعدادات API (الخاصة بتليجرام)
# ======================
API_ID = 34997391
API_HASH = "f1e6c3a84f61c38b3667acd210f77e12"

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# 🛠️ هيكلية الدالة الأساسية (مثال للاستخدام)
# ======================
def get_available_numbers(country_code):
    # هنا يتم استدعاء اللوحة التي تعمل عليها
    # تذكر: لا تضع أي باسورد مباشر هنا، استخدم متغيرات البيئة
    pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("قناة الأكواد 📢", url=CHANNEL_LINK)
    markup.add(btn)
    
    welcome_text = (
        "<b>مرحباً بك في بوت Mocha International</b>\n\n"
        "<b>المطور:</b> @zafer43647\n"
        "<b>أهلاً بك في خدماتنا الاحترافية.</b>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    print("🚀 البوت يعمل الآن..")
    bot.polling(none_stop=True)

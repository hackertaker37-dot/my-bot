import telebot
import os
from telebot import types

# ======================
# 🔑 معلوماتك الحقيقية (تمت الإضافة)
# ======================
BOT_TOKEN = "8886084382:AAH3-CYsadKsXuaLuCmupzjiIwGkE2U8RrM"
ADMIN_IDS = [8728019066]
API_ID = 34997391
API_HASH = "f1e6c3a84f61c38b3667acd210f77e12"

# 📢 معلومات القناة
CHANNEL_LINK = "https://t.me/shhsnbdb"
CHANNEL_ID = -1003908016285

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# 🚀 تشغيل البوت
# ======================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("قناة الأكواد 📢", url=CHANNEL_LINK)
    markup.add(btn)
    
    welcome_text = (
        "<b>❍─── 𓏺 𝙈𝙤𝙘𝙝𝙖 𝙄𝙣𝙩𝙚𝙧𝙣𝙖𝙩𝙞𝙤𝙣𝙖𝙡 𓏺 ───❍</b>\n\n"
        "<b>👤 المطور:</b> @zafer43647\n"
        "<b>🆔 الأيدي:</b> <code>8728019066</code>\n\n"
        "<b>أهلاً بك في بوت Mocha للخدمات الاحترافية.</b>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    print("🚀 تم تفعيل معلومات Mocha بنجاح.. البوت يعمل الآن")
    bot.polling(none_stop=True)

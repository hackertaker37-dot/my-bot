# -*- coding: utf-8 -*-
import time
import requests
import json
import re
import os
import sqlite3
import telebot
from telebot import types
import threading
import random
from datetime import datetime
from flask import Flask

print("✅ Bot is starting...")

# ======================
# 🔧 التوكن والإعدادات
# ======================
BOT_TOKEN = "8719786806:AAFs9X2Xntzv62-fQdw2OwSQWgoXkE9wOlU"
ADMIN_IDS = [8728019066, 8972941677]
CHAT_IDS = ["-1003789271722"]
DB_PATH = "bot1.db"
BOT_ACTIVE = True

# ======================
# 🧰 قاعدة البيانات
# ======================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            first_seen TEXT,
            last_seen TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ======================
# 🤖 إنشاء البوت
# ======================
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# 🏠 أمر /start
# ======================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # حفظ المستخدم
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (user_id, username, first_name, last_name, first_seen, last_seen) VALUES (?,?,?,?,?,?)",
                      (user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 
                       datetime.now().isoformat(), datetime.now().isoformat()))
        else:
            c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
    except:
        pass
    
    # رسالة الترحيب
    welcome_text = (
        "✨ *أهلاً بك في بوت Taker2 OTP* ✨\n\n"
        "🔹 البوت يعمل بنجاح ✅\n"
        "🔹 جاهز لاستقبال طلباتك\n\n"
        "📌 *استخدم الأزرار أدناه:*"
    )
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📱 احصل على رقم"),
        types.KeyboardButton("📊 إحصائياتي")
    )
    markup.add(
        types.KeyboardButton("💰 رصيدي"),
        types.KeyboardButton("🤝 دعوة")
    )
    
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ======================
# 📊 إحصائيات
# ======================
@bot.message_handler(func=lambda m: m.text == "📊 إحصائياتي")
def stats_handler(message):
    user_id = message.from_user.id
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT first_seen, last_seen FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            text = f"📊 *إحصائياتك*\n\n🟢 أول استخدام: {row[0][:16]}\n🔵 آخر استخدام: {row[1][:16]}"
        else:
            text = "📊 *لا توجد إحصائيات*"
    except:
        text = "📊 *حدث خطأ*"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ======================
# 💰 الرصيد
# ======================
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def balance_handler(message):
    text = "💰 *رصيدك*\n\n💎 رصيدك الحالي: `0.00 USDT`\n\n💡 اربح 0.05 USDT عن كل صديق"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ======================
# 🤝 دعوة
# ======================
@bot.message_handler(func=lambda m: m.text == "🤝 دعوة")
def invite_handler(message):
    user_id = message.from_user.id
    link = f"https://t.me/Taker2_OTP_BOT?start=ref{user_id}"
    text = f"🤝 *دعوة الأصدقاء*\n\n🔗 رابط دعوتك:\n`{link}`\n\n📤 شارك الرابط مع أصدقائك"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ======================
# 📱 احصل على رقم
# ======================
@bot.message_handler(func=lambda m: m.text == "📱 احصل على رقم")
def get_number_handler(message):
    text = "📱 *احصل على رقم*\n\n🔹 الخدمة قيد التطوير\n🔹 سيتم إضافة الأرقام قريباً"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ======================
# ▶️ تشغيل البوت
# ======================
def run_bot():
    print("🤖 Bot is running...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

# ======================
# 🖥️ Flask للـ Render
# ======================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Taker2 OTP Bot is running!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "Taker2 OTP"}

if __name__ == "__main__":
    # تشغيل البوت في الخلفية
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل Flask
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

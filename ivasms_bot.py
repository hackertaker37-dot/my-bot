import telebot
from flask import Flask
import os
import threading
import time

# ========== التوكن ==========
BOT_TOKEN = "8719786806:AAFs9X2Xntzv62-fQdw2OwSQWgoXkE9wOlU"

# ========== إنشاء البوت ==========
bot = telebot.TeleBot(BOT_TOKEN)

# ========== أمر /start ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ البوت شغال! \nمرحباً بك في Taker2 OTP")

# ========== تشغيل البوت ==========
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# ========== Flask ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Taker2 OTP Bot is running!"

if __name__ == "__main__":
    # شغال البوت في الخلفية
    threading.Thread(target=run_bot, daemon=True).start()
    # شغال Flask
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

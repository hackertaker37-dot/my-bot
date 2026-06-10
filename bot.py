import telebot
import requests
import logging

# إعداد السجلات لمراقبة أخطاء البوت
logging.basicConfig(level=logging.INFO)

# --- إعداداتك ---
TOKEN = '8886084382:AAEcFhXXRlypOcDFl19z-lGQLqxEq67Vejc'
ADMIN_ID = 8728019066  # أيدي المطور الخاص بك
bot = telebot.TeleBot(TOKEN)

# --- نظام حفظ البيانات ---
def save_data(data):
    with open("database.txt", "a") as f:
        f.write(data + "\n")

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton('🚀 زيادة (Boost)', callback_data='submit_link')
    markup.add(btn1)
    
    # إضافة زر المطور فقط لك
    if message.chat.id == ADMIN_ID:
        btn2 = telebot.types.InlineKeyboardButton('🛠 لوحة المطور', callback_data='admin_panel')
        markup.add(btn2)
        
    bot.send_message(message.chat.id, "أهلاً بك في نظام Mocha المتطور للخدمات.", reply_markup=markup)

# --- لوحة المطور ---
@bot.callback_query_handler(func=lambda call: call.data == 'admin_panel')
def admin_panel(call):
    if call.from_user.id == ADMIN_ID:
        msg = bot.send_message(call.message.chat.id, "أرسل البيانات أو الأرقام لإضافتها لقاعدة البيانات:")
        bot.register_next_step_handler(msg, add_to_db)

def add_to_db(message):
    save_data(message.text)
    bot.reply_to(message, "✅ تم حفظ البيانات في قاعدة البيانات بنجاح.")

# --- نظام الزيادة (API) ---
@bot.callback_query_handler(func=lambda call: call.data == 'submit_link')
def ask_for_link(call):
    bot.send_message(call.message.chat.id, "أرسل الرابط الذي تريد زيادة التفاعل له (يجب أن يبدأ بـ https):")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('https://'))
def handle_boost(message):
    link = message.text
    data = {
        'action': 'add',
        'service': 5706,
        'link': link,
        'quantity': 250,
        'key': 'ecd9a18096101e397646f0a9d6dfcec9'
    }
    try:
        response = requests.post('https://foloiq.com/api/v2', data=data).json()
        if "order" in response:
            bot.reply_to(message, f"✅ تمت العملية بنجاح!\n🆔 رقم الطلب: {response['order']}")
        else:
            bot.reply_to(message, f"⚠️ فشل الطلب: {response}")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ في الاتصال بالسيرفر: {e}")

# --- التشغيل ---
print("البوت يعمل الآن..")
bot.polling(none_stop=True)

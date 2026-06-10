# ==================جعبتك========================
# 🚀 مطور البوت: ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟
# 📅 الإصدار: v70 - Sudan Secure Edition (Encrypted Sources)
# ==========================================

import time
import requests
import re
import os
import random
import json
import base64
from datetime import datetime
import sqlite3
import telebot
from telebot import types
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======================
# 📊 إعدادات البوت - ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟
# ======================
BOT_TOKEN = "8886084382:AAEcFhXXRlypOcDFl19z-lGQLqxEq67Vejc"
CHAT_IDS = ["-1003908016285 "] # آيدي القناة التي ترسل إليها الأكواد (بث مباشر)
ADMIN_IDS = [8728019066] # آيدي الأدمن المسموح له بدخول لوحة التحكم
DB_PATH = "bot_ramos_live.db" # مسار قاعدة البيانات
REFRESH_INTERVAL = 2 # سرعة تحديث الأكواد بالثواني

# ---------------------------------------------------------
# 🔒 نظام تشفير المصادر (Encrypted Sources)
# ---------------------------------------------------------
_E_SITE_URL = "aHR0cHM6Ly9pbmZpbml0eS1zbXMudmVyY2VsLmFwcA==" 
_E_NUMBERS_PATH = "L251bWJlcnM=" 
_E_GET_BTN_TEXT = "R0VUIDMgTlVNQkVSUw==" 
FREE_PHONE_URL = "https://freephonenum.com/receive-sms"

def _d(data):
    return base64.b64decode(data).decode('utf-8')

SITE_URL = _d(_E_SITE_URL)
NUMBERS_URL = SITE_URL + _d(_E_NUMBERS_PATH)
GET_BTN_TEXT = _d(_E_GET_BTN_TEXT)

# ---------------------------------------------------------
# 🌟 إعدادات الرموز التعبيرية المميزة
# ---------------------------------------------------------
EMOJI_SUDAN = "5294177148058228060"
EMOJI_ROCKET = "5861568308116984245"
EMOJI_STAR = "5971959460229289659"
EMOJI_DEFAULT = "5794032228015020065"

def get_custom_emoji(emoji_id, fallback="✨"):
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ======================
# 🗄️ إدارة قاعدة البيانات
# ======================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, join_date TEXT, is_banned INTEGER DEFAULT 0, last_msg_id INTEGER, has_image INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sent_otps (otp_key TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sent_numbers (number TEXT PRIMARY KEY, user_id INTEGER, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS my_numbers (number TEXT PRIMARY KEY, user_id INTEGER, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pending_inputs (user_id INTEGER PRIMARY KEY, action TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_setting(key, default=""):
    with get_db() as conn:
        res = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return res[0] if res else default

def set_setting(key, value):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

def get_bot_image():
    img = get_setting('bot_image')
    return img if img else None

# ======================
# 🛡️ نظام الاشتراك الإجباري (تم الإلغاء)
# ======================
def check_sub(user_id):
    return True # تم الإلغاء

def force_sub_markup():
    return None # تم الإلغاء

# ======================
# 🖼️ دالة التحديث الذكي
# ======================
def smart_edit(chat_id, user_id, text, reply_markup=None):
    with get_db() as conn:
        user = conn.execute("SELECT last_msg_id, has_image FROM users WHERE user_id=?", (user_id,)).fetchone()
    last_msg_id = user[0] if user else None
    old_has_img = bool(user[1]) if user else False
    bot_img = get_bot_image()
    new_has_img = bool(bot_img)

    try:
        if last_msg_id:
            if not old_has_img and new_has_img:
                bot.delete_message(chat_id, last_msg_id)
                sent = bot.send_photo(chat_id, bot_img, caption=text, reply_markup=reply_markup)
                update_user_msg(user_id, sent.message_id, 1)
                return
            elif old_has_img and not new_has_img:
                bot.delete_message(chat_id, last_msg_id)
                sent = bot.send_message(chat_id, text, reply_markup=reply_markup)
                update_user_msg(user_id, sent.message_id, 0)
                return
            elif new_has_img:
                bot.edit_message_caption(caption=text, chat_id=chat_id, message_id=last_msg_id, reply_markup=reply_markup)
                return
            else:
                bot.edit_message_text(text, chat_id, last_msg_id, reply_markup=reply_markup)
                return
    except: pass

    try:
        if new_has_img:
            sent = bot.send_photo(chat_id, bot_img, caption=text, reply_markup=reply_markup)
            update_user_msg(user_id, sent.message_id, 1)
        else:
            sent = bot.send_message(chat_id, text, reply_markup=reply_markup)
            update_user_msg(user_id, sent.message_id, 0)
    except: pass

def update_user_msg(uid, mid, has_img):
    with get_db() as conn:
        conn.execute("UPDATE users SET last_msg_id=?, has_image=? WHERE user_id=?", (mid, has_img, uid))

def back_btn(cb="home"):
    return types.InlineKeyboardButton("🔙 رجوع", callback_data=cb)

# ======================
# 🌐 وظيفة الجلب المباشر
# ======================
def live_fetch_new_numbers(country_name):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(NUMBERS_URL)
        wait = WebDriverWait(driver, 20)
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{country_name}')]")))
        btn.click()
        time.sleep(2)
        sub_name = f"{country_name} 1"
        sub_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{sub_name}')]")))
        sub_btn.click()
        time.sleep(2)
        get_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{GET_BTN_TEXT}')]")))
        get_btn.click()
        time.sleep(5)
        page_source = driver.page_source
        pattern = r"(\d+INFINITY\d+|84\d{8,12}|263\d{8,12}|593\d{8,12}|49\d{8,12})"
        matches = re.findall(pattern, page_source)
        return list(set(matches))
    except: return []
    finally: driver.quit()

def assign_fresh_number(user_id, country_name):
    fresh_site_numbers = live_fetch_new_numbers(country_name)
    if not fresh_site_numbers: return None
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    selected_number = None
    for num in fresh_site_numbers:
        c.execute("SELECT 1 FROM sent_numbers WHERE number = ?", (num,))
        if not c.fetchone():
            selected_number = num
            break
    if selected_number:
        c.execute("INSERT INTO sent_numbers (number, user_id, timestamp) VALUES (?, ?, ?)", (selected_number, user_id, datetime.now()))
        c.execute("DELETE FROM my_numbers WHERE user_id = ?", (user_id,))
        c.execute("INSERT INTO my_numbers (number, user_id, timestamp) VALUES (?, ?, ?)", (selected_number, user_id, datetime.now()))
        conn.commit()
    conn.close()
    return selected_number

# ======================
# 📡 سكريبت سحب الأكواد (دمج الموقعين)
# ======================
def scrape_all_otps():
    otps = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(SITE_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator='|')
        pattern = r"(?P<flag>[\U0001F1E6-\U0001F1FF]{2})\|(?P<service>[^|]+)\|(?P<country>[^|]+)\|[^|]+\|(?P<number>\d+INFINITY\d+|\d+)"
        for match in re.finditer(pattern, page_text):
            otps.append({"flag": match.group("flag"), "service": "#INFINITY", "country": match.group("country").strip(), "number": match.group("number"), "sms": "🔓 متاح"})
    except: pass
    try:
        res2 = requests.get(FREE_PHONE_URL, headers=headers, timeout=10)
        soup2 = BeautifulSoup(res2.text, 'html.parser')
        for n in soup2.select('.number-box'):
            otps.append({"flag": "🇺🇸", "service": "#USA", "country": "USA", "number": n.text.strip(), "sms": "🎁 كود جديد"})
    except: pass
    return otps

def format_otp_message(otp, is_private=False):
    masked_num = otp['number']
    emoji = get_custom_emoji(EMOJI_DEFAULT, "🔥")
    return f"{emoji} <b>بث مباشر:</b>\n\n{otp['flag']} <b>{otp['country']}</b>\n{otp['service']} <b>{masked_num}</b>\n\n<pre><code>{otp['sms']}</code></pre>\n\n<b>BY: 𝐑𝐀𝐌𝐎𝐒 (@ramosb)</b>"

# ======================
# 🤖 الأوامر ولوحة التحكم
# ======================
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)", (uid, msg.from_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    show_home(msg.chat.id, uid)

def show_home(cid, uid):
    sudan_flag = get_custom_emoji(EMOJI_SUDAN, "🇸🇩")
    text = f"{sudan_flag} مرحباً بك في بوت <b>تايتنز</b> سيد بوتات الأرقام"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🌍 طلب رقم", callback_data="quick_countries"))
    if uid in ADMIN_IDS: markup.add(types.InlineKeyboardButton(f"🛠 لوحة التحكم", callback_data="admin_panel"))
    smart_edit(cid, uid, text, markup)

def show_admin_panel(cid, uid):
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton("🖼️ تعيين صورة", callback_data="adm_setimg"), types.InlineKeyboardButton("❌ حذف صورة", callback_data="adm_delimg"))
    mk.add(types.InlineKeyboardButton("📊 الإحصائيات", callback_data="adm_stats"), types.InlineKeyboardButton("✉️ إذاعة", callback_data="adm_broadcast"))
    mk.add(back_btn())
    smart_edit(cid, uid, "🛠 <b>لوحة الأدمن</b>", mk)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    data = call.data
    if data == "home": show_home(cid, uid)
    elif data == "quick_countries":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🇻🇳 Vietnam", callback_data="gen_Vietnam_🇻🇳"), types.InlineKeyboardButton("🇿🇼 Zimbabwe", callback_data="gen_Zimbabwe_🇿🇼"))
        markup.add(back_btn())
        smart_edit(cid, uid, "🌍 اختر الدولة:", markup)
    elif data.startswith("gen_"):
        _, name, flag = data.split("_")
        next_num = assign_fresh_number(uid, name)
        res_msg = f"✅ تم جلب رقم جديد من {flag} {name}!\n\n📱 الرقم: <code>+{next_num}</code>"
        smart_edit(cid, uid, res_msg, back_btn("quick_countries"))
    elif data == "admin_panel" and uid in ADMIN_IDS: show_admin_panel(cid, uid)
    elif data == "adm_setimg": set_pending(uid, "set_image"); bot.send_message(cid, "🖼️ أرسل الصورة:")
    elif data == "adm_delimg": set_setting('bot_image', ''); show_admin_panel(cid, uid)
    elif data == "adm_stats": bot.answer_callback_query(call.id, "📊 البوت يعمل", show_alert=True)
    elif data == "adm_broadcast": set_pending(uid, "broadcast"); bot.send_message(cid, "✉️ أرسل نص الإذاعة:")
    elif data == "cancel_input": show_home(cid, uid)

def set_pending(uid, action, data=""):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO pending_inputs (user_id, action, data) VALUES (?, ?, ?)", (uid, action, data))

@bot.message_handler(content_types=['text', 'photo'])
def handle_inputs(msg):
    uid = msg.from_user.id
    cid = msg.chat.id
    with get_db() as conn:
        pending = conn.execute("SELECT action, data FROM pending_inputs WHERE user_id=?", (uid,)).fetchone()
    if not pending: return
    action, data = pending
    if action == "set_image" and msg.photo:
        set_setting('bot_image', msg.photo[-1].file_id)
        with get_db() as conn: conn.execute("DELETE FROM pending_inputs WHERE user_id=?", (uid,))
        bot.reply_to(msg, "✅ تم تعيين الصورة")
        show_home(cid, uid)
    elif action == "broadcast" and msg.text:
        with get_db() as conn:
            users = conn.execute("SELECT user_id FROM users").fetchall()
            conn.execute("DELETE FROM pending_inputs WHERE user_id=?", (uid,))
        for u in users:
            try: bot.send_message(u[0], msg.text)
            except: pass
        bot.send_message(cid, "✅ تم الإرسال")
        show_admin_panel(cid, uid)

def live_otp_stream():
    while True:
        try:
            current_otps = scrape_all_otps()
            # (منطق التوزيع هنا)
            time.sleep(REFRESH_INTERVAL)
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=live_otp_stream, daemon=True).start()
    bot.polling(none_stop=True)

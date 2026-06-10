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
#البوت ما تناخس في حاجه انتا ما عارفها شنو يا جعبه 
_E_SITE_URL = "aHR0cHM6Ly9pbmZpbml0eS1zbXMudmVyY2VsLmFwcA==" # رابط الموقع المصدر مشفر
_E_NUMBERS_PATH = "L251bWJlcnM=" #ما تناخس
_E_GET_BTN_TEXT = "R0VUIDMgTlVNQkVSUw==" # ما تناخس

def _d(data):
    """دالة لفك تشفير البيانات الحساسة داخلياً"""
    return base64.b64decode(data).decode('utf-8')

SITE_URL = _d(_E_SITE_URL)
NUMBERS_URL = SITE_URL + _d(_E_NUMBERS_PATH)
GET_BTN_TEXT = _d(_E_GET_BTN_TEXT)

# ---------------------------------------------------------
# 🌟 إعدادات الرموز التعبيرية المميزة (Custom Emoji IDs)
# ---------------------------------------------------------
EMOJI_SUDAN = "5294177148058228060"  # علم السودان الايموجي المميز
EMOJI_ROCKET = "5861568308116984245" # الصاروخ
EMOJI_STAR = "5971959460229289659"   # النجمة
EMOJI_DEFAULT = "5794032228015020065" # الرمز الافتراضي

def get_custom_emoji(emoji_id, fallback="✨"):
    """تنشئ وسم HTML للرمز التعبيري المميز"""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

# ---------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ======================
# 🗄️ إدارة قاعدة البيانات
# ======================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        join_date TEXT,
        is_banned INTEGER DEFAULT 0,
        last_msg_id INTEGER,
        has_image INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sent_otps (otp_key TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sent_numbers (number TEXT PRIMARY KEY, user_id INTEGER, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS my_numbers (number TEXT PRIMARY KEY, user_id INTEGER, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pending_inputs (
        user_id INTEGER PRIMARY KEY,
        action TEXT,
        data TEXT
    )''')
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
# 🛡️ نظام الاشتراك الإجباري (تم الإلغاء تماماً)
# ======================
def check_sub(user_id):
    return True # تم تصفير الفحص

def force_sub_markup():
    return None # تم إغلاق أي أزرار اشتراك

# ======================
# 🖼️ دالة التحديث الذكي (Smart Edit)
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
# 🌐 وظيفة الجلب المباشر (Live Fetch)
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
# 📡 سكريبت سحب الأكواد الشامل (Full Stream Script)
# ======================
def scrape_all_otps():
    """سكريبت لجلب كافة الأكواد المتاحة في البث المباشر (الجديد والقديم) وبنك الأرقام"""
    otps = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. جلب كافة سجلات البث المباشر (Full Live Stream History)
    try:
        response = requests.get(SITE_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # سحب النص بالكامل مع فواصل واضحة
        page_text = soup.get_text(separator='|')
        
        # نستخدم Regex مطور للبحث عن السجلات من الأعلى للأسفل
        # يبحث عن: (علم | خدمة | دولة | رقم)
        pattern = r"(?P<flag>[\U0001F1E6-\U0001F1FF]{2})\|(?P<service>[^|]+)\|(?P<country>[^|]+)\|[^|]+\|(?P<number>\d+INFINITY\d+|\d+)"
        matches = list(re.finditer(pattern, page_text))
        
        # نأخذ جميع النتائج (الجديدة في الأعلى والقديمة في الأسفل)
        for match in matches:
            service_raw = match.group("service").strip()
            service_tag = "#" + re.sub(r'\W+', '', service_raw).upper()[:10]
            
            otps.append({
                "flag": match.group("flag"),
                "service": service_tag,
                "country": match.group("country").strip(),
                "number": match.group("number"),
                "sms": "🔓 كود متاح في سجل البث المباشر بالموقع!" 
            })
    except: pass

    # 2. جلب كافة سجلات بنك الأرقام (Bank Numbers History)
    try:
        response_bank = requests.get(NUMBERS_URL, headers=headers, timeout=10)
        soup_bank = BeautifulSoup(response_bank.text, 'html.parser')
        bank_text = soup_bank.get_text(separator='|')
        
        # سحب كافة الأرقام والأكواد المتوفرة في بنك الأرقام
        bank_pattern = r"(?P<number>\d+INFINITY\d+|\d+)\|(?P<sms>\d{4,8})"
        bank_matches = list(re.finditer(bank_pattern, bank_text))
        
        for match in bank_matches:
            otps.append({
                "flag": "🏦",
                "service": "#BANK",
                "country": "Bank Number",
                "number": match.group("number"),
                "sms": f"🎁 كود بنك الأرقام: {match.group('sms')}"
            })
    except: pass
    
    return otps

def mask_number(number):
    number = str(number).strip()
    if "INFINITY" in number: return number.replace("INFINITY", "•••")
    if len(number) > 8: return number[:7] + "••" + number[-4:]
    return number

def format_otp_message(otp, is_private=False):
    masked_num = mask_number(otp['number'])
    emoji = get_custom_emoji(EMOJI_DEFAULT, "🔥")
    prefix = f"{emoji} <b>كود خاص برقمك (بنك الأرقام):</b>\n\n" if is_private else f"{emoji} <b>بث مباشر (كود جديد):</b>\n\n"
    return f"{prefix}{otp['flag']} <b><u>{otp['country']}</u></b> {otp['service']} <b><u>{masked_num}</u></b>\n\n<pre><code>{otp['sms']}</code></pre>\n\n<b>BY: 𝐑𝐀𝐌𝐎𝐒 (@ramosb)</b>"

# ======================
# 🤖 أوامر البوت ولوحة التحكم
# ======================
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)", 
                     (uid, msg.from_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    show_home(msg.chat.id, uid)

def show_home(cid, uid):
    sudan_flag = get_custom_emoji(EMOJI_SUDAN, "🇸🇩")
    rocket = get_custom_emoji(EMOJI_ROCKET, "🚀")
    star = get_custom_emoji(EMOJI_STAR, "✨")
    
    text = (
        f"{sudan_flag} مرحباً بك في بوت <b>تايتنز</b> سيد بوتات الأرقام\n\n"
        f"{rocket} أول بوت سوداني مجاني، صنع سوداني متكامل.\n"
        f"{star} ميزاتنا: سرعة، أمان، ودعم كامل لجميع التطبيقات.\n\n"
        f"استخدم الأزرار أدناه للتحكم في البوت ما تخليك دنقلاوي."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🌍 طلب رقم حقيقي (Live)", callback_data="quick_countries"))
    if uid in ADMIN_IDS:
        markup.add(types.InlineKeyboardButton(f"🛠 لوحة التحكم", callback_data="admin_panel"))
    smart_edit(cid, uid, text, markup)

def show_admin_panel(cid, uid):
    emoji = get_custom_emoji(EMOJI_DEFAULT, "🛠")
    text = f"{emoji} <b>لوحة الأدمن - TITANS</b>"
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton("🖼️ تعيين صورة", callback_data="adm_setimg"),
           types.InlineKeyboardButton("❌ حذف صورة", callback_data="adm_delimg"))
    mk.add(types.InlineKeyboardButton("📊 الإحصائيات", callback_data="adm_stats"),
           types.InlineKeyboardButton("✉️ إذاعة", callback_data="adm_broadcast"))
    mk.add(back_btn())
    smart_edit(cid, uid, text, mk)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    data = call.data
    # تم إلغاء كل ما يخص القناة من هنا
    if data == "home": show_home(cid, uid)
    elif data == "quick_countries":
        countries = [
            {"name": "Vietnam", "flag": "🇻🇳", "code": "84"},
            {"name": "Zimbabwe", "flag": "🇿🇼", "code": "263"},
            {"name": "Ecuador", "flag": "🇪🇨", "code": "593"},
            {"name": "Germany", "flag": "🇩🇪", "code": "49"}
        ]
        markup = types.InlineKeyboardMarkup(row_width=2)
        for c in countries:
            markup.add(types.InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"gen_{c['name']}_{c['flag']}"))
        markup.add(back_btn())
        emoji = get_custom_emoji(EMOJI_DEFAULT, "🌍")
        smart_edit(cid, uid, f"{emoji} اختر الدولة:", markup)
    elif data.startswith("gen_"):
        _, name, flag = data.split("_")
        bot.answer_callback_query(call.id, f"⏳ جاري جلب رقم لـ {name}...")
        next_num = assign_fresh_number(uid, name)
        if not next_num:
            emoji_err = get_custom_emoji(EMOJI_DEFAULT, "❌")
            bot.send_message(cid, f"{emoji_err} عذراً، فشل جلب رقم لـ {name} حالياً.")
            return
        emoji_ok = get_custom_emoji(EMOJI_DEFAULT, "✅")
        res_msg = f"{emoji_ok} تم جلب رقم جديد من {flag} {name}!\n\n📱 الرقم: <code>+{next_num}</code>\n\n⏳ البوت يراقب الأكواد الآن..."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 جلب رقم آخر", callback_data=f"gen_{name}_{flag}"))
        markup.add(back_btn("quick_countries"))
        smart_edit(cid, uid, res_msg, markup)
    elif data == "admin_panel" and uid in ADMIN_IDS: show_admin_panel(cid, uid)
    elif data == "adm_setimg":
        emoji = get_custom_emoji(EMOJI_DEFAULT, "🖼️")
        smart_edit(cid, uid, f"{emoji} أرسل الصورة:", types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_input")))
        set_pending(uid, "set_image")
    elif data == "adm_delimg":
        set_setting('bot_image', '')
        with get_db() as conn: conn.execute("UPDATE users SET has_image=0 WHERE user_id=?", (uid,))
        bot.answer_callback_query(call.id, f"✅ تم الحذف")
        show_admin_panel(cid, uid)
    elif data == "adm_stats":
        with get_db() as conn:
            u = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            s = conn.execute("SELECT COUNT(*) FROM sent_numbers").fetchone()[0]
        bot.answer_callback_query(call.id, f"👤 المستخدمين: {u}\n📱 الأرقام: {s}", show_alert=True)
    elif data == "adm_broadcast":
        emoji = get_custom_emoji(EMOJI_DEFAULT, "✉️")
        smart_edit(cid, uid, f"{emoji} أرسل نص الإذاعة:", types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_input")))
        set_pending(uid, "broadcast")
    elif data == "cancel_input":
        with get_db() as conn: conn.execute("DELETE FROM pending_inputs WHERE user_id=?", (uid,))
        show_home(cid, uid)

def set_pending(uid, action, data=""):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO pending_inputs (user_id, action, data) VALUES (?, ?, ?)", (uid, action, data))

@bot.message_handler(content_types=['text', 'photo'])
def handle_inputs(msg):
    uid = msg.from_user.id
    cid = msg.chat.id
    with get_db() as conn:
        pending = conn.execute("SELECT action, data FROM pending_inputs WHERE user_id=?", (uid,)).fetchone()
    if not pending: return
    action, data = pending
    if action == "set_image" and msg.photo:
        fid = msg.photo[-1].file_id
        set_setting('bot_image', fid)
        with get_db() as conn: 
            conn.execute("UPDATE users SET has_image=1 WHERE user_id=?", (uid,))
            conn.execute("DELETE FROM pending_inputs WHERE user_id=?", (uid,))
        emoji = get_custom_emoji(EMOJI_DEFAULT, "✅")
        bot.reply_to(msg, f"{emoji} تم تعيين الصورة")
        show_home(cid, uid)
    elif action == "broadcast" and msg.text:
        with get_db() as conn:
            users = conn.execute("SELECT user_id FROM users").fetchall()
            conn.execute("DELETE FROM pending_inputs WHERE user_id=?", (uid,))
        emoji_wait = get_custom_emoji(EMOJI_DEFAULT, "⏳")
        bot.reply_to(msg, f"{emoji_wait} جاري الإذاعة...")
        count = 0
        emoji_msg = get_custom_emoji(EMOJI_DEFAULT, "📢")
        broadcast_text = f"{emoji_msg} {msg.text}"
        for u in users:
            try: bot.send_message(u[0], broadcast_text); count += 1
            except: pass
        emoji_done = get_custom_emoji(EMOJI_DEFAULT, "✅")
        bot.send_message(cid, f"{emoji_done} تم إرسال الإذاعة لـ {count} مستخدم.")
        show_admin_panel(cid, uid)

# ======================
# 🔄 حلقة المراقبة الشاملة (Background Full Monitor)
# ======================
def live_otp_stream():
    """سكريبت يعمل في الخلفية لسحب كافة الأكواد (الجديدة والقديمة) وتوزيعها"""
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT number, user_id FROM my_numbers")
            watched_data = {row[0]: row[1] for row in c.fetchall()}
            conn.close()
            
            current_otps = scrape_all_otps()
            
            for otp in current_otps:
                otp_key = f"{otp['number']}_{otp['service']}_{otp['sms']}"
                
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT 1 FROM sent_otps WHERE otp_key = ?", (otp_key,))
                
                if not c.fetchone():
                    msg_group = format_otp_message(otp, is_private=False)
                    for chat_id in CHAT_IDS:
                        try: bot.send_message(chat_id, msg_group)
                        except: pass
                    
                    clean_site_num = otp['number'].replace("INFINITY", "")
                    for watched_num, user_id in watched_data.items():
                        clean_watched = watched_num.replace("INFINITY", "")
                        if clean_site_num == clean_watched or (len(clean_site_num) > 5 and clean_site_num in clean_watched):
                            try: bot.send_message(user_id, format_otp_message(otp, is_private=True))
                            except: pass
                    
                    c.execute("INSERT INTO sent_otps VALUES (?)", (otp_key,))
                    conn.commit()
                conn.close()
            
            time.sleep(REFRESH_INTERVAL)
        except: time.sleep(5)

# ======================
# 🏁 تشغيل البوت
# ======================
if __name__ == "__main__":
    threading.Thread(target=live_otp_stream, daemon=True).start()
    print("Bot v30 (Sudan Secure Edition) is running with Encrypted Sources...")
    bot.polling(none_stop=True)

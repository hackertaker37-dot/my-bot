import time
import requests
import json
import re
import os
from datetime import datetime, date, timedelta
from urllib.parse import quote_plus
from pathlib import Path
import sqlite3
import telebot
from telebot import types
import threading
import traceback
import random
import itertools
import logging
import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃               𝐈𝐕𝐀 𝐒𝐌𝐒 𝐂𝐎𝐑𝐄                ┃
# ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
# ┃ 📡 SMS Source Configuration                 ┃
# ┃ 🔑 API & Service Provider Settings          ┃
# ┃ ⚙️ Number Allocation & Message Handling     ┃
# ┃                                              ┃
# ┃ 👨‍💻 Developed By : @hackerTaker7            ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

IVASMS_DASHBOARD = {
    "name": "iVasms",
    "type": "ivasms",
    "login_url": "https://ivas.tempnum.qzz.io/login",
    "base_url": "https://ivas.tempnum.qzz.io",
    "sms_api_endpoint": "https://ivas.tempnum.qzz.io/portal/sms/received/getsms",
    "username": "bwt756183@gmail.com",
    "password": "011399@ZZzz",
    "session": requests.Session(),
    "is_logged_in": False,
    "cookies": None,
    "csrf_token": None,
    "last_check": None
}

# ======================
# 🔧 إعدادات عامة
# ======================
USERNAME = "bwt756183@gmail.com"
PASSWORD = "011399@ZZzz"
BOT_TOKEN = "8886084382:AAFqOJtnMenWNR4ummLPpN5mQlCizidavuU"
CHAT_IDS = [
    "-1003908016285",
]
REFRESH_INTERVAL = 3
TIMEOUT = 100
MAX_RETRIES = 5
RETRY_DELAY = 5

IDX_DATE = 0
IDX_NUMBER = 2
IDX_SMS = 5
SENT_MESSAGES_FILE = "sent_messages.json"

ADMIN_IDS = [8728019066]
DB_PATH = "bot.db"
FORCE_SUB_CHANNEL = None
FORCE_SUB_ENABLED = False
BOT_ACTIVE = True

# ✨🌟🌟🌟 إضافة إعدادات الألوان للأزرار 🌟🌟🌟✨
# ======================
# 🎨 إعدادات الألوان للأزرار (مضافة)
# ======================
BUTTON_COLORS = {
    "primary": "🔵",    # أزرق للاختيارات الرئيسية
    "success": "🟢",    # أخضر للتأكيد والنجاح
    "danger": "🔴",     # أحمر للحذف والخطر
    "warning": "🟡",    # أصفر للتحذير
    "info": "🔷",       # أزرق فاتح للمعلومات
    "admin": "🔐",      # للأدمن
    "back": "🔙",       # للرجوع
    "refresh": "🔄",    # للتحديث
    "number": "📱",     # للأرقام
    "country": "🌍",    # للدول
    "otp": "📨",        # للرسائل
}

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN must be set in Secrets (Environment Variables)")
if not CHAT_IDS:
    raise SystemExit("❌ CHAT_IDS must be configured")
if not USERNAME or not PASSWORD:
    print("⚠️  WARNING: SITE_USERNAME and SITE_PASSWORD not set in Secrets")
    print("⚠️  Bot will continue but login may fail")

# ======================
# 🌍 رموز الدول
# ======================
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸", "US"),
    "7": ("Russia", "🇷🇺", "RU"),
    "20": ("Egypt", "🇪🇬", "EG"),
    "27": ("South Africa", "🇿🇦", "ZA"),
    "30": ("Greece", "🇬🇷", "GR"),
    "31": ("Netherlands", "🇳🇱", "NL"),
    "32": ("Belgium", "🇧🇪", "BE"),
    "33": ("France", "🇫🇷", "FR"),
    "34": ("Spain", "🇪🇸", "ES"),
    "36": ("Hungary", "🇭🇺", "HU"),
    "39": ("Italy", "🇮🇹", "IT"),
    "40": ("Romania", "🇷🇴", "RO"),
    "41": ("Switzerland", "🇨🇭", "CH"),
    "42": ("????", "❓", "??"),
    "43": ("Austria", "🇦🇹", "AT"),
    "44": ("United Kingdom", "🇬🇧", "UK"),
    "45": ("Denmark", "🇩🇰", "DK"),
    "46": ("Sweden", "🇸🇪", "SE"),
    "47": ("Norway", "🇳🇴", "NO"),
    "48": ("Poland", "🇵🇱", "PL"),
    "49": ("Germany", "🇩🇪", "DE"),
    "51": ("Peru", "🇵🇪", "PE"),
    "52": ("Mexico", "🇲🇽", "MX"),
    "53": ("Cuba", "🇨🇺", "CU"),
    "54": ("Argentina", "🇦🇷", "AR"),
    "55": ("Brazil", "🇧🇷", "BR"),
    "56": ("Chile", "🇨🇱", "CL"),
    "57": ("Colombia", "🇨🇴", "CO"),
    "58": ("Venezuela", "🇻🇪", "VE"),
    "60": ("Malaysia", "🇲🇾", "MY"),
    "61": ("Australia", "🇦🇺", "AU"),
    "62": ("Indonesia", "🇮🇩", "ID"),
    "63": ("Philippines", "🇵🇭", "PH"),
    "64": ("New Zealand", "🇳🇿", "NZ"),
    "65": ("Singapore", "🇸🇬", "SG"),
    "66": ("Thailand", "🇹🇭", "TH"),
    "81": ("Japan", "🇯🇵", "JP"),
    "82": ("South Korea", "🇰🇷", "KR"),
    "84": ("Vietnam", "🇻🇳", "VN"),
    "86": ("China", "🇨🇳", "CN"),
    "90": ("Turkey", "🇹🇷", "TR"),
    "91": ("India", "🇮🇳", "IN"),
    "92": ("Pakistan", "🇵🇰", "PK"),
    "93": ("Afghanistan", "🇦🇫", "AF"),
    "94": ("Sri Lanka", "🇱🇰", "LK"),
    "95": ("Myanmar", "🇲🇲", "MM"),
    "98": ("Iran", "🇮🇷", "IR"),
    "211": ("South Sudan", "🇸🇸", "SS"),
    "212": ("Morocco", "🇲🇦", "MA"),
    "213": ("Algeria", "🇩🇿", "DZ"),
    "216": ("Tunisia", "🇹🇳", "TN"),
    "218": ("Libya", "🇱🇾", "LY"),
    "220": ("Gambia", "🇬🇲", "GM"),
    "221": ("Senegal", "🇸🇳", "SN"),
    "222": ("Mauritania", "🇲🇷", "MR"),
    "223": ("Mali", "🇲🇱", "ML"),
    "224": ("Guinea", "🇬🇳", "GN"),
    "225": ("Ivory Coast", "🇨🇮", "CI"),
    "226": ("Burkina Faso", "🇧🇫", "BF"),
    "227": ("Niger", "🇳🇪", "NE"),
    "228": ("Togo", "🇹🇬", "TG"),
    "229": ("Benin", "🇧🇯", "BJ"),
    "230": ("Mauritius", "🇲🇺", "MU"),
    "231": ("Liberia", "🇱🇷", "LR"),
    "232": ("Sierra Leone", "🇸🇱", "SL"),
    "233": ("Ghana", "🇬🇭", "GH"),
    "234": ("Nigeria", "🇳🇬", "NG"),
    "235": ("Chad", "🇹🇩", "TD"),
    "236": ("Central African Rep", "🇨🇫", "CF"),
    "237": ("Cameroon", "🇨🇲", "CM"),
    "238": ("Cape Verde", "🇨🇻", "CV"),
    "239": ("Sao Tome", "🇸🇹", "ST"),
    "240": ("Equatorial Guinea", "🇬🇶", "GQ"),
    "241": ("Gabon", "🇬🇦", "GA"),
    "242": ("Congo", "🇨🇬", "CG"),
    "243": ("DR Congo", "🇨🇩", "CD"),
    "244": ("Angola", "🇦🇴", "AO"),
    "245": ("Guinea-Bissau", "🇬🇼", "GW"),
    "248": ("Seychelles", "🇸🇨", "SC"),
    "249": ("Sudan", "🇸🇩", "SD"),
    "250": ("Rwanda", "🇷🇼", "RW"),
    "251": ("Ethiopia", "🇪🇹", "ET"),
    "252": ("Somalia", "🇸🇴", "SO"),
    "253": ("Djibouti", "🇩🇯", "DJ"),
    "254": ("Kenya", "🇰🇪", "KE"),
    "255": ("Tanzania", "🇹🇿", "TZ"),
    "256": ("Uganda", "🇺🇬", "UG"),
    "257": ("Burundi", "🇧🇮", "BI"),
    "258": ("Mozambique", "🇲🇿", "MZ"),
    "260": ("Zambia", "🇿🇲", "ZM"),
    "261": ("Madagascar", "🇲🇬", "MG"),
    "262": ("Reunion", "🇷🇪", "RE"),
    "263": ("Zimbabwe", "🇿🇼", "ZW"),
    "264": ("Namibia", "🇳🇦", "NA"),
    "265": ("Malawi", "🇲🇼", "MW"),
    "266": ("Lesotho", "🇱🇸", "LS"),
    "267": ("Botswana", "🇧🇼", "BW"),
    "268": ("Eswatini", "🇸🇿", "SZ"),
    "269": ("Comoros", "🇰🇲", "KM"),
    "350": ("Gibraltar", "🇬🇮", "GI"),
    "351": ("Portugal", "🇵🇹", "PT"),
    "352": ("Luxembourg", "🇱🇺", "LU"),
    "353": ("Ireland", "🇮🇪", "IE"),
    "354": ("Iceland", "🇮🇸", "IS"),
    "355": ("Albania", "🇦🇱", "AL"),
    "356": ("Malta", "🇲🇹", "MT"),
    "357": ("Cyprus", "🇨🇾", "CY"),
    "358": ("Finland", "🇫🇮", "FI"),
    "359": ("Bulgaria", "🇧🇬", "BG"),
    "370": ("Lithuania", "🇱🇹", "LT"),
    "371": ("Latvia", "🇱🇻", "LV"),
    "372": ("Estonia", "🇪🇪", "EE"),
    "373": ("Moldova", "🇲🇩", "MD"),
    "374": ("Armenia", "🇦🇲", "AM"),
    "375": ("Belarus", "🇧🇾", "BY"),
    "376": ("Andorra", "🇦🇩", "AD"),
    "377": ("Monaco", "🇲🇨", "MC"),
    "378": ("San Marino", "🇸🇲", "SM"),
    "380": ("Ukraine", "🇺🇦", "UA"),
    "381": ("Serbia", "🇷🇸", "RS"),
    "382": ("Montenegro", "🇲🇪", "ME"),
    "383": ("Kosovo", "🇽🇰", "XK"),
    "385": ("Croatia", "🇭🇷", "HR"),
    "386": ("Slovenia", "🇸🇮", "SI"),
    "387": ("Bosnia", "🇧🇦", "BA"),
    "389": ("North Macedonia", "🇲🇰", "MK"),
    "420": ("Czech Republic", "🇨🇿", "CZ"),
    "421": ("Slovakia", "🇸🇰", "SK"),
    "423": ("Liechtenstein", "🇱🇮", "LI"),
    "500": ("Falkland Islands", "🇫🇰", "FK"),
    "501": ("Belize", "🇧🇿", "BZ"),
    "502": ("Guatemala", "🇬🇹", "GT"),
    "503": ("El Salvador", "🇸🇻", "SV"),
    "504": ("Honduras", "🇭🇳", "HN"),
    "505": ("Nicaragua", "🇳🇮", "NI"),
    "506": ("Costa Rica", "🇨🇷", "CR"),
    "507": ("Panama", "🇵🇦", "PA"),
    "509": ("Haiti", "🇭🇹", "HT"),
    "591": ("Bolivia", "🇧🇴", "BO"),
    "592": ("Guyana", "🇬🇾", "GY"),
    "593": ("Ecuador", "🇪🇨", "EC"),
    "595": ("Paraguay", "🇵🇾", "PY"),
    "597": ("Suriname", "🇸🇷", "SR"),
    "598": ("Uruguay", "🇺🇾", "UY"),
    "670": ("Timor-Leste", "🇹🇱", "TL"),
    "673": ("Brunei", "🇧🇳", "BN"),
    "674": ("Nauru", "🇳🇷", "NR"),
    "675": ("Papua New Guinea", "🇵🇬", "PG"),
    "676": ("Tonga", "🇹🇴", "TO"),
    "677": ("Solomon Islands", "🇸🇧", "SB"),
    "678": ("Vanuatu", "🇻🇺", "VU"),
    "679": ("Fiji", "🇫🇯", "FJ"),
    "680": ("Palau", "🇵🇼", "PW"),
    "685": ("Samoa", "🇼🇸", "WS"),
    "686": ("Kiribati", "🇰🇮", "KI"),
    "687": ("New Caledonia", "🇳🇨", "NC"),
    "688": ("Tuvalu", "🇹🇻", "TV"),
    "689": ("French Polynesia", "🇵🇫", "PF"),
    "691": ("Micronesia", "🇫🇲", "FM"),
    "692": ("Marshall Islands", "🇲🇭", "MH"),
    "850": ("North Korea", "🇰🇵", "KP"),
    "852": ("Hong Kong", "🇭🇰", "HK"),
    "853": ("Macau", "🇲🇴", "MO"),
    "855": ("Cambodia", "🇰🇭", "KH"),
    "856": ("Laos", "🇱🇦", "LA"),
    "960": ("Maldives", "🇲🇻", "MV"),
    "961": ("Lebanon", "🇱🇧", "LB"),
    "962": ("Jordan", "🇯🇴", "JO"),
    "963": ("Syria", "🇸🇾", "SY"),
    "964": ("Iraq", "🇮🇶", "IQ"),
    "965": ("Kuwait", "🇰🇼", "KW"),
    "966": ("Saudi Arabia", "🇸🇦", "SA"),
    "967": ("Yemen", "🇾🇪", "YE"),
    "968": ("Oman", "🇴🇲", "OM"),
    "970": ("Palestine", "🇵🇸", "PS"),
    "971": ("UAE", "🇦🇪", "AE"),
    "972": ("Israel", "🇮🇱", "IL"),
    "973": ("Bahrain", "🇧🇭", "BH"),
    "974": ("Qatar", "🇶🇦", "QA"),
    "975": ("Bhutan", "🇧🇹", "BT"),
    "976": ("Mongolia", "🇲🇳", "MN"),
    "977": ("Nepal", "🇳🇵", "NP"),
    "992": ("Tajikistan", "🇹🇯", "TJ"),
    "993": ("Turkmenistan", "🇹🇲", "TM"),
    "994": ("Azerbaijan", "🇦🇿", "AZ"),
    "995": ("Georgia", "🇬🇪", "GE"),
    "996": ("Kyrgyzstan", "🇰🇬", "KG"),
    "998": ("Uzbekistan", "🇺🇿", "UZ"),
}

# ======================
# 🧰 دوال إدارة قاعدة البيانات
# ======================
def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# ======================
# 🧠 إنشاء قاعدة البيانات
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
            country_code TEXT,
            assigned_number TEXT,
            is_banned INTEGER DEFAULT 0,
            private_combo_country TEXT DEFAULT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS combos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            combo_index INTEGER DEFAULT 1,
            numbers TEXT,
            UNIQUE(country_code, combo_index)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            otp TEXT,
            full_message TEXT,
            timestamp TEXT,
            assigned_to INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_url TEXT,
            ajax_path TEXT,
            login_page TEXT,
            login_post TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS private_combos (
            user_id INTEGER,
            country_code TEXT,
            numbers TEXT,
            PRIMARY KEY (user_id, country_code)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS force_sub_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_url TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1
        )
    ''')

    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_channel', '')")
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('force_sub_enabled', '0')")
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES ('welcome_photo', '')")

    c.execute("SELECT value FROM bot_settings WHERE key = 'force_sub_channel'")
    old_channel = c.fetchone()
    if old_channel and old_channel[0].strip():
        channel = old_channel[0].strip()
        c.execute("SELECT 1 FROM force_sub_channels WHERE channel_url = ?", (channel,))
        if not c.fetchone():
            enabled = 1 if get_setting("force_sub_enabled") == "1" else 0
            c.execute("INSERT INTO force_sub_channels (channel_url, description, enabled) VALUES (?, ?, ?)",
                      (channel, "القناة الأساسية", enabled))

    conn.commit()
    conn.close()

init_db()

# ======================
# 🧰 دوال إدارة المستخدمين
# ======================

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user(user_id, username="", first_name="", last_name="", country_code=None, assigned_number=None, private_combo_country=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    existing_data = get_user(user_id)
    if existing_data:
        if country_code is None:
            country_code = existing_data[4]
        if assigned_number is None:
            assigned_number = existing_data[5]
        if private_combo_country is None:
            private_combo_country = existing_data[7]

    c.execute("""
        REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_number, is_banned, private_combo_country)
        VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0), ?)
    """, (
        user_id,
        username,
        first_name,
        last_name,
        country_code,
        assigned_number,
        user_id,
        private_combo_country
    ))
    conn.commit()
    conn.close()

def ban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[6] == 1
    
def is_maintenance_mode():
    return not BOT_ACTIVE

def set_maintenance_mode(status):
    global BOT_ACTIVE
    BOT_ACTIVE = not status
    
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users
    
def get_combo(country_code, combo_index=1, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("SELECT numbers FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        row = c.fetchone()
        if row:
            conn.close()
            return json.loads(row[0])
    c.execute("SELECT numbers FROM combos WHERE country_code=? AND combo_index=?", (country_code, combo_index))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def save_combo(country_code, numbers, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if user_id:
        c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?, ?, ?)",
                  (user_id, country_code, json.dumps(numbers)))
    else:
        c.execute("SELECT MAX(combo_index) FROM combos WHERE country_code=?", (country_code,))
        max_index = c.fetchone()[0]
        next_index = 1 if max_index is None else max_index + 1
        
        c.execute("INSERT INTO combos (country_code, combo_index, numbers) VALUES (?, ?, ?)",
                  (country_code, next_index, json.dumps(numbers)))
    
    conn.commit()
    conn.close()

def delete_combo(country_code, combo_index=None, user_id=None):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
        c = conn.cursor()
        
        if user_id:
            c.execute("DELETE FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        elif combo_index:
            c.execute("DELETE FROM combos WHERE country_code=? AND combo_index=?", (country_code, combo_index))
        else:
            c.execute("DELETE FROM combos WHERE country_code=?", (country_code,))
        
        conn.commit()
        print(f"✅ تم حذف كومبو: {country_code} (index: {combo_index})")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ خطأ SQLite في delete_combo: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_all_combos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT country_code, combo_index FROM combos ORDER BY country_code, combo_index")
    combos = c.fetchall()
    conn.close()
    return combos

def assign_number_to_user(user_id, number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
    conn.commit()
    conn.close()

def get_user_by_number(number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def log_otp(number, otp, full_message, assigned_to=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?, ?, ?, ?, ?)",
              (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
    conn.commit()
    conn.close()

def release_number(old_number):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

# --- دوال إدارة قنوات الاشتراك الإجباري ---
def get_all_force_sub_channels(enabled_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if enabled_only:
        c.execute("SELECT id, channel_url, description FROM force_sub_channels WHERE enabled = 1 ORDER BY id")
    else:
        c.execute("SELECT id, channel_url, description FROM force_sub_channels ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def add_force_sub_channel(channel_url, description=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO force_sub_channels (channel_url, description, enabled) VALUES (?, ?, 1)",
                  (channel_url.strip(), description.strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_force_sub_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM force_sub_channels WHERE id = ?", (channel_id,))
    changed = c.rowcount > 0
    conn.commit()
    conn.close()
    return changed

def toggle_force_sub_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE force_sub_channels SET enabled = 1 - enabled WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()

# ======================
# 🔐 دوال الاشتراك الإجباري
# ======================
def force_sub_check(user_id):
    channels = get_all_force_sub_channels(enabled_only=True)
    if not channels:
        return True

    for _, url, _ in channels:
        try:
            if url.startswith("https://t.me/"):
                ch = "@" + url.split("/")[-1]
            elif url.startswith("@"):
                ch = url
            else:
                continue
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print(f"[!] خطأ في التحقق من القناة {url}: {e}")
            return False
    return True

def force_sub_markup():
    channels = get_all_force_sub_channels(enabled_only=True)
    if not channels:
        return None

    markup = types.InlineKeyboardMarkup()
    for _, url, desc in channels:
        text = f"📢 {desc}" if desc else "📢 اشترك في القناة"
        markup.add(types.InlineKeyboardButton(text, url=url))
    markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
    return markup

# ======================
# 🤖 إنشاء بوت Telegram
# ======================
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# 🎮 وظائف البوت التفاعلي
# ======================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def safe_html(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

# ✨🌟🌟🌟 دالة جديدة للرد على جميع المستخدمين 🌟🌟🌟✨
# ======================
# 📩 الرد على جميع الرسائل (مضافة)
# ======================
@bot.message_handler(func=lambda message: True)
def reply_to_all_users(message):
    """
    ✅ ترد على جميع المستخدمين برسالة ترحيبية احترافية وأزرار ملونة.
    تضمن أن البوت ما يرد بس على الأدمن بل على الكل.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # تسجيل المستخدم إذا كان جديداً
    if not get_user(user_id):
        save_user(
            user_id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
            last_name=message.from_user.last_name or ""
        )
        # إشعار الأدمن بمستخدم جديد
        for admin in ADMIN_IDS:
            try:
                bot.send_message(
                    admin,
                    f"🆕 <b>مستخدم جديد:</b>\n"
                    f"🆔 <code>{user_id}</code>\n"
                    f"👤 {safe_html(message.from_user.first_name or '')}",
                    parse_mode="HTML"
                )
            except:
                pass
    
    # رسالة ترحيبية احترافية للجميع
    welcome_text = (
        f"<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
        f"<b>│    {BUTTON_COLORS['primary']} 𝐇𝐀𝐂𝐊𝐄𝐑 𝐓𝐀𝐊𝐄𝐑 𝐁𝐎𝐓 {BUTTON_COLORS['primary']}    │</b>\n"
        f"<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"
        f"<b>{BUTTON_COLORS['success']} ▸ أهلاً بك يا {safe_html(message.from_user.first_name or 'مستخدم')}</b>\n"
        f"<b>▸ استخدم /start للدخول للوحة التحكم</b>\n"
        f"<b>▸ للحصول على رقم جديد استخدم الأزرار</b>\n\n"
        f"<b>{BUTTON_COLORS['info']} ♻️ البوت يعمل 24/7</b>\n"
        f"<b>{BUTTON_COLORS['warning']} ⚡ سرعة فائقة في استقبال الرسائل</b>"
    )
    
    # أزرار ملونة للتفاعل السريع
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['success']} ابدأ", callback_data="back_to_countries"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['info']} قناة البوت", url="https://t.me/shhsnbdb")
    )
    markup.add(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['warning']} مساعدة", callback_data="help_info"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['primary']} المطور", url="https://t.me/hackerTaker7")
    )
    
    bot.reply_to(message, welcome_text, parse_mode="HTML", reply_markup=markup)

# ✨🌟🌟🌟 إضافة Callback للمساعدة 🌟🌟🌟✨
@bot.callback_query_handler(func=lambda call: call.data == "help_info")
def help_info_callback(call):
    """زر المساعدة السريعة"""
    help_text = (
        f"<b>{BUTTON_COLORS['info']} 📖 دليل الاستخدام:</b>\n\n"
        f"<b>1.</b> اضغط /start للدخول للوحة الرئيسية\n"
        f"<b>2.</b> اختر الدولة من الأزرار\n"
        f"<b>3.</b> استلم الرقم وانتظر الرسالة\n"
        f"<b>4.</b> سيصلك الكود تلقائياً\n\n"
        f"<b>{BUTTON_COLORS['warning']} للمشاكل تواصل مع:</b> @hackerTaker7"
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # 1. فحص وضع الصيانة
    if is_maintenance_mode() and not is_admin(user_id):
        maintenance_caption = (
            "<b>❍─── <u>𝐖𝐄𝐋𝐂𝐎𝐌 𝐓𝐎 ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟 𝐁𝐎𝐓 </u> ───❍</b>\n\n"
            "<b>⚠️ عذراً عزيزي المستخدم..</b>\n"
            "<b>البوت الآن في وضع الصيانة لتحديث الخدمات.</b>\n\n"
            "<b>⏳ يرجى المحاولة مرة أخرى لاحقاً.</b>\n"
            "<b>────────────────────</b>"
        )
        maintenance_photo = "https://i.ibb.co/2352v1FN/file-000000004f20720aaa70039fcd26faab-1.png"
        
        try:
            bot.send_photo(
                chat_id,
                maintenance_photo,
                caption=maintenance_caption,
                parse_mode="HTML"
            )
        except:
            bot.send_message(chat_id, maintenance_caption, parse_mode="HTML")
        return

    # 2. فحص الحظر
    if is_banned(user_id):
        bot.reply_to(message, "<b>🚫 عذراً، لقد تم حظرك من استخدام البوت.</b>", parse_mode="HTML")
        return

    # 3. فحص الاشتراك الإجباري
    if not force_sub_check(user_id):
        markup = force_sub_markup()
        if markup:
            bot.send_message(chat_id, "<b>🔒 يجب الاشتراك في القنوات لاستخدام البوت.</b>", parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, "<b>🔒 الاشتراك الإجباري مفعل لكن لم يتم تحديد قناة!</b>", parse_mode="HTML")
        return

    # 4. حفظ المستخدم الجديد وإشعار الإدارة
    if not get_user(user_id):
        save_user(
            user_id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
            last_name=message.from_user.last_name or ""
        )
        for admin in ADMIN_IDS:
            try:
                caption = (
                    f"🆕 <b>مستخدم جديد دخل البوت:</b>\n"
                    f"<b>🆔:</b> <code>{user_id}</code>\n"
                    f"<b>👤:</b> @{safe_html(message.from_user.username or 'None')}\n"
                    f"<b>الاسم:</b> {safe_html(message.from_user.first_name or '')}"
                )
                bot.send_message(admin, caption, parse_mode="HTML")
            except:
                pass
    
    # 5. بناء قائمة الأزرار (الدول والكومبوهات)
    # ✨🌟🌟🌟 أزرار ملونة محسّنة 🌟🌟🌟✨
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    user_data = get_user(user_id)
    private_combo = user_data[7] if user_data else None
    all_combos = get_all_combos()

    # تجميع الكومبوهات لكل دولة
    country_combos = {}
    for country_code, combo_index in all_combos:
        if country_code not in country_combos:
            country_combos[country_code] = []
        country_combos[country_code].append(combo_index)

    # الكومبو الخاص أولاً
    if private_combo and private_combo in COUNTRY_CODES:
        name, flag, _ = COUNTRY_CODES[private_combo]
        buttons.append(types.InlineKeyboardButton(
            f"{BUTTON_COLORS['success']} {flag} {name} (خاص)",
            callback_data=f"country_{private_combo}_1"
        ))

    # عمل أزرار لكل كومبو
    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES and country_code != private_combo:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                if len(indices) == 1:
                    btn_text = f"{BUTTON_COLORS['primary']} {flag} {name}"
                else:
                    btn_text = f"{BUTTON_COLORS['primary']} {flag} {name} (#{idx})"
                buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"country_{country_code}_{idx}"))

    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    # زر لوحة التحكم للأدمن فقط
    if is_admin(user_id):
        markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['admin']} لوحة التحكم", callback_data="admin_panel"))

    # 6. الرسالة الترحيبية المنسقة
    fancy_text = (
        "<b>❍<u>💀 𝐇𝐀𝐂𝐊𝐄𝐑 𝐓𝐀𝐊𝐄𝐑 𝐓𝐄𝐑𝐌𝐈𝐍𝐀𝐋 💀</u>❍</b>\n\n"
        "<b>🧠 <u>𝐒𝐘𝐒𝐓𝐄𝐌 𝐋𝐎𝐀𝐃𝐈𝐍𝐆...</u></b>\n"
        "<b>⚡ Injecting modules: ████████████ 100%</b>\n"
        "<b>🛡 Firewall status: ACTIVE</b>\n"
        "<b>🌐 Network: STABLE CONNECTION</b>\n\n"
        "<b>📡 <u>𝐀𝐂𝐂𝐄𝐒𝐒 𝐋𝐄𝐕𝐄𝐋</u></b>\n"
        "<b>🔓 USER: AUTHORIZED</b>\n"
        "<b>🎯 MODE: ADMIN CONTROL PANEL</b>\n\n"
        "<b>🎓 <u>𝐎𝐖𝐍𝐄𝐑</u> • <a href='tg://user?id=6640004356'>ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟 (@hackerTaker7)</a></b>\n\n"
        "<b>────────────────────────────</b>\n\n"
        "<b>💾 <u>𝐂𝐎𝐍𝐒𝐎𝐋𝐄</u></b>\n"
        "<b>▶ اختر الدولة التي تريد تشغيل العمليات عليها من الأسفل</b>\n"
        "<b>⏳ Waiting for input...</b>\n"
    )
    
    welcome_photo = get_setting("welcome_photo")
    if welcome_photo:
        try:
            bot.send_photo(
                chat_id,
                welcome_photo,
                caption=fancy_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        except:
            bot.send_message(
                chat_id,
                fancy_text,
                parse_mode="HTML",
                reply_markup=markup,
                disable_web_page_preview=True
            )
    else:
        bot.send_message(
            chat_id,
            fancy_text,
            parse_mode="HTML",
            reply_markup=markup,
            disable_web_page_preview=True
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if force_sub_check(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق! يمكنك استخدام البوت الآن.", show_alert=True)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def handle_country_selection(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
        return
    if not force_sub_check(user_id):
        markup = force_sub_markup()
        bot.send_message(chat_id, "<b>🔒 يجب الاشتراك في القناة لاستخدام البوت.</b>", parse_mode="HTML", reply_markup=markup)
        return

    parts = call.data.split("_")
    country_code = parts[1]
    combo_index = int(parts[2]) if len(parts) > 2 else 1
    
    available_numbers = get_available_numbers(country_code, combo_index, user_id)
    
    if not available_numbers:
        error_msg = f"<b>{BUTTON_COLORS['danger']} ❌ نعتذر، جميع الأرقام قيد الاستخدام حالياً لهذه الدولة.</b>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            f"{BUTTON_COLORS['back']} العودة لاختيار دولة أخرى",
            callback_data="back_to_countries"
        ))
        bot.edit_message_text(error_msg, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        return

    assigned = random.choice(available_numbers)
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    
    assign_number_to_user(user_id, assigned)
    save_user(user_id, country_code=country_code, assigned_number=assigned)
    
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    msg_text = (
        f"<b>{BUTTON_COLORS['success']} ◈ Number:</b> <code>+{assigned}</code>\n"
        f"<b>{BUTTON_COLORS['info']} ◈ Country:</b> {flag} {name}\n"
        f"<b>{BUTTON_COLORS['primary']} ◈ Combo:</b> #{combo_index}\n"
        f"<b>{BUTTON_COLORS['warning']} ◈ Status :</b> ⏳ Waiting for SMS"
    )

    # ✨🌟🌟🌟 لوحة أزرار ملونة محسّنة 🌟🌟🌟✨
    markup = types.InlineKeyboardMarkup()
    
    markup.add(types.InlineKeyboardButton(
        f"{BUTTON_COLORS['info']} 📢 قناة البوت",
        url="https://t.me/shhsnbdb"
    ))
    
    markup.row(
        types.InlineKeyboardButton(
            f"{BUTTON_COLORS['refresh']} تغيير الرقم",
            callback_data=f"change_num_{country_code}_{combo_index}"
        ),
        types.InlineKeyboardButton(
            f"{BUTTON_COLORS['back']} رجوع",
            callback_data="back_to_countries"
        )
    )

    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=msg_text,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error updating message: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_num_"))
def handle_change_number(call):
    handle_country_selection(call)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_countries")
def back_to_main(call):
    # ✨🌟🌟🌟 أزرار ملونة محسّنة 🌟🌟🌟✨
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    user_data = get_user(call.from_user.id)
    private_combo = user_data[7] if user_data else None
    all_combos = get_all_combos()

    country_combos = {}
    for country_code, combo_index in all_combos:
        if country_code not in country_combos:
            country_combos[country_code] = []
        country_combos[country_code].append(combo_index)

    if private_combo and private_combo in COUNTRY_CODES:
        name, flag, _ = COUNTRY_CODES[private_combo]
        buttons.append(types.InlineKeyboardButton(
            f"{BUTTON_COLORS['success']} {flag} {name} (خاص)",
            callback_data=f"country_{private_combo}_1"
        ))

    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES and country_code != private_combo:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                if len(indices) == 1:
                    btn_text = f"{BUTTON_COLORS['primary']} {flag} {name}"
                else:
                    btn_text = f"{BUTTON_COLORS['primary']} {flag} {name} (#{idx})"
                buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"country_{country_code}_{idx}"))

    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    if is_admin(call.from_user.id):
        admin_btn = types.InlineKeyboardButton(
            f"{BUTTON_COLORS['admin']} لوحة التحكم",
            callback_data="admin_panel"
        )
        markup.add(admin_btn)

    fancy_text = (
        "<b>❍<u>𝐖𝐄𝐋𝐂𝐎𝐌 𝐓𝐎 ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟 𝐁𝐎𝐓 </u>❍</b>\n\n"
        "<b>🔋 <u>𝐅𝐚𝐬𝐭  • 𝐒𝐞𝐜𝐮𝐫𝐞  • 𝐨𝐢𝐧𝐞</u></b>\n\n"
        "<b>🎓 <u>𝐎𝐰𝐧𝐞𝐫</u>  • <a href='tg://user?id=8355137132'>ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟</a></b>\n\n"
        "<b>────────────────────</b>\n"
        "<b><u>اخـتـر الــدولـة الـتـي تـريـدهـا مـن الـزر الاسـفـل</u> ⬇️</b>"
    )

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=fancy_text,
            parse_mode="HTML",
            reply_markup=markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error editing message: {e}")
        bot.answer_callback_query(call.id)

# ======================
# 🔐 لوحة التحكم الإدارية
# ======================
user_states = {}

def admin_main_menu():
    # ✨🌟🌟🌟 لوحة تحكم بأزرار ملونة 🌟🌟🌟✨
    markup = types.InlineKeyboardMarkup()
    
    # 1. زر حالة البوت
    status_icon = "🟢" if not is_maintenance_mode() else "🔴"
    status_text = "يعمل" if not is_maintenance_mode() else "صيانة"
    markup.add(types.InlineKeyboardButton(
        f"{status_icon} {status_text} {status_icon}",
        callback_data="toggle_maintenance"
    ))
    
    # 2. قسم إدارة الكومبوهات
    markup.row(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['success']} 📥 إضافة كومبو", callback_data="admin_add_combo"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} 🗑️ حذف كومبو", callback_data="admin_del_combo")
    )
    
    # 3. قسم الإحصائيات والتقارير
    markup.row(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['info']} 📊 الإحصائيات", callback_data="admin_stats"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['info']} 📄 تقرير", callback_data="admin_full_report")
    )
    
    # 4. قسم الإذاعة
    markup.row(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['primary']} 📢 إذاعة", callback_data="admin_broadcast_all"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['primary']} 📨 إذاعة لمستخدم", callback_data="admin_broadcast_user")
    )
    
    # 5. قسم إدارة المستخدمين
    markup.row(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} 🚫 حظر", callback_data="admin_ban"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['success']} ✅ فك حظر", callback_data="admin_unban"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['info']} 👤 معلومات", callback_data="admin_user_info")
    )
    
    # 6. قسم الإعدادات المتقدمة
    markup.row(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['warning']} 🔗 اشتراك", callback_data="admin_force_sub"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['warning']} 🖥️ اللوحات", callback_data="admin_dashboards"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['warning']} 🔑 برايفت", callback_data="admin_private_combo")
    )

    # 7. قسم إعدادات الصورة
    markup.row(
        types.InlineKeyboardButton(f"{BUTTON_COLORS['primary']} 🖼️ صورة الترحيب", callback_data="admin_set_welcome_photo"),
        types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} 🗑️ حذف الصورة", callback_data="admin_del_welcome_photo")
    )

    # 8. زر الخروج
    markup.add(types.InlineKeyboardButton(
        f"{BUTTON_COLORS['back']} 🔙 خروج",
        callback_data="back_to_countries"
    ))
    
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def show_admin_panel(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⚠️ عذراً، هذا القسم للمطورين فقط.", show_alert=True)
        return

    if call.from_user.id in user_states:
        del user_states[call.from_user.id]

    admin_text = (
        "<b>╔════════════════════╗</b>\n"
        "<b>   ⚙️ لوحة التحكم | ADMIN PANEL</b>\n"
        "<b>╚════════════════════╝</b>\n\n"
        "<b>👤 مرحباً بك يا مطور</b>\n"
        "<b>تم تسجيل دخولك إلى لوحة التحكم بنجاح.</b>\n"
        "<b>أنت الآن تملك الصلاحيات الكاملة لإدارة البوت.</b>\n\n"
        "<b>📌 الوظائف المتاحة:</b>\n"
        "<b>• إدارة المستخدمين</b>\n"
        "<b>• التحكم في إعدادات البوت</b>\n"
        "<b>• تشغيل / إيقاف الخدمات</b>\n"
        "<b>• متابعة الإحصائيات</b>\n\n"
        "<b>⚠️ تنبيه أمني:</b>\n"
        "<b>أي تعديل يتم تطبيقه مباشرة بدون تأخير.</b>\n\n"
        "<b>────────────────────</b>\n"
        "<b>📊 حالة النظام:</b>\n"
        "<b>• السيرفر: <u>Online ✅</u></b>\n"
        f"<b>• الوقت: <u>{datetime.now().strftime('%H:%M')}</u></b>\n"
        "<b>────────────────────</b>\n\n"
        "<b>🚀 لوحة احترافية جاهزة للإدارة</b>"
    )
    
    try:
        bot.answer_callback_query(call.id)
        
        if call.message.content_type != 'text':
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(
                chat_id=call.message.chat.id,
                text=admin_text,
                parse_mode="HTML",
                reply_markup=admin_main_menu(),
                disable_web_page_preview=True
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=admin_text,
                parse_mode="HTML",
                reply_markup=admin_main_menu(),
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"Admin Panel Error: {e}")
        try:
            bot.send_message(call.message.chat.id, admin_text, parse_mode="HTML", reply_markup=admin_main_menu())
        except:
            pass

# ======================
# 🖼️ ميزة تغيير صورة الترحيب
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_set_welcome_photo")
def admin_set_welcome_photo(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_for_welcome_photo"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} إلغاء", callback_data="admin_panel"))
    bot.edit_message_text("🖼️ حسناً، أرسل الآن الصورة التي تريد ظهورها مع رسالة الترحيب:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(content_types=['photo'], func=lambda msg: user_states.get(msg.from_user.id) == "waiting_for_welcome_photo")
def handle_welcome_photo_upload(message):
    if not is_admin(message.from_user.id): return
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
        
    photo_id = message.photo[-1].file_id
    set_setting("welcome_photo", photo_id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} العودة للوحة التحكم", callback_data="admin_panel"))
    
    bot.send_message(message.chat.id, "✅ تم حفظ صورة الترحيب بنجاح! ستظهر الآن للمستخدمين عند ضغط /start", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_welcome_photo")
def admin_del_welcome_photo(call):
    if not is_admin(call.from_user.id): return
    set_setting("welcome_photo", "")
    bot.answer_callback_query(call.id, "🗑️ تم حذف صورة الترحيب. سيظهر النص فقط الآن.", show_alert=True)
    show_admin_panel(call)

# ======================
# 📌 ميزة الاشتراك الإجباري
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_force_sub")
def admin_force_sub(call):
    if not is_admin(call.from_user.id):
        return

    channels = get_all_force_sub_channels(enabled_only=False)
    text = "⚙️ إدارة قنوات الاشتراك الإجباري:\n"
    text += f"إجمالي القنوات: {len(channels)}\n"
    text += "──────────────────\n"

    markup = types.InlineKeyboardMarkup()
    for ch_id, url, desc in channels:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT enabled FROM force_sub_channels WHERE id=?", (ch_id,))
        enabled = c.fetchone()[0]
        conn.close()
        status = "✅" if enabled else "❌"
        btn_text = f"{status} {desc or url[:25]}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"edit_force_ch_{ch_id}"))

    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['success']} ➕ إضافة قناة", callback_data="add_force_ch"))
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} 🔙 رجوع", callback_data="admin_panel"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_maintenance")
def handle_maintenance_toggle(call):
    if not is_admin(call.from_user.id): return
    
    current_status = is_maintenance_mode()
    set_maintenance_mode(not current_status)
    
    new_status_text = "🔓 تم فتح البوت للجميع" if current_status else "🔒 تم قفل البوت (وضع الصيانة)"
    
    bot.answer_callback_query(call.id, new_status_text, show_alert=True)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
    
@bot.callback_query_handler(func=lambda call: call.data == "add_force_ch")
def add_force_ch_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "add_force_ch_url"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_force_sub"))
    bot.edit_message_text("أرسل رابط القناة (مثل: https://t.me/xxx أو @xxx):", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_force_ch_url")
def add_force_ch_step2(message):
    url = message.text.strip()
    if not (url.startswith("@") or url.startswith("https://t.me/")):
        bot.reply_to(message, "❌ رابط غير صالح! يجب أن يبدأ بـ @ أو https://t.me/")
        return
    user_states[message.from_user.id] = {"step": "add_force_ch_desc", "url": url}
    bot.reply_to(message, "أدخل وصفًا للقناة (أو اترك فارغًا):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_force_ch_desc")
def add_force_ch_step3(message):
    data = user_states[message.from_user.id]
    url = data["url"]
    desc = message.text.strip()
    if add_force_sub_channel(url, desc):
        bot.reply_to(message, f"✅ تم إضافة القناة:\n{url}\nالوصف: {desc or '—'}")
    else:
        bot.reply_to(message, "❌ القناة موجودة مسبقًا!")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_force_ch_"))
def edit_force_ch(call):
    if not is_admin(call.from_user.id):
        return
    try:
        ch_id = int(call.data.split("_", 3)[3])
    except:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT channel_url, description, enabled FROM force_sub_channels WHERE id=?", (ch_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ القناة غير موجودة!", show_alert=True)
        return

    url, desc, enabled = row
    status = "مفعلة" if enabled else "معطلة"
    text = f"🔧 إدارة القناة:\nالرابط: {url}\nالوصف: {desc or '—'}\nالحالة: {status}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ تعديل الوصف", callback_data=f"edit_desc_{ch_id}"))
    if enabled:
        markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} ❌ تعطيل", callback_data=f"toggle_ch_{ch_id}"))
    else:
        markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['success']} ✅ تفعيل", callback_data=f"toggle_ch_{ch_id}"))
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} 🗑️ حذف", callback_data=f"del_ch_{ch_id}"))
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} 🔙 رجوع", callback_data="admin_force_sub"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_ch_"))
def toggle_ch(call):
    ch_id = int(call.data.split("_", 2)[2])
    toggle_force_sub_channel(ch_id)
    bot.answer_callback_query(call.id, "🔄 تم تغيير حالة القناة", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_ch_"))
def del_ch(call):
    ch_id = int(call.data.split("_", 2)[2])
    if delete_force_sub_channel(ch_id):
        bot.answer_callback_query(call.id, "🗑️ تم حذف القناة بنجاح", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_desc_"))
def edit_desc_step1(call):
    ch_id = int(call.data.split("_", 2)[2])
    user_states[call.from_user.id] = {"step": "edit_ch_desc", "id": ch_id}
    bot.edit_message_text("أدخل الوصف الجديد للقناة:", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "edit_ch_desc")
def edit_desc_step2(message):
    data = user_states[message.from_user.id]
    ch_id = data["id"]
    new_desc = message.text.strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE force_sub_channels SET description=? WHERE id=?", (new_desc, ch_id))
    conn.commit()
    conn.close()
    bot.reply_to(message, "✅ تم تحديث الوصف بنجاح!")
    del user_states[message.from_user.id]

# ======================
# 📥 إضافة وحذف الكومبوهات (أدمن)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_combo")
def admin_add_combo_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "add_combo_country"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_panel"))
    bot.edit_message_text("أرسل كود الدولة (مثل 20 لمصر):", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_combo_country")
def admin_add_combo_step2(message):
    code = message.text.strip().replace("+", "")
    if code not in COUNTRY_CODES:
        bot.reply_to(message, "❌ كود دولة غير مدعوم!")
        return
    user_states[message.from_user.id] = {"step": "add_combo_numbers", "code": code}
    bot.reply_to(message, f"أرسل الأرقام لدولة {COUNTRY_CODES[code][0]} (نصياً أو قم برفع ملف .txt):")

@bot.message_handler(content_types=['text', 'document'], func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_combo_numbers")
def admin_add_combo_step3(message):
    data = user_states[message.from_user.id]
    code = data["code"]
    numbers = []

    if message.content_type == 'text':
        numbers = [clean_number(n) for n in message.text.split("\n") if clean_number(n)]
    elif message.content_type == 'document':
        if message.document.file_name.endswith('.txt'):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            try:
                content = downloaded_file.decode('utf-8')
                numbers = [clean_number(n) for n in content.split("\n") if clean_number(n)]
            except Exception as e:
                bot.reply_to(message, f"❌ خطأ في قراءة الملف: {e}")
                return
        else:
            bot.reply_to(message, "❌ يرجى إرسال ملف بصيغة .txt فقط!")
            return

    if not numbers:
        bot.reply_to(message, "❌ لم يتم العثور على أرقام صالحة في الرسالة أو الملف!")
        return
        
    save_combo(code, numbers)
    bot.reply_to(message, f"✅ تم إضافة {len(numbers)} رقم بنجاح لدولة {COUNTRY_CODES[code][0]}!")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_combo")
def admin_del_combo_step1(call):
    if not is_admin(call.from_user.id): return
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "❌ لا توجد كومبوهات لحذفها!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for code, idx in combos:
        name, flag, _ = COUNTRY_CODES.get(code, (code, "🌍", ""))
        markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} 🗑️ {flag} {name} (#{idx})", callback_data=f"del_combo_{code}_{idx}"))
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_panel"))
    bot.edit_message_text("اختر الكومبو المراد حذفه:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_combo_"))
def admin_del_combo_step2(call):
    parts = call.data.split("_")
    code, idx = parts[2], int(parts[3])
    if delete_combo(code, idx):
        bot.answer_callback_query(call.id, "✅ تم الحذف بنجاح", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل الحذف", show_alert=True)
    admin_del_combo_step1(call)

# ======================
# 📊 الإحصائيات والتقارير
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id): return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1")
    banned_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM otp_logs")
    total_otps = c.fetchone()[0]
    conn.close()
    
    stats_text = (
        "<b>📊 إحصائيات البوت:</b>\n\n"
        f"<b>• إجمالي المستخدمين:</b> {total_users}\n"
        f"<b>• المحظورين:</b> {banned_users}\n"
        f"<b>• إجمالي الأكواد المستلمة:</b> {total_otps}\n"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_panel"))
    bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "admin_full_report")
def admin_full_report(call):
    if not is_admin(call.from_user.id): return
    try:
        with open(DB_PATH, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption="📄 تقرير شامل (قاعدة البيانات)")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {e}", show_alert=True)

# ======================
# 📢 نظام الإذاعة (Broadcast)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_all")
def admin_broadcast_all_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_broadcast_msg"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} إلغاء", callback_data="admin_panel"))
    bot.edit_message_text("أرسل الرسالة التي تريد إذاعتها لجميع المستخدمين:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_broadcast_msg")
def admin_broadcast_all_step2(message):
    if not is_admin(message.from_user.id): return
    users = get_all_users()
    count = 0
    for uid in users:
        try:
            bot.copy_message(uid, message.chat.id, message.message_id)
            count += 1
            time.sleep(0.05)
        except: pass
    bot.reply_to(message, f"✅ تم إرسال الإذاعة لـ {count} مستخدم بنجاح!")
    del user_states[message.from_user.id]

# ======================
# 🚫 إدارة الحظر والمعلومات
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_ban")
def admin_ban_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_ban_uid"
    bot.edit_message_text("أرسل ID المستخدم المراد حظره:", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_ban_uid")
def admin_ban_step2(message):
    try:
        uid = int(message.text)
        ban_user(uid)
        bot.reply_to(message, f"✅ تم حظر المستخدم {uid} بنجاح!")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_unban")
def admin_unban_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_unban_uid"
    bot.edit_message_text("أرسل ID المستخدم لفك حظره:", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_unban_uid")
def admin_unban_step2(message):
    try:
        uid = int(message.text)
        unban_user(uid)
        bot.reply_to(message, f"✅ تم فك حظر المستخدم {uid} بنجاح!")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_user_info")
def admin_user_info_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_info_uid"
    bot.edit_message_text("أرسل ID المستخدم لجلب معلوماته:", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_info_uid")
def admin_user_info_step2(message):
    try:
        uid = int(message.text)
        user = get_user(uid)
        if user:
            info = (
                f"👤 <b>معلومات المستخدم:</b>\n"
                f"<b>ID:</b> <code>{user[0]}</code>\n"
                f"<b>Username:</b> @{user[1]}\n"
                f"<b>Name:</b> {user[2]} {user[3]}\n"
                f"<b>Banned:</b> {'Yes' if user[6] else 'No'}\n"
                f"<b>Assigned Num:</b> {user[5] or 'None'}"
            )
            bot.reply_to(message, info, parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ المستخدم غير موجود في قاعدة البيانات.")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")
    del user_states[message.from_user.id]

# ======================
# 🔑 إدارة الكومبوهات الخاصة (Private)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_private_combo")
def admin_private_combo(call):
    if not is_admin(call.from_user.id): return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['success']} ➕ تعيين برايفت", callback_data="add_private_combo"))
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['danger']} 🗑️ حذف برايفت", callback_data="del_private_combo"))
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_panel"))
    bot.edit_message_text("🔑 إدارة الكومبوهات الخاصة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_private_combo")
def add_private_combo_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "add_private_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_private_combo"))
    bot.edit_message_text("أدخل معرف المستخدم (User ID):", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_private_user_id")
def add_private_combo_step2(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = {"step": "add_private_country", "uid": uid}
        markup = types.InlineKeyboardMarkup()
        for code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[code]
            markup.add(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"select_private_{uid}_{code}"))
        markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_private_combo"))
        bot.reply_to(message, "اختر الدولة:", reply_markup=markup)
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_private_"))
def select_private_combo(call):
    parts = call.data.split("_")
    uid = int(parts[2])
    country_code = parts[3]
    save_user(uid, private_combo_country=country_code)
    name, flag, _ = COUNTRY_CODES[country_code]
    bot.answer_callback_query(call.id, f"✅ تم تعيين كومبو برايفت لـ {uid} - {flag} {name}", show_alert=True)
    admin_private_combo(call)

@bot.callback_query_handler(func=lambda call: call.data == "del_private_combo")
def del_private_combo_step1(call):
    if not is_admin(call.from_user.id):
        return
    user_states[call.from_user.id] = "del_private_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{BUTTON_COLORS['back']} رجوع", callback_data="admin_private_combo"))
    bot.edit_message_text("أدخل معرف المستخدم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "del_private_user_id")
def del_private_combo_step2(message):
    try:
        uid = int(message.text)
        save_user(uid, private_combo_country=None)
        bot.reply_to(message, f"✅ تم مسح الكومبو البرايفت للمستخدم {uid}")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")
    del user_states[message.from_user.id]

# ======================
# 🆕 جلب الأرقام المتاحة
# ======================
def get_available_numbers(country_code, combo_index=1, user_id=None):
    all_numbers = get_combo(country_code, combo_index, user_id)
    if not all_numbers:
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number != ''")
    used_numbers = set(row[0] for row in c.fetchall())
    conn.close()
    available = [num for num in all_numbers if num not in used_numbers]
    return available

# ======================
# 🔄 الدوال الأساسية للتنظيف والمعالجة
# ======================
def clean_html(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    return text

def clean_number(number):
    if not number:
        return ""
    number = re.sub(r'\D', '', str(number))
    return number

def get_country_info(number):
    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")

    for code, (name, flag, short) in COUNTRY_CODES.items():
        if number.startswith(code):
            return name, flag, short

    return "Unknown", "🌍", "UN"

def mask_number(number):
    number = number.strip()
    if len(number) > 8:
        return number[:4] + "⁦⁦••••" + number[-3:]
    return number

def extract_otp(message):
    patterns = [
        r'(?:code|رمز|كود|verification|تحقق|otp|pin)[:\s]+[‎]?(\d{3,8}(?:[- ]\d{3,4})?)',
        r'(\d{3})[- ](\d{3,4})',
        r'\b(\d{4,8})\b',
        r'[‎](\d{3,8})',
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            if len(match.groups()) > 1:
                return ''.join(match.groups())
            return match.group(1).replace(' ', '').replace('-', '')
    all_numbers = re.findall(r'\d{4,8}', message)
    if all_numbers:
        return all_numbers[0]
    return "N/A"

def detect_service(message):
    message_lower = message.lower()

    services = {
        "#WP": ["whatsapp", "واتساب", "واتس"],
        "#FB": ["facebook", "فيسبوك", "fb"],
        "#IG": ["instagram", "انستقرام", "انستا"],
        "#TG": ["telegram", "تيليجرام", "تلي"],
        "#TW": ["twitter", "تويتر", "x"],
        "#GG": ["google", "gmail", "جوجل", "جميل"],
        "#DC": ["discord", "ديسكورد"],
        "#LN": ["line", "لاين"],
        "#VB": ["viber", "فايبر"],
        "#SK": ["skype", "سكايب"],
        "#SC": ["snapchat", "سناب"],
        "#TT": ["tiktok", "تيك توك", "تيك"],
        "#AMZ": ["amazon", "امازون"],
        "#APL": ["apple", "ابل", "icloud"],
        "#MS": ["microsoft", "مايكروسوفت"],
        "#IN": ["linkedin", "لينكد"],
        "#UB": ["uber", "اوبر"],
        "#AB": ["airbnb", "ايربنب"],
        "#NF": ["netflix", "نتفلكس"],
        "#SP": ["spotify", "سبوتيفاي"],
        "#YT": ["youtube", "يوتيوب"],
        "#GH": ["github", "جيت هاب"],
        "#PT": ["pinterest", "بنتريست"],
        "#PP": ["paypal", "باي بال"],
        "#BK": ["booking", "بوكينج"],
        "#TL": ["tala", "تالا"],
        "#OLX": ["olx", "اوليكس"],
        "#STC": ["stcpay", "stc"],
    }

    for service_code, keywords in services.items():
        for keyword in keywords:
            if keyword in message_lower:
                return service_code

    if "code" in message_lower or "verification" in message_lower:
        if "telegram" in message_lower:
            return "#TG"
        if "whatsapp" in message_lower:
            return "#WP"
        if "facebook" in message_lower:
            return "#FB"
        if "instagram" in message_lower:
            return "#IG"
        if "google" in message_lower or "gmail" in message_lower:
            return "#GG"
        if "twitter" in message_lower or "x.com" in message_lower:
            return "#TW"

    return "Unknown"

def html_escape(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def format_message(date_str, number, sms):
    country_name, country_flag, country_code = get_country_info(number)
    masked_num = mask_number(number)
    otp_code = extract_otp(sms)
    service = detect_service(sms)

    message = (
        f"╭───────────────╮\n"
        f"│ {country_flag} {service} {masked_num}\n"
        f"╰───────────────╯"
    )
    return message

# ======================
# 📡 دوال الاتصال بلوحة iVasms
# ======================

def login_to_ivasms():
    try:
        dash = IVASMS_DASHBOARD
        login_url = dash["login_url"]
        base_url = dash["base_url"]
        username = dash["username"]
        password = dash["password"]
        session = dash["session"]

        print(f"[{dash['name']}] محاولة تسجيل الدخول...")
        
        login_page_resp = session.get(login_url, timeout=30)
        login_page_resp.raise_for_status()
        
        soup = BeautifulSoup(login_page_resp.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        csrf_token = token_input['value'] if token_input else None
        
        login_data = {
            'email': username,
            'password': password
        }
        if csrf_token:
            login_data['_token'] = csrf_token
        
        login_resp = session.post(login_url, data=login_data, timeout=30)
        
        if "login" not in login_resp.url.lower():
            print(f"[{dash['name']}] ✅ تسجيل الدخول ناجح")
            
            dashboard_soup = BeautifulSoup(login_resp.text, 'html.parser')
            csrf_meta = dashboard_soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                dash['csrf_token'] = csrf_meta.get('content')
            else:
                print(f"[{dash['name']}] ⚠️ لم يتم العثور على CSRF token")
            
            dash['is_logged_in'] = True
            dash['cookies'] = session.cookies.get_dict()
            return True
        else:
            print(f"[{dash['name']}] ❌ فشل تسجيل الدخول")
            return False
            
    except Exception as e:
        print(f"[{dash['name']}] ❌ خطأ في تسجيل الدخول: {e}")
        return False

def fetch_ivasms_messages():
    dash = IVASMS_DASHBOARD
    
    if not dash.get('is_logged_in', False):
        if not login_to_ivasms():
            return []
    
    try:
        session = dash['session']
        base_url = dash['base_url']
        sms_api_url = dash['sms_api_endpoint']
        csrf_token = dash.get('csrf_token')
        
        if not csrf_token:
            print(f"[{dash['name']}] ⚠️ CSRF token غير متوفر")
            return []
        
        headers = {
            'Referer': f"{base_url}/portal/sms/received",
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        today = datetime.utcnow()
        start_date = (today - timedelta(days=1)).strftime('%m/%d/%Y')
        end_date = today.strftime('%m/%d/%Y')
        
        summary_payload = {
            'from': start_date,
            'to': end_date,
            '_token': csrf_token
        }
        
        summary_resp = session.post(sms_api_url, headers=headers, data=summary_payload, timeout=30)
        summary_resp.raise_for_status()
        
        soup = BeautifulSoup(summary_resp.text, 'html.parser')
        range_options = soup.find_all('option')
        group_ids = [opt['value'] for opt in range_options if opt['value']]
        
        all_messages = []
        
        sms_details_url = urljoin(base_url, "portal/sms/received/getsms/number/sms")
        
        for group_id in group_ids:
            numbers_payload = {
                'start': start_date,
                'end': end_date,
                'range': group_id,
                '_token': csrf_token
            }
            
            numbers_resp = session.post(sms_api_url, headers=headers, data=numbers_payload, timeout=30)
            numbers_soup = BeautifulSoup(numbers_resp.text, 'html.parser')
            number_divs = numbers_soup.find_all('div', class_='phone-number')
            phone_numbers = [div.text.strip() for div in number_divs]
            
            for phone in phone_numbers:
                sms_payload = {
                    'start': start_date,
                    'end': end_date,
                    'Number': phone,
                    'Range': group_id,
                    '_token': csrf_token
                }
                
                sms_resp = session.post(sms_details_url, headers=headers, data=sms_payload, timeout=30)
                sms_data = sms_resp.json()
                
                if sms_data and 'messages' in sms_data:
                    for msg in sms_data['messages']:
                        all_messages.append({
                            'date': msg.get('created_at'),
                            'number': phone,
                            'sms': msg.get('message')
                        })
                        
        return all_messages
        
    except Exception as e:
        print(f"[{dash['name']}] ❌ خطأ في جلب الرسائل: {e}")
        if "401" in str(e) or "login" in str(e).lower():
            dash['is_logged_in'] = False
        return []

# ======================
# 🔄 الحلقة الأساسية للبوت (Main Loop)
# ======================

def load_sent_messages():
    if os.path.exists(SENT_MESSAGES_FILE):
        try:
            with open(SENT_MESSAGES_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_sent_messages(sent_set):
    with open(SENT_MESSAGES_FILE, "w") as f:
        json.dump(list(sent_set), f)

def delete_message_after_delay(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def send_to_telegram(formatted_text, otp_code, chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # ✨🌟🌟🌟 كيبورد ملون لنسخ الكود 🌟🌟🌟✨
    keyboard = {
        "inline_keyboard": [
            [
                {"text": f"{BUTTON_COLORS['otp']} 𝐂𝐎𝐏𝐘 𝐎𝐓𝐏", "callback_data": f"copy_{otp_code}"}
            ]
        ]
    }
    
    payload = {
        "chat_id": chat_id,
        "text": formatted_text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    }
    
    success_count = 0
    try:
        resp = requests.post(url, data=payload, timeout=30)
        if resp.status_code == 200:
            success_count += 1
            msg_id = resp.json()["result"]["message_id"]
            threading.Thread(
                target=delete_message_after_delay,
                args=(chat_id, msg_id, 150),
                daemon=True
            ).start()
        else:
            print(f"[!] فشل إرسال إلى {chat_id}: {resp.status_code}")
    except Exception as e:
        print(f"[!] خطأ في الإرسال لـ {chat_id}: {e}")

    return success_count > 0

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def handle_copy_button(call):
    otp_code = call.data.split("_", 1)[1]
    # ✨🌟🌟🌟 إشعار ملون عند نسخ الكود 🌟🌟🌟✨
    bot.answer_callback_query(call.id, f"✅ {BUTTON_COLORS['success']} تم نسخ الكود: {otp_code}", show_alert=True)

# ✨🌟🌟🌟 دالة إرسال OTP للمستخدمين المعنيين (مضافة) 🌟🌟🌟✨
def send_otp_to_user(user_id, number, otp_code, full_message):
    """
    ✅ إرسال OTP مباشرة للمستخدم صاحب الرقم مع واجهة ملونة
    """
    try:
        country_name, country_flag, _ = get_country_info(number)
        msg_text = (
            f"<b>{BUTTON_COLORS['otp']} 📨 وصول رسالة جديدة!</b>\n\n"
            f"<b>{BUTTON_COLORS['number']} الرقم:</b> <code>+{number}</code>\n"
            f"<b>{BUTTON_COLORS['country']} الدولة:</b> {country_flag} {country_name}\n"
            f"<b>{BUTTON_COLORS['success']} الكود:</b> <code>{otp_code}</code>\n\n"
            f"<b>{BUTTON_COLORS['info']} 📝 الرسالة كاملة:</b>\n{full_message[:200]}"
        )
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            f"{BUTTON_COLORS['success']} 📋 نسخ الكود {otp_code}",
            callback_data=f"copy_{otp_code}"
        ))
        markup.add(types.InlineKeyboardButton(
            f"{BUTTON_COLORS['refresh']} 🔄 طلب رقم جديد",
            callback_data="back_to_countries"
        ))
        
        bot.send_message(user_id, msg_text, parse_mode="HTML", reply_markup=markup)
        return True
    except Exception as e:
        print(f"Error sending OTP to user {user_id}: {e}")
        return False

# ======================
# 🚀 تشغيل البوت
# ======================

def main_loop():
    print(f"[*] Starting main loop (Interval: {REFRESH_INTERVAL}s)...")
    sent_messages = load_sent_messages()
    
    while True:
        try:
            messages = fetch_ivasms_messages()
            
            new_sent = False
            for msg in messages:
                msg_date = msg['date']
                phone = clean_number(msg['number'])
                sms_text = msg['sms']
                
                msg_hash = f"{msg_date}_{phone}_{sms_text[:50]}"
                
                if msg_hash not in sent_messages:
                    formatted = format_message(msg_date, phone, sms_text)
                    otp = extract_otp(sms_text)
                    
                    target_user = get_user_by_number(phone)
                    
                    # الإرسال للجروبات الأساسية
                    for chat_id in CHAT_IDS:
                        send_to_telegram(formatted, otp, chat_id)
                    
                    # ✨🌟🌟🌟 إرسال OTP للمستخدم صاحب الرقم (مضافة) 🌟🌟🌟✨
                    if target_user:
                        send_otp_to_user(target_user, phone, otp, sms_text)
                    
                    log_otp(phone, otp, sms_text, assigned_to=target_user)
                    
                    sent_messages.add(msg_hash)
                    new_sent = True
                    print(f"[+] New SMS: {phone} -> {otp}")
            
            if new_sent:
                save_sent_messages(sent_messages)
                
        except Exception as e:
            print(f"[!] Error in main loop: {e}")
            traceback.print_exc()
            
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    print("[*] Starting System...")
    
    sms_thread = threading.Thread(target=main_loop, daemon=True)
    sms_thread.start()
    print("📡 SMS Polling Thread Started.")
    
    print("🤖 Telegram Bot Started and Listening...")
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"❌ Critical Error in Bot Polling: {e}")


# ==========================================
# Project Modified & Enhanced
# Developer  : ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟
# Telegram   : @hackerTaker7
# Edition    : Sudanese Arabic Localization
# Status     : Stable Release
# ==========================================

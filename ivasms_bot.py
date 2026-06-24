# -*- coding: utf-8 -*-
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


# منع تكرار رسالة انتهاء الكوكيز
_cookies_alert_sent = False

# منع تعارض login من مصادر متعددة
_login_lock = threading.Lock()
_login_in_progress = False
_cookies_expired = False  # لما الكوكيز تنتهي يوقف المحاولات


COOKIES_FILE = "mafia_ck_4235.json"

def save_cookies_to_file(cookies_dict):
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies_dict, f, ensure_ascii=False, indent=2)

def load_cookies_from_file():
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def apply_cookies(cookies_list_or_dict):
    dash    = IVASMS_DASHBOARD
    session = dash['session']
    session.cookies.clear()
    print(f"[DEBUG] apply_cookies - نوع البيانات: {type(cookies_list_or_dict)}")
    if isinstance(cookies_list_or_dict, list):
        print(f"[DEBUG] عدد الكوكيز: {len(cookies_list_or_dict)}")
        for c in cookies_list_or_dict:
            name   = c['name']
            value  = c['value']
            domain = c.get('domain', 'www.ivasms.com').lstrip('.')
            print(f"[DEBUG] حط كوكي: {name} | domain={domain} | value={value[:20]}")
            session.cookies.set(name, value, domain=domain, path='/')
        save_cookies_to_file(cookies_list_or_dict)
        print(f"[DEBUG] تم حفظ الكوكيز في الملف ✅")
    else:
        print(f"[DEBUG] كوكيز dict: {list(cookies_list_or_dict.keys())}")
        for name, value in cookies_list_or_dict.items():
            session.cookies.set(name, value, domain='www.ivasms.com', path='/')
        save_cookies_to_file(cookies_list_or_dict)
    print(f"[DEBUG] الكوكيز في الـ session بعد apply:")
    for c in session.cookies:
        print(f"    {c.name} | domain={c.domain} | value={c.value[:20]}")
    dash['is_logged_in'] = False
    global _cookies_expired
    _cookies_expired = False
    print(f"[DEBUG] _cookies_expired = False ✅")
    threading.Thread(target=login_to_ivasms, daemon=True).start()
    return True


# ======================
# 🖥️ إعداد اللوحة الوحيدة (iVasms)
# ======================

IVASMS_DASHBOARD = {
    "name": "iVasms",
    "type": "ivasms",
    "login_url": "https://www.ivasms.com/login",
    "base_url": "https://www.ivasms.com",
    "sms_api_endpoint": "https://www.ivasms.com/portal/sms/received/getsms",
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
BOT_TOKEN = "8719786806:AAHwGHyhqN5dOHSQEoLb4jt-YTvHEs2YLuM"
CHAT_IDS = ["-1003789271722"]
REFRESH_INTERVAL = 3
TIMEOUT = 100
MAX_RETRIES = 5
RETRY_DELAY = 5

IDX_DATE = 0
IDX_NUMBER = 2
IDX_SMS = 5
SENT_MESSAGES_FILE = "sent_messages_bot1.json"

ADMIN_IDS = [6073745914, 6073745914]  
DB_PATH = "bot1.db"
FORCE_SUB_CHANNEL = None
FORCE_SUB_ENABLED = False
BOT_ACTIVE = True 

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN must be set in Secrets")
if not CHAT_IDS:
    raise SystemExit("❌ CHAT_IDS must be configured")

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
# 🧰 دوال قاعدة البيانات
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
    """, (user_id, username, first_name, last_name, country_code, assigned_number, user_id, private_combo_country))
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
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
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

def assign_numbers_to_user(user_id, numbers):
    """تخزين الأرقام كمصفوفة JSON"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (json.dumps(numbers), user_id))
    conn.commit()
    conn.close()

def get_user_by_number(number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number != ''")
    rows = c.fetchall()
    conn.close()
    
    for user_id, assigned_json in rows:
        try:
            numbers = json.loads(assigned_json)
            if isinstance(numbers, list) and number in numbers:
                return user_id
            elif isinstance(numbers, str) and number == numbers:
                return user_id
        except:
            if number == assigned_json:
                return user_id
    return None

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
    try:
        numbers_list = json.loads(old_number)
        if isinstance(numbers_list, list):
            for num in numbers_list:
                c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number LIKE ?", (f'%"{num}"%',))
        else:
            c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    except:
        c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

def get_otp_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM otp_logs")
    logs = c.fetchall()
    conn.close()
    return logs

def get_user_info(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

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
            print(f"Error checking {url}: {e}")
            continue
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

bot = telebot.TeleBot(BOT_TOKEN)

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

# ======================
# دعم الألوان للأزرار
# ======================
def color_button(text, callback_data, style="primary"):
    btn = types.InlineKeyboardButton(text, callback_data=callback_data)
    btn.style = style
    return btn

def color_url_button(text, url, style="primary"):
    btn = types.InlineKeyboardButton(text, url=url)
    btn.style = style
    return btn

# ======================
# 🏠 رسالة الترحيب
# ======================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if is_admin(user_id) and not IVASMS_DASHBOARD.get('is_logged_in', False):
        mar = types.InlineKeyboardMarkup(row_width=1)
        mar.add(
            color_button("💻 شرح جلب الكوكيز من PC", "cookies_guide_pc", "primary"),
            color_button("📱 شرح جلب الكوكيز من الفون", "cookies_guide_phone", "primary"),
            color_button("📤 ابعت الكوكيز الجديدة", "cookies_send", "danger")
        )
        bot.send_message(chat_id, "⚠️ <b>الكوكيز منتهية!</b>\n\nالبوت مش شغال دلوقتي.\nجدد الكوكيز عشان يكمل 👇", reply_markup=mar, parse_mode="HTML")
        return

    if not is_admin(user_id) and not IVASMS_DASHBOARD.get('is_logged_in', False):
        maintenance_caption = (
            "<b>❍─── <u> Taker2 OTP</u> ───❍</b>\n\n"
            "<b>⚠️ عذراً عزيزي المستخدم..</b>\n"
            "<b>البوت الآن في وضع الصيانة لتحديث الخدمات.</b>\n\n"
            "<b>⏳ يرجى المحاولة مرة أخرى لاحقاً.</b>\n"
            "<b>────────────────────</b>"
        )
        maintenance_photo = "https://i.ibb.co/2352v1FN/file-000000004f20720aaa70039fcd26faab-1.png"
        try:
            bot.send_photo(chat_id, maintenance_photo, caption=maintenance_caption, parse_mode="HTML")
        except Exception:
            bot.send_message(chat_id, maintenance_caption, parse_mode="HTML")
        return

    if is_maintenance_mode() and not is_admin(user_id):
        maintenance_caption = (
            "<b>❍─── <u> Taker2 OTP</u> ───❍</b>\n\n"
            "<b>⚠️ عذراً عزيزي المستخدم..</b>\n"
            "<b>البوت الآن في وضع الصيانة لتحديث الخدمات.</b>\n\n"
            "<b>⏳ يرجى المحاولة مرة أخرى لاحقاً.</b>\n"
            "<b>────────────────────</b>"
        )
        maintenance_photo = "https://i.ibb.co/2352v1FN/file-000000004f20720aaa70039fcd26faab-1.png"
        try:
            bot.send_photo(chat_id, maintenance_photo, caption=maintenance_caption, parse_mode="HTML")
        except:
            bot.send_message(chat_id, maintenance_caption, parse_mode="HTML")
        return

    if is_banned(user_id):
        bot.reply_to(message, "<b>🚫 عذراً، لقد تم حظرك من استخدام البوت.</b>", parse_mode="HTML")
        return

    if not force_sub_check(user_id):
        markup = force_sub_markup()
        if markup:
            bot.send_message(chat_id, "<b>🔒 يجب الاشتراك في القنوات لاستخدام البوت.</b>", parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, "<b>🔒 الاشتراك الإجباري مفعل لكن لم يتم تحديد قناة!</b>", parse_mode="HTML")
        return

    if not get_user(user_id):
        save_user(user_id, username=message.from_user.username or "", first_name=message.from_user.first_name or "", last_name=message.from_user.last_name or "")
        for admin in ADMIN_IDS:
            try:
                caption = f"🆕 <b>ضيف جديد نور بوتك :</b>\n<b>🆔:</b> <code>{user_id}</code>\n<b>👤:</b> @{safe_html(message.from_user.username or 'None')}\n<b>الاسم:</b> {safe_html(message.from_user.first_name or '')}"
                bot.send_message(admin, caption, parse_mode="HTML")
            except:
                pass
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    user_data = get_user(user_id)
    private_combo = user_data[7] if user_data else None
    all_combos = get_all_combos()

    country_combos = {}
    for country_code, combo_index in all_combos:
        if country_code not in country_combos:
            country_combos[country_code] = []
        country_combos[country_code].append(combo_index)

    if private_combo and private_combo in COUNTRY_CODES:
        name, flag, _ = COUNTRY_CODES[private_combo]
        buttons.append(color_button(f"{flag} {name} (Private)", f"country_{private_combo}_1", "success"))

    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES and country_code != private_combo:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                if len(indices) == 1:
                    btn_text = f"{flag} {name}"
                else:
                    btn_text = f"{flag} {name} ({idx})"
                buttons.append(color_button(btn_text, f"country_{country_code}_{idx}", "primary"))

    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    if is_admin(user_id):
        markup.add(color_button("🔐 Admin Panel", "admin_panel", "danger"))

    fancy_text = (
        "<b>❍<u> Taker2 OTP</u>❍</b>\n\n"
        "<b>🔋<u>★WELCOME MY FRIEND  TO THE BEST OTP  NUMBERS BOT ★</u></b>\n\n"
        "<b>🎓<u>𝒐𝒘𝒏𝒆𝒓</u> : <a href='tg://user?id=6073745914'>.⤹​𝗠𝗘𝗗𝗢 𝗕𝗘𝗡 𝗔𝗦𝗬𝗨𝗧⤾.</a></b>\n\n"
        "<b>────────────────────</b>\n"
        "<b><u>اخـتـر الــدولـة الـتـي تـريـدهـا مـن الـزر الاسـفـل</u> ⬇️</b>"
    )

    bot.send_message(chat_id, fancy_text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

# ======================
# معالج الاشتراك الإجباري
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if force_sub_check(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق! يمكنك استخدام البوت الآن.", show_alert=True)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ انت غير مشترك!", show_alert=True)

# ======================
# معالج اختيار الدولة (كل الأزرار تحت بعض)
# ======================
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
        bot.send_message(chat_id, "<b>🔒 اشترك في القنوات أولاً</b>", parse_mode="HTML", reply_markup=markup)
        return

    parts = call.data.split("_")
    country_code = parts[1]
    combo_index = int(parts[2]) if len(parts) > 2 else 1
    
    save_user(user_id, country_code=country_code)
    
    available_numbers = get_available_numbers(country_code, combo_index, user_id)
    
    if not available_numbers:
        error_msg = "<b>❌ نعتذر، جميع الأرقام قيد الاستخدام حالياً لهذه الدولة.</b>"
        markup = types.InlineKeyboardMarkup()
        markup.add(color_button("🔙 العودة لاختيار دولة أخرى", "back_to_countries", "primary"))
        bot.edit_message_text(error_msg, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        return

    # اختيار 3 أرقام عشوائية مختلفة
    if len(available_numbers) >= 3:
        assigned_numbers = random.sample(available_numbers, 3)
    else:
        assigned_numbers = available_numbers
    
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    
    assign_numbers_to_user(user_id, assigned_numbers)
    save_user(user_id, country_code=country_code, assigned_number=json.dumps(assigned_numbers))
    
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    
    numbers_text = ""
    for i, num in enumerate(assigned_numbers, 1):
        numbers_text += f"<b>📱 رقم {i}:</b> <code>+{num}</code>\n"
    
    msg_text = (
        f"<b>❍─── <u> Taker2 OTP</u> ───❍</b>\n\n"
        f"<b>🌍 الدولة:</b> {flag} {name}\n"
        f"<b>🔢 الكومبو:</b> #{combo_index}\n"
        f"<b>📊 عدد الأرقام المتاحة:</b> {len(assigned_numbers)}\n\n"
        f"{numbers_text}\n"
        f"<b>⏳ في انتظار وصول الـ OTP على أي من هذه الأرقام</b>\n\n"
        f"<b>────────────────────</b>"
    )

    # الأزرار تحت بعض (كل زر في سطر منفصل)
    markup = types.InlineKeyboardMarkup()
    markup.add(color_url_button("👥 Group OTP", "https://t.me/+Vkh68Z0Rz-wzMGNk", "success"))
    markup.add(color_url_button("📢 Bot Channel", "https://t.me/numhj", "primary"))
    markup.add(color_url_button("👑 Developer", "https://t.me/hackerTaker", "primary"))
    markup.add(color_button("🔄 تغيير الأرقام", f"change_num_{country_code}_{combo_index}", "primary"))
    markup.add(color_button("🔙 رجوع", "back_to_countries", "danger"))

    try:
        bot.edit_message_text(
            text=msg_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id, "✅ تم استلام الأرقام بنجاح")
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_num_"))
def change_number(call):
    user_id = call.from_user.id
    
    if is_banned(user_id):
        return
    if not force_sub_check(user_id):
        return
        
    parts = call.data.split("_")
    country_code = parts[2]
    combo_index = int(parts[3]) if len(parts) > 3 else 1
    
    available_numbers = get_available_numbers(country_code, combo_index, user_id)
    
    if len(available_numbers) < 3:
        bot.answer_callback_query(call.id, "❌ نعتذر، لا يوجد 3 أرقام متاحة حالياً.", show_alert=True)
        return

    assigned_numbers = random.sample(available_numbers, 3)
    
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])
        
    assign_numbers_to_user(user_id, assigned_numbers)
    save_user(user_id, assigned_number=json.dumps(assigned_numbers))
    
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    
    numbers_text = ""
    for i, num in enumerate(assigned_numbers, 1):
        numbers_text += f"<b>📱 رقم {i}:</b> <code>+{num}</code>\n"
    
    msg_text = (
        f"<b>❍─── <u> Taker2 OTP</u> ───❍</b>\n\n"
        f"<b>🌍 الدولة:</b> {flag} {name}\n"
        f"<b>🔢 الكومبو:</b> #{combo_index}\n"
        f"{numbers_text}\n"
        f"<b>⏳ في انتظار وصول الـ OTP على أي من هذه الأرقام</b>"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(color_url_button("👥 Group OTP", "https://t.me/+Vkh68Z0Rz-wzMGNk", "success"))
    markup.add(color_url_button("📢 Bot Channel", "https://t.me/numhj", "primary"))
    markup.add(color_url_button("👑 Developer", "https://t.me/hackerTaker", "primary"))
    markup.add(color_button("🔄 تغيير الأرقام", f"change_num_{country_code}_{combo_index}", "primary"))
    markup.add(color_button("🔙 رجوع", "back_to_countries", "danger"))

    try:
        bot.edit_message_text(
            text=msg_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id, "✅ تم تغيير الأرقام")
    except Exception as e:
        print(f"Error in change_number: {e}")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_countries")
def back_to_countries(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    user = get_user(call.from_user.id)
    private_combo = user[7] if user else None
    all_combos = get_all_combos()

    country_combos = {}
    for country_code, combo_index in all_combos:
        if country_code not in country_combos:
            country_combos[country_code] = []
        country_combos[country_code].append(combo_index)

    if private_combo and private_combo in COUNTRY_CODES:
        name, flag, _ = COUNTRY_CODES[private_combo]
        buttons.append(color_button(f"{flag} {name} (Private)", f"country_{private_combo}_1", "success"))

    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES and country_code != private_combo:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                if len(indices) == 1:
                    btn_text = f"{flag} {name}"
                else:
                    btn_text = f"{flag} {name} ({idx})"
                buttons.append(color_button(btn_text, f"country_{country_code}_{idx}", "primary"))

    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    if is_admin(call.from_user.id):
        markup.add(color_button("🔐 Admin Panel", "admin_panel", "danger"))

    fancy_text = (
        "<b>❍<u> Taker2 OTP</u>❍</b>\n\n"
        "<b>🔋<u>مـنـور بـوت ارقـام يـ صـديـقـي😁✌️</u></b>\n\n"
        "<b>🎓<u>𝒐𝒘𝒏𝒆𝒓</u> : <a href='tg://user?id=6073745914'>.⤹​𝗠𝗘𝗗𝗢 𝗕𝗘𝗡 𝗔𝗦𝗬𝗨𝗧⤾.</a></b>\n\n"
        "<b>────────────────────</b>\n"
        "<b><u>اخـتـر الــدولـة الـتـي تـريـدهـا مـن الـزر الاسـفـل</u> ⬇️</b>"
    )

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=fancy_text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Edit failed: {e}")
        bot.send_message(call.message.chat.id, fancy_text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
        bot.answer_callback_query(call.id)

# ======================
# 🔐 لوحة التحكم الإدارية
# ======================
user_states = {}

def admin_main_menu():
    markup = types.InlineKeyboardMarkup()
    
    status_icon = "🟢" if not is_maintenance_mode() else "🔴"
    status_text = "الآن: يعمل بنجاح" if not is_maintenance_mode() else "الآن: قيد الصيانة"
    markup.add(color_button(f"{status_icon} {status_text}", "toggle_maintenance", "primary"))
    
    markup.row(
        color_button("📥 إضافة كومبو", "admin_add_combo", "success"),
        color_button("🗑️ حذف كومبو", "admin_del_combo", "danger")
    )
    
    markup.row(
        color_button("📊 الإحصائيات", "admin_stats", "primary"),
        color_button("📄 تقرير شامل", "admin_full_report", "primary")
    )
    
    markup.row(
        color_button("📢 إذاعة عامة", "admin_broadcast_all", "success"),
        color_button("📨 إذاعة مخصصة", "admin_broadcast_user", "primary")
    )
    
    markup.row(
        color_button("🚫 حظر", "admin_ban", "danger"),
        color_button("✅ إلغاء حظر", "admin_unban", "success"),
        color_button("👤 معلومات", "admin_user_info", "primary")
    )
    
    markup.row(
        color_button("🔗 إشتراك", "admin_force_sub", "primary"),
        color_button("🖥️ اللوحات", "admin_dashboards", "primary"),
        color_button("🔑 برايفت", "admin_private_combo", "primary")
    )

    markup.add(color_button("🔙 مغادرة لوحة التحكم", "back_to_countries", "danger"))
    
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def show_admin_panel(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⚠️ عذراً، هذا القسم للمطورين فقط.", show_alert=True)
        return

    admin_text = (
        "<b>❍─── <u>Taker2 OTP</u> ───❍</b>\n\n"
        "<b>👋  مــــرحـــــبا بــــك أيـــــهــا الـــمـــطــــور فــي لوحــــة الــــتـــحــكــم.</b>\n\n" 
        "<b>⚙️ يمكنك التحكم في كامل وظائف البوت من هنا.</b>\n"
        "<b>⚠️ تنبيه: أي تغيير في الإعدادات يؤثر على المستخدمين فوراً.</b>\n\n"
        "<b>────────────────────</b>\n"
        "<b>إحصائيات سريعة:</b>\n"
        "<b>• حالة السيرفر: <u>Online</u> ✅</b>\n"
        f"<b>• الوقت الحالي: <u>{datetime.now().strftime('%H:%M')}</u></b>\n"
        "<b>────────────────────</b>"
    )
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=admin_text, parse_mode="HTML", reply_markup=admin_main_menu(), disable_web_page_preview=True)
    except Exception as e:
        print(f"Admin Panel Error: {e}")

# ======================
# إدارة الاشتراك الإجباري
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_force_sub")
def admin_force_sub(call):
    if not is_admin(call.from_user.id):
        return

    channels = get_all_force_sub_channels(enabled_only=False)
    text = "⚙️ إدارة قنوات الاشتراك الإجباري:\n"
    text += f"إجمالي القنوات: {len(channels)}\n"

    markup = types.InlineKeyboardMarkup()
    for ch_id, url, desc in channels:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT enabled FROM force_sub_channels WHERE id=?", (ch_id,))
        enabled = c.fetchone()[0]
        conn.close()
        status = "✅" if enabled else "❌"
        btn_text = f"{status} {desc or url[:25]}"
        markup.add(color_button(btn_text, f"edit_force_ch_{ch_id}", "primary"))

    markup.add(color_button("➕ إضافة قناة", "add_force_ch", "success"))
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ======================
# إدارة الكومبوهات (إضافة وحذف)
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_combo")
def admin_add_combo(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_combo_file"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(
            "📤 أرسل ملف الكومبو بصيغة TXT\n\n"
            "📌 الشكل الصحيح للملف:\n"
            "كل رقم في سطر منفصل\n\n"
            "مثال:\n"
            "584162105744\n"
            "584162206645\n"
            "584161959282",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except:
        bot.send_message(
            call.message.chat.id,
            "📤 أرسل ملف الكومبو بصيغة TXT\n\n"
            "📌 الشكل الصحيح للملف:\n"
            "كل رقم في سطر منفصل",
            reply_markup=markup
        )
    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=['document'])
def handle_combo_file(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ هذا الأمر للمطورين فقط")
        return
    
    if user_states.get(message.from_user.id) != "waiting_combo_file":
        bot.reply_to(message, "❌ من فضلك استخدم زر 'إضافة كومبو' أولاً")
        return
    
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        try:
            content = downloaded_file.decode('utf-8')
        except:
            content = downloaded_file.decode('latin-1')
        
        lines = []
        for line in content.splitlines():
            line = line.strip()
            if line:
                clean_line = re.sub(r'[^0-9]', '', line)
                if clean_line:
                    lines.append(clean_line)
        
        if len(lines) == 0:
            bot.reply_to(message, "❌ الملف فارغ أو لا يحتوي على أرقام صالحة!")
            return
        
        first_num = lines[0]
        country_code = None
        
        sorted_codes = sorted(COUNTRY_CODES.keys(), key=len, reverse=True)
        for code in sorted_codes:
            if first_num.startswith(code):
                country_code = code
                break
        
        if not country_code:
            bot.reply_to(
                message, 
                f"❌ لا يمكن تحديد الدولة من الرقم: {first_num}\n\n"
                f"تأكد أن الرقم يبدأ بكود الدولة الصحيح\n"
                f"مثال: 584162105744 (كود فنزويلا 58)"
            )
            return
        
        save_combo(country_code, lines)
        name, flag, _ = COUNTRY_CODES[country_code]
        
        sample = "\n".join([f"• {num}" for num in lines[:5]])
        if len(lines) > 5:
            sample += f"\n• ... و {len(lines) - 5} أرقام أخرى"
        
        bot.reply_to(
            message, 
            f"✅ <b>تم حفظ الكومبو بنجاح!</b>\n\n"
            f"🌍 <b>الدولة:</b> {flag} {name}\n"
            f"🔢 <b>كود الدولة:</b> +{country_code}\n"
            f"📊 <b>عدد الأرقام:</b> {len(lines)}\n\n"
            f"📋 <b>عينة من الأرقام:</b>\n{sample}\n\n"
            f"✨ يمكنك الآن استخدام /start لرؤية الدولة في القائمة",
            parse_mode="HTML"
        )
        
        del user_states[message.from_user.id]
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ أثناء معالجة الملف:\n{str(e)}")
        print(f"Error in handle_combo_file: {e}")
        traceback.print_exc()


@bot.callback_query_handler(func=lambda call: call.data == "admin_del_combo")
def admin_del_combo(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "📭 لا توجد كومبوهات لحذفها!", show_alert=True)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    country_combos = {}
    
    for country_code, combo_index in combos:
        if country_code not in country_combos:
            country_combos[country_code] = []
        country_combos[country_code].append(combo_index)
    
    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                if len(indices) == 1:
                    btn_text = f"🗑️ {flag} {name}"
                else:
                    btn_text = f"🗑️ {flag} {name} (كومبو {idx})"
                markup.add(color_button(btn_text, f"del_combo_{country_code}_{idx}", "danger"))
    
    markup.add(color_button("🔙 رجوع", "admin_panel", "primary"))
    
    try:
        bot.edit_message_text(
            "🗑️ <b>اختر الكومبو الذي تريد حذفه:</b>",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except:
        bot.send_message(
            call.message.chat.id,
            "🗑️ <b>اختر الكومبو الذي تريد حذفه:</b>",
            reply_markup=markup,
            parse_mode="HTML"
        )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("del_combo_"))
def confirm_del_combo(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    
    parts = call.data.split("_")
    country_code = parts[2]
    combo_index = int(parts[3]) if len(parts) > 3 else 1
    
    success = delete_combo(country_code, combo_index)
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    
    if success:
        bot.answer_callback_query(call.id, f"✅ تم حذف كومبو {flag} {name} بنجاح!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, f"❌ فشل حذف الكومبو!", show_alert=True)
    
    admin_del_combo(call)

# ======================
# دوال إضافية
# ======================

def get_available_numbers(country_code, combo_index=1, user_id=None):
    all_numbers = get_combo(country_code, combo_index, user_id)
    if not all_numbers:
        return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number != ''")
    used_numbers = set()
    for row in c.fetchall():
        try:
            nums = json.loads(row[0])
            if isinstance(nums, list):
                used_numbers.update(nums)
            else:
                used_numbers.add(row[0])
        except:
            used_numbers.add(row[0])
    conn.close()
    available = [num for num in all_numbers if num not in used_numbers]
    return available

def clean_html(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def clean_number(number):
    if not number:
        return ""
    return re.sub(r'\D', '', str(number))

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

def format_message(date_str, number, sms):
    country_name, country_flag, country_code = get_country_info(number)
    masked_num = mask_number(number)
    otp_code = extract_otp(sms)
    service = detect_service(sms)
    
    message = f"""✨ <b><u>OTP RECEIVED!</u></b> ✨

🌍 <b>Country:</b> {country_name} {country_flag}
⚙️ <b>Service:</b> {service}
📞 <b>Number:</b> {masked_num}
🕒 <b>Time:</b> {date_str}
🔐 <b>Code:</b> <code>{otp_code}</code>

📩 <b>Full Message:</b>
{safe_html(sms)}</b>

────────────────────</b>"""
    
    return message

def send_to_telegram_group(text, otp_code):
    success_count = 0
    try:
        keyboard = {
            "inline_keyboard": [
                [{"text": "🤖 دخول البوت", "url": f"https://t.me/{bot.get_me().username}"}],
                [{"text": "📢 قناة البوت", "url": "https://t.me/numhj"}],
                [{"text": "👑 المطور", "url": "https://t.me/hackerTaker"}]
            ]
        }
    except Exception as e:
        print(f"Keyboard error: {e}")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(keyboard)
            }
            resp = requests.post(url, data=payload, timeout=10)
            if resp.status_code == 200:
                success_count += 1
                msg_id = resp.json()["result"]["message_id"]
                threading.Thread(target=delete_message_after_delay, args=(chat_id, msg_id, 180), daemon=True).start()
        except Exception as e:
            print(f"Error: {e}")
    return success_count > 0

def delete_message_after_delay(chat_id, message_id, delay=300):
    time.sleep(delay)
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage", data={"chat_id": chat_id, "message_id": message_id})
    except Exception as e:
        print(f"Delete error: {e}")

def send_otp_to_user_and_group(date_str, number, sms):
    otp_code = extract_otp(sms)
    country_name, country_flag, country_code = get_country_info(number)
    service = detect_service(sms)
    user_id = get_user_by_number(number)
    log_otp(number, otp_code, sms, user_id)
    
    if user_id:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.row(
                color_url_button("𝑂𝑊𝑁𝐸𝑅⚙️", "https://t.me/numhj", "primary"),
                color_url_button("𓆩𝘽𝙤𝙩 𝘾𝙝𝙖𝙣𝙣𝙚𝙡𓆪", "https://t.me/numhj", "primary")
            )
            bot.send_message(
                user_id,
                f"""✨ <b><u> Taker2 OTP</u></b>\n
🌍 <b>Country:</b> {safe_html(country_name)} {country_flag}
⚙ <b>Service:</b> {safe_html(service)}
☎ <b>Number:</b> {safe_html(number)}
🕒 <b>Time:</b> {safe_html(date_str)}

🔐 <b>Code:</b> <code>{safe_html(otp_code)}</code>

📩 <b>Full Message:</b>
{safe_html(sms)}</b>""",
                reply_markup=markup,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error sending to user: {e}")
    
    text = format_message(date_str, number, sms)
    send_to_telegram_group(text, otp_code)

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def handle_copy_button(call):
    otp_code = call.data.split("_", 1)[1]
    bot.answer_callback_query(call.id, f"✅ تم نسخ الكود: {otp_code}", show_alert=True)

# ======================
# نظام الكوكيز المتكامل (أمر /cookies + شرح + استقبال)
# ======================

@bot.message_handler(commands=['cookies'])
def cmd_cookies(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    mar = types.InlineKeyboardMarkup(row_width=1)
    mar.add(
        types.InlineKeyboardButton("💻 شرح جلب الكوكيز من PC", callback_data="cookies_guide_pc"),
        types.InlineKeyboardButton("📱 شرح جلب الكوكيز من الفون", callback_data="cookies_guide_phone"),
        types.InlineKeyboardButton("📤 ابعت الكوكيز الجديدة", callback_data="cookies_send")
    )
    bot.reply_to(message,
        "🍪 <b>تحديث الكوكيز</b>\n\nاختر طريقة جلب الكوكيز حسب جهازك 👇",
        reply_markup=mar,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data in [
    "cookies_guide_pc", "cookies_guide_phone", "cookies_send", "cookies_main"
])
def cookies_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        return

    chat_id = call.message.chat.id
    msg_id  = call.message.message_id

    if call.data == "cookies_main":
        mar = types.InlineKeyboardMarkup(row_width=1)
        mar.add(
            types.InlineKeyboardButton("💻 شرح جلب الكوكيز من PC", callback_data="cookies_guide_pc"),
            types.InlineKeyboardButton("📱 شرح جلب الكوكيز من الفون", callback_data="cookies_guide_phone"),
            types.InlineKeyboardButton("📤 ابعت الكوكيز الجديدة", callback_data="cookies_send")
        )
        try:
            bot.edit_message_text(
                "🍪 <b>تحديث الكوكيز</b>\n\nاختر طريقة جلب الكوكيز حسب جهازك 👇",
                chat_id, msg_id, reply_markup=mar, parse_mode="HTML"
            )
        except Exception:
            bot.send_message(chat_id,
                "🍪 <b>تحديث الكوكيز</b>\n\nاختر طريقة جلب الكوكيز حسب جهازك 👇",
                reply_markup=mar, parse_mode="HTML"
            )

    elif call.data == "cookies_guide_pc":
        mar = types.InlineKeyboardMarkup(row_width=1)
        mar.add(
            types.InlineKeyboardButton("📤 ابعت الكوكيز دلوقتي", callback_data="cookies_send"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="cookies_main")
        )
        try:
            bot.edit_message_text(
                "💻 <b>جلب الكوكيز من PC أو لاب توب</b>\n\n"
                "1️⃣ افتح أي متصفح (Chrome / Firefox / Edge)\n\n"
                "2️⃣ افتح الموقع:\n"
                "<code>https://www.ivasms.com/login</code>\n\n"
                "3️⃣ سجل دخول بالإيميل والباسورد\n\n"
                "4️⃣ افتح متجر الإضافات وابحث عن:\n"
                "<code>Cookie-Editor</code> واضغط Add\n\n"
                "5️⃣ ارجع للموقع وافتح إضافة Cookie-Editor\n\n"
                "6️⃣ اضغط <b>Export</b> ← <b>Export as JSON</b>\n"
                "الكوكيز هتتنسخ تلقائياً\n\n"
                "7️⃣ ارجع للبوت واضغط الزرار 👇",
                chat_id, msg_id, reply_markup=mar, parse_mode="HTML"
            )
        except Exception:
            pass

    elif call.data == "cookies_guide_phone":
        mar = types.InlineKeyboardMarkup(row_width=1)
        mar.add(
            types.InlineKeyboardButton("📤 ابعت الكوكيز دلوقتي", callback_data="cookies_send"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="cookies_main")
        )
        try:
            bot.edit_message_text(
                "📱 <b>جلب الكوكيز من الفون (أندرويد) — شرح مفصل</b>\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "1️⃣ <b>تحميل Kiwi Browser</b>\n"
                "افتح Play Store وابحث عن:\n"
                "<code>Kiwi Browser</code>\n"
                "حمّله وافتحه ✅\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "2️⃣ <b>تثبيت إضافة Cookie-Editor</b>\n"
                "• في Kiwi اضغط على <b>⋮</b> (النقط التلاتة) فوق يمين\n"
                "• اضغط <b>Extensions</b>\n"
                "• اضغط <b>+ From store</b>\n"
                "• في مربع البحث اكتب: <code>Cookie-Editor</code>\n"
                "• اضغط على أول نتيجة (110,000+ مستخدم)\n"
                "• اضغط <b>Add to Kiwi</b> ✅\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "3️⃣ <b>فتح الموقع وتسجيل الدخول</b>\n"
                "• اضغط <b>⋮</b> ← <b>New Tab</b>\n"
                "• في شريط البحث اكتب:\n"
                "<code>www.ivasms.com/login</code>\n"
                "• سجل دخول بالإيميل والباسورد\n"
                "• تأكد إنك وصلت للـ Dashboard ✅\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "4️⃣ <b>فتح Cookie-Editor</b>\n"
                "• اضغط <b>⋮</b> فوق يمين\n"
                "• اضغط <b>Extensions</b>\n"
                "• اضغط على <b>Cookie-Editor</b>\n"
                "• هتشوف قائمة فيها كوكيز منها:\n"
                "  — <code>ivas_sms_session</code>\n"
                "  — <code>XSRF-TOKEN</code> ✅\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "5️⃣ <b>تصدير الكوكيز</b>\n"
                "• نزّل للأسفل في Cookie-Editor\n"
                "• اضغط <b>Export</b>\n"
                "• اضغط <b>Export as JSON</b>\n"
                "• انسخ كل النص اللي ظهر (اضغط مطولاً ← Select All ← Copy) ✅\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "6️⃣ <b>ابعت الكوكيز للبوت</b>\n"
                "ارجع هنا واضغط الزرار 👇",
                chat_id, msg_id, reply_markup=mar, parse_mode="HTML"
            )
        except Exception:
            pass

    elif call.data == "cookies_send":
        try:
            bot.edit_message_text(
                "📤 <b>ابعت الكوكيز دلوقتي</b>\n\n"
                "الصق الـ JSON اللي نسخته من Cookie-Editor هنا 👇",
                chat_id, msg_id,
                reply_markup=types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton("🔙 رجوع", callback_data="cookies_main")
                ]]),
                parse_mode="HTML"
            )
        except Exception:
            pass
        bot.register_next_step_handler(call.message, receive_new_cookies)

    bot.answer_callback_query(call.id)

def receive_new_cookies(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        cookies_data = json.loads(message.text)
        apply_cookies(cookies_data)
        def check_login():
            import time as _t
            _t.sleep(5)
            if IVASMS_DASHBOARD.get('is_logged_in', False):
                bot.send_message(message.chat.id, "✅ تم تحديث الكوكيز وتسجيل الدخول بنجاح!\nالبوت شغال دلوقتي 🟢")
            else:
                bot.send_message(message.chat.id, "⚠️ تم حفظ الكوكيز لكن فشل تسجيل الدخول، جرب مرة تانية.")
        bot.reply_to(message, "⏳ جاري التحقق من الكوكيز...")
        threading.Thread(target=check_login, daemon=True).start()
    except json.JSONDecodeError:
        bot.reply_to(message, "❌ الـ JSON غلط! تأكد إنك نسخت الكل صح.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

# ======================
# دوال iVasms
# ======================

def login_to_ivasms():
    global _cookies_alert_sent, _login_in_progress, _cookies_expired
    if _login_in_progress:
        return IVASMS_DASHBOARD.get('is_logged_in', False)
    if _cookies_expired:
        return False
    _login_in_progress = True
    try:
        dash = IVASMS_DASHBOARD
        session = dash["session"]
        saved = load_cookies_from_file()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        session.cookies.clear()
        default_cookies = [
            {"name": "_fbp", "value": "fb.1.1773603458145.356616031657165102", "domain": ".ivasms.com"},
            {"name": "XSRF-TOKEN", "value": "eyJpdiI6IjFCUG5nNnpjcWJhMkpuR0QvSFcvZlE9PSIsInZhbHVlIjoiUTFtR2NJQnBudGtxMkxQcWpNMXNaSHcySTYrVkZuQ25tVGJwMXpSVWNyOGE1OGM4ZDFjN2Q3MmQ3YmRmODA3NWUzNzM3NjkwZDQ5YzcwYzFjNmY5OGRlZmI1YzM2M2MzMmFmNDM2IiwidGFnIjoiIn0%3D", "domain": "www.ivasms.com"},
            {"name": "ivas_sms_session", "value": "eyJpdiI6IlZGdkdLZVkyYUlHUWp5NmZYWkVCa1E9PSIsInZhbHVlIjoiUUVLalNLbVJZDlhYWZkMGExOGY4NmU1NTcyNDUwYTRhNWM1NTNhZTM2MWZkYzdiYTdlYTg2NTYwYmQ4ZjkxYzRjNzY0ZTE1IiwidGFnIjoiIn0%3D", "domain": "www.ivasms.com"},
        ]
        cookies_to_use = saved if saved else default_cookies
        if isinstance(cookies_to_use, list):
            for c in cookies_to_use:
                domain = c.get('domain', 'www.ivasms.com').lstrip('.')
                session.cookies.set(c['name'], c['value'], domain=domain, path='/')
        else:
            for name, value in cookies_to_use.items():
                session.cookies.set(name, value, domain='www.ivasms.com', path='/')
        dashboard_resp = session.get("https://www.ivasms.com/portal/sms/received", timeout=30, allow_redirects=True)
        if "login" in dashboard_resp.url.lower():
            _cookies_expired = True
            mar = types.InlineKeyboardMarkup(row_width=1)
            mar.add(
                color_button("💻 شرح جلب الكوكيز من PC", "cookies_guide_pc", "primary"),
                color_button("📱 شرح جلب الكوكيز من الفون", "cookies_guide_phone", "primary"),
                color_button("📤 ابعت الكوكيز الجديدة", "cookies_send", "danger")
            )
            if not _cookies_alert_sent:
                _cookies_alert_sent = True
                def _send_alert():
                    for admin_id in ADMIN_IDS:
                        try:
                            bot.send_message(admin_id, "⚠️ <b>كوكيز iVasms انتهت!</b>\n\nالبوت وقف عن استقبال الرسائل.\nجدد الكوكيز عشان يكمل 👇", reply_markup=mar, parse_mode="HTML")
                        except Exception:
                            pass
                threading.Thread(target=_send_alert, daemon=True).start()
            return False
        soup = BeautifulSoup(dashboard_resp.text, 'html.parser')
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta:
            dash['csrf_token'] = csrf_meta.get('content')
        dash['is_logged_in'] = True
        dash['cookies'] = session.cookies.get_dict()
        _cookies_alert_sent = False
        return True
    except Exception as e:
        print(f"Login error: {e}")
        return False
    finally:
        _login_in_progress = False

def fetch_ivasms_messages():
    dash = IVASMS_DASHBOARD
    if not dash.get('is_logged_in', False):
        if not login_to_ivasms():
            return []
    try:
        session = dash['session']
        base_url = "https://www.ivasms.com"
        dashboard_page = session.get(f"{base_url}/portal/sms/received", timeout=30)
        soup_dash = BeautifulSoup(dashboard_page.text, 'html.parser')
        csrf_meta = soup_dash.find('meta', {'name': 'csrf-token'})
        csrf_token = csrf_meta.get('content') if csrf_meta else None
        if not csrf_token:
            token_input = soup_dash.find('input', {'name': '_token'})
            csrf_token = token_input['value'] if token_input else None
        if not csrf_token:
            dash['is_logged_in'] = False
            return []
        headers = {'Referer': f"{base_url}/portal/sms/received", 'X-Requested-With': 'XMLHttpRequest'}
        today = datetime.utcnow()
        start_date = (today - timedelta(days=3)).strftime('%m/%d/%Y')
        end_date = today.strftime('%m/%d/%Y')
        sms_api_url = f"{base_url}/portal/sms/received/getsms"
        summary_payload = {'from': start_date, 'to': end_date, '_token': csrf_token}
        summary_resp = session.post(sms_api_url, headers=headers, data=summary_payload, timeout=30)
        summary_resp.raise_for_status()
        summary_soup = BeautifulSoup(summary_resp.text, 'html.parser')
        country_groups = summary_soup.find_all('div', class_='rng')
        if not country_groups:
            country_groups = [el for el in summary_soup.find_all('div') if 'toggleRange' in el.get('onclick', '')]
        if not country_groups:
            dash['is_logged_in'] = False
            login_to_ivasms()
            return []
        group_ids = []
        for group in country_groups:
            onclick = group.get('onclick', '')
            match = re.search(r"toggleRange\('([^']+)'\s*,\s*'([^']+)'\)", onclick)
            if match:
                range_id = match.group(1).strip()
                safe_id = match.group(2).strip()
                if range_id not in [g[0] for g in group_ids]:
                    group_ids.append((range_id, safe_id))
        if not group_ids:
            return []
        all_messages = []
        numbers_url = f"{base_url}/portal/sms/received/getsms/number"
        sms_details_url = f"{base_url}/portal/sms/received/getsms/number/sms"
        for (range_id, safe_id) in group_ids:
            numbers_payload = {'start': start_date, 'end': end_date, 'range': range_id, '_token': csrf_token}
            numbers_resp = session.post(numbers_url, headers=headers, data=numbers_payload, timeout=30)
            numbers_soup = BeautifulSoup(numbers_resp.text, 'html.parser')
            phone_numbers = []
            for el in numbers_soup.find_all(['div', 'span', 'li', 'a', 'td']):
                onclick_val = el.get('onclick', '')
                if onclick_val:
                    nm = re.search(r"'(\d{7,})'", onclick_val)
                    if nm and nm.group(1) not in phone_numbers:
                        phone_numbers.append(nm.group(1))
                else:
                    txt = el.get_text(strip=True)
                    if re.fullmatch(r'\d{7,15}', txt) and txt not in phone_numbers:
                        phone_numbers.append(txt)
            if not phone_numbers:
                continue
            for phone in phone_numbers:
                sms_payload = {'start': start_date, 'end': end_date, 'Number': phone, 'Range': range_id, '_token': csrf_token}
                sms_resp = session.post(sms_details_url, headers=headers, data=sms_payload, timeout=30)
                sms_soup = BeautifulSoup(sms_resp.text, 'html.parser')
                rows = sms_soup.select('table tbody tr')
                for row in rows:
                    msg_div = row.find('div', class_='msg-text')
                    if not msg_div:
                        continue
                    sms_text = msg_div.get_text(separator=' ').strip()
                    if not sms_text:
                        continue
                    sender_tag = row.find('span', class_='cli-tag')
                    sender = sender_tag.get_text(strip=True) if sender_tag else 'Unknown'
                    message_id = f"{phone}-{sms_text[:50]}"
                    all_messages.append({'id': message_id, 'number': phone, 'text': sms_text, 'sender': sender, 'country': range_id, 'timestamp': datetime.utcnow().isoformat()})
        return all_messages
    except Exception as e:
        print(f"Fetch error: {e}")
        dash['is_logged_in'] = False
        return []

# ======================
# معالجات الأزرار الإدارية الناقصة (الإضافات الجديدة)
# ======================

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    users = get_all_users()
    combos = get_all_combos()
    logs = get_otp_logs()
    total_users = len(users)
    total_combos = len(combos)
    total_otps = len(logs)
    banned_users = 0
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE is_banned=1")
    banned_users = c.fetchone()[0]
    conn.close()
    text = (
        f"📊 <b>الإحصائيات العامة</b>\n\n"
        f"👥 <b>المستخدمين:</b> {total_users}\n"
        f"🚫 <b>المحظورين:</b> {banned_users}\n"
        f"📦 <b>الكومبوهات:</b> {total_combos}\n"
        f"📝 <b>سجلات OTP:</b> {total_otps}\n\n"
        f"🟢 <b>حالة البوت:</b> {'يعمل' if not is_maintenance_mode() else 'صيانة'}\n"
        f"🍪 <b>حالة الكوكيز:</b> {'صالحة ✅' if IVASMS_DASHBOARD.get('is_logged_in') else 'منتهية ❌'}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_full_report")
def admin_full_report(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    users = get_all_users()
    combos = get_all_combos()
    logs = get_otp_logs()[-50:]
    report = "📄 <b>تقرير شامل</b>\n\n"
    report += f"👥 <b>إجمالي المستخدمين:</b> {len(users)}\n"
    report += f"📦 <b>إجمالي الكومبوهات:</b> {len(combos)}\n"
    report += f"📝 <b>آخر 50 OTP:</b>\n"
    for log in logs[-10:]:
        report += f"• {log[3]} | {log[1]} | {log[2][:30]}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(report, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, report, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)

# متغيرات للإذاعة
broadcast_data = {}

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_all")
def admin_broadcast_all(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_broadcast_all"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(
            "📢 <b>إذاعة عامة لجميع المستخدمين</b>\n\nأرسل الرسالة التي تريد إذاعتها (نص أو صورة أو فيديو):",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد إذاعتها:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_user")
def admin_broadcast_user(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_broadcast_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(
            "📨 <b>إذاعة مخصصة لمستخدم معين</b>\n\nأرسل معرف المستخدم (user_id) أولاً:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "📨 أرسل معرف المستخدم أولاً:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_ban")
def admin_ban(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_ban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(
            "🚫 <b>حظر مستخدم</b>\n\nأرسل معرف المستخدم (user_id) لحظره:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "🚫 أرسل معرف المستخدم لحظره:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_unban")
def admin_unban(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_unban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(
            "✅ <b>إلغاء حظر مستخدم</b>\n\nأرسل معرف المستخدم (user_id) لإلغاء حظره:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "✅ أرسل معرف المستخدم لإلغاء حظره:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_user_info")
def admin_user_info(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_user_info"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(
            "👤 <b>معلومات مستخدم</b>\n\nأرسل معرف المستخدم (user_id) للحصول على معلوماته:",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "👤 أرسل معرف المستخدم للحصول على معلوماته:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_dashboards")
def admin_dashboards(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    text = "🖥️ <b>لوحة التحكم iVasms</b>\n\n"
    text += f"🔗 <b>الموقع:</b> {IVASMS_DASHBOARD['base_url']}\n"
    text += f"📧 <b>البريد:</b> {IVASMS_DASHBOARD['username']}\n"
    text += f"🍪 <b>حالة الكوكيز:</b> {'صالحة ✅' if IVASMS_DASHBOARD.get('is_logged_in') else 'منتهية ❌'}\n"
    text += f"🔄 <b>آخر فحص:</b> {IVASMS_DASHBOARD.get('last_check', 'لم يتم بعد')}\n\n"
    text += f"💡 <b>لتحديث الكوكيز استخدم الأمر:</b> /cookies"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_private_combo")
def admin_private_combo(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    text = "🔑 <b>إدارة الكومبوهات الخاصة</b>\n\n"
    text += "الكومبو الخاص هو كومبو يظهر لمستخدم معين فقط.\n\n"
    text += "<b>الأوامر المتاحة:</b>\n"
    text += "• <code>/set_private_combo [user_id] [country_code]</code> - تعيين كومبو خاص لمستخدم\n"
    text += "• <code>/remove_private_combo [user_id] [country_code]</code> - حذف كومبو خاص\n"
    text += "• <code>/upload_private_combo [user_id] [country_code]</code> - رفع ملف كومبو خاص\n\n"
    text += "مثال:\n"
    text += "<code>/set_private_combo 123456789 EG</code>"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_panel", "danger"))
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_maintenance")
def toggle_maintenance(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    global BOT_ACTIVE
    BOT_ACTIVE = not BOT_ACTIVE
    status = "🟢 يعمل بنجاح" if BOT_ACTIVE else "🔴 قيد الصيانة"
    bot.answer_callback_query(call.id, f"✅ تم تغيير حالة البوت إلى: {status}", show_alert=True)
    show_admin_panel(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_force_ch_"))
def edit_force_channel(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    channel_id = int(call.data.split("_")[-1])
    toggle_force_sub_channel(channel_id)
    bot.answer_callback_query(call.id, "✅ تم تغيير حالة القناة", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data == "add_force_ch")
def add_force_channel_start(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هذا الأمر للمطورين فقط", show_alert=True)
        return
    user_states[call.from_user.id] = "waiting_channel_url"
    markup = types.InlineKeyboardMarkup()
    markup.add(color_button("🔙 رجوع", "admin_force_sub", "danger"))
    try:
        bot.edit_message_text(
            "➕ <b>إضافة قناة جديدة</b>\n\n"
            "أرسل رابط القناة (مثال: @shhsnbdb أو https://t.me/shhsnbdb):",
            call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML"
        )
    except:
        bot.send_message(call.message.chat.id, "➕ أرسل رابط القناة:", reply_markup=markup)
    bot.answer_callback_query(call.id)

# ======================
# معالجات الرسائل النصية للأزرار الإدارية
# ======================

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_broadcast_all")
def handle_broadcast_all(message):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users()
    success = 0
    fail = 0
    bot.reply_to(message, f"⏳ جاري إذاعة الرسالة لـ {len(users)} مستخدم...")
    for user_id in users:
        try:
            if message.text:
                bot.send_message(user_id, message.text, parse_mode="HTML")
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption, parse_mode="HTML")
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=message.caption, parse_mode="HTML")
            elif message.document:
                bot.send_document(user_id, message.document.file_id, caption=message.caption, parse_mode="HTML")
            success += 1
        except:
            fail += 1
        time.sleep(0.05)
    bot.reply_to(message, f"✅ تم الإذاعة بنجاح!\nتم الإرسال: {success}\nفشل الإرسال: {fail}")
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_broadcast_user_id")
def handle_broadcast_user_id(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
        user_states[message.from_user.id] = "waiting_broadcast_msg"
        user_states[f"broadcast_target_{message.from_user.id}"] = target_id
        bot.reply_to(message, f"📨 تم تعيين المستخدم: {target_id}\n\nأرسل الرسالة الآن (نص أو صورة أو فيديو):")
    except:
        bot.reply_to(message, "❌ معرف المستخدم غير صالح! أرسل رقم صحيح.")
        del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_broadcast_msg")
def handle_broadcast_msg(message):
    if not is_admin(message.from_user.id):
        return
    target_id = user_states.get(f"broadcast_target_{message.from_user.id}")
    if not target_id:
        bot.reply_to(message, "❌ حدث خطأ، حاول مرة أخرى.")
        del user_states[message.from_user.id]
        return
    try:
        if message.text:
            bot.send_message(target_id, message.text, parse_mode="HTML")
        elif message.photo:
            bot.send_photo(target_id, message.photo[-1].file_id, caption=message.caption, parse_mode="HTML")
        elif message.video:
            bot.send_video(target_id, message.video.file_id, caption=message.caption, parse_mode="HTML")
        elif message.document:
            bot.send_document(target_id, message.document.file_id, caption=message.caption, parse_mode="HTML")
        bot.reply_to(message, f"✅ تم إرسال الرسالة للمستخدم {target_id} بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال: {str(e)}")
    del user_states[message.from_user.id]
    if f"broadcast_target_{message.from_user.id}" in user_states:
        del user_states[f"broadcast_target_{message.from_user.id}"]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_ban_user")
def handle_ban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
        ban_user(target_id)
        bot.reply_to(message, f"✅ تم حظر المستخدم {target_id} بنجاح!")
    except:
        bot.reply_to(message, "❌ معرف المستخدم غير صالح!")
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_unban_user")
def handle_unban_user(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
        unban_user(target_id)
        bot.reply_to(message, f"✅ تم إلغاء حظر المستخدم {target_id} بنجاح!")
    except:
        bot.reply_to(message, "❌ معرف المستخدم غير صالح!")
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_user_info")
def handle_user_info(message):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
        user = get_user_info(target_id)
        if user:
            text = f"👤 <b>معلومات المستخدم</b>\n\n"
            text += f"🆔 <b>المعرف:</b> <code>{user[0]}</code>\n"
            text += f"👤 <b>اليوزر:</b> @{user[1] if user[1] else 'None'}\n"
            text += f"📛 <b>الاسم:</b> {user[2] or ''} {user[3] or ''}\n"
            text += f"🌍 <b>الدولة:</b> {user[4] or 'غير محدد'}\n"
            text += f"📱 <b>الأرقام:</b> {user[5] or 'لا يوجد'}\n"
            text += f"🚫 <b>محظور:</b> {'نعم' if user[6] == 1 else 'لا'}\n"
            text += f"🔑 <b>كومبو خاص:</b> {user[7] or 'لا يوجد'}"
        else:
            text = f"❌ لا يوجد مستخدم بالمعرف {target_id}"
        bot.reply_to(message, text, parse_mode="HTML")
    except:
        bot.reply_to(message, "❌ معرف المستخدم غير صالح!")
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_channel_url")
def handle_channel_url(message):
    if not is_admin(message.from_user.id):
        return
    channel_url = message.text.strip()
    user_states[message.from_user.id] = "waiting_channel_desc"
    user_states[f"channel_url_{message.from_user.id}"] = channel_url
    bot.reply_to(message, "📝 أرسل وصف القناة (اختياري، أو اكتب 'تخطي'):")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_channel_desc")
def handle_channel_desc(message):
    if not is_admin(message.from_user.id):
        return
    channel_url = user_states.get(f"channel_url_{message.from_user.id}", "")
    desc = message.text.strip()
    if desc.lower() == "تخطي":
        desc = ""
    if add_force_sub_channel(channel_url, desc):
        bot.reply_to(message, "✅ تم إضافة القناة بنجاح!")
    else:
        bot.reply_to(message, "❌ القناة موجودة مسبقاً أو الرابط غير صالح")
    del user_states[message.from_user.id]
    if f"channel_url_{message.from_user.id}" in user_states:
        del user_states[f"channel_url_{message.from_user.id}"]

# ======================
# أوامر إضافية للمطور
# ======================

@bot.message_handler(commands=['set_private_combo'])
def set_private_combo(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "❌ الاستخدام: /set_private_combo [user_id] [country_code]\nمثال: /set_private_combo 123456789 EG")
        return
    try:
        user_id = int(parts[1])
        country_code = parts[2].upper()
        if country_code not in COUNTRY_CODES:
            bot.reply_to(message, f"❌ كود الدولة {country_code} غير صالح!")
            return
        save_user(user_id, private_combo_country=country_code)
        bot.reply_to(message, f"✅ تم تعيين كومبو خاص للمستخدم {user_id} للدولة {COUNTRY_CODES[country_code][1]} {COUNTRY_CODES[country_code][0]}")
    except:
        bot.reply_to(message, "❌ حدث خطأ، تأكد من صحة البيانات")

@bot.message_handler(commands=['remove_private_combo'])
def remove_private_combo(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ الاستخدام: /remove_private_combo [user_id]")
        return
    try:
        user_id = int(parts[1])
        save_user(user_id, private_combo_country=None)
        bot.reply_to(message, f"✅ تم إزالة الكومبو الخاص للمستخدم {user_id}")
    except:
        bot.reply_to(message, "❌ حدث خطأ")

def main_loop():
    global REFRESH_INTERVAL
    REFRESH_INTERVAL = 3
    DASHBOARDS = [IVASMS_DASHBOARD]
    SENT_MESSAGES_FILE = "mafia_sent_messages.json"
    sent_messages = {}
    try:
        if os.path.exists(SENT_MESSAGES_FILE):
            with open(SENT_MESSAGES_FILE, 'r') as f:
                data = json.load(f)
                sent_messages = {mid: "" for mid in data} if isinstance(data, list) else data
    except Exception as e:
        print(f"Error: {e}")
    print("=" * 60)
    print("🚀 بدء مراقبة لوحة iVasms (كل 3 ثوانٍ)")
    print("=" * 60)
    consecutive_errors = {dash["name"]: 0 for dash in DASHBOARDS}
    for dash in DASHBOARDS:
        if not dash.get('is_logged_in', False):
            success = login_to_ivasms()
            if not success:
                mar = types.InlineKeyboardMarkup(row_width=1)
                mar.add(
                    color_button("💻 شرح جلب الكوكيز من PC", "cookies_guide_pc", "primary"),
                    color_button("📱 شرح جلب الكوكيز من الفون", "cookies_guide_phone", "primary"),
                    color_button("📤 ابعت الكوكيز الجديدة", "cookies_send", "danger")
                )
                def _send_first_alert():
                    for admin_id in ADMIN_IDS:
                        try:
                            bot.send_message(admin_id, "👋 <b>أهلاً! البوت اشتغل للمرة الأولى أو الكوكيز منتهية</b>\n\n⚠️ محتاج تجيب الكوكيز الخاصة بحسابك على iVasms\nعشان البوت يبدأ يشتغل معاك.\n\nاختر طريقة جلب الكوكيز 👇", reply_markup=mar, parse_mode="HTML")
                        except Exception:
                            pass
                threading.Thread(target=_send_first_alert, daemon=True).start()
    while True:
        for dash in DASHBOARDS:
            try:
                messages = fetch_ivasms_messages()
                if messages:
                    new_messages = 0
                    for msg in messages:
                        msg_id = msg['id']
                        if msg_id not in sent_messages:
                            number = clean_number(msg['number'])
                            sms_text = msg['text']
                            date_str = msg['timestamp']
                            send_otp_to_user_and_group(date_str, number, sms_text)
                            sent_messages[msg_id] = datetime.utcnow().isoformat()
                            new_messages += 1
                    if new_messages > 0:
                        try:
                            with open(SENT_MESSAGES_FILE, 'w') as f:
                                json.dump(list(sent_messages)[-1000:], f)
                        except Exception as e:
                            print(f"Error: {e}")
                    consecutive_errors[dash["name"]] = 0
                else:
                    if not dash.get('is_logged_in', False) and not _login_in_progress and not _cookies_expired:
                        threading.Thread(target=login_to_ivasms, daemon=True).start()
                if len(sent_messages) > 2000:
                    sent_messages = dict(list(sent_messages.items())[-1000:])
            except Exception as e:
                consecutive_errors[dash["name"]] += 1
                if consecutive_errors[dash["name"]] >= 5:
                    dash['is_logged_in'] = False
                    if not _login_in_progress:
                        threading.Thread(target=login_to_ivasms, daemon=True).start()
                    consecutive_errors[dash["name"]] = 0
            time.sleep(REFRESH_INTERVAL)

def run_bot():
    print("[*] Starting bot...")
    while True:
        try:
            bot.polling(none_stop=False, timeout=30)
        except Exception as e:
            print(f"[!] Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=main_loop, daemon=True).start()
    run_bot()

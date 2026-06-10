# ==========================================
# 🚀 مطور البوت: ℎ𝑎𝑐𝑘𝑒𝑟 𝑇𝑎𝑘𝑒𝑟
# 📅 الإصدار: v70 - Sudan Secure Edition (Optimized)
# ==========================================

import time
import requests
import re
import os
import base64
from datetime import datetime
import sqlite3
import telebot
from telebot import types
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# إعدادات البوت الأساسية
BOT_TOKEN = os.getenv("BOT_TOKEN", "8886084382:AAEcFhXXRlypOcDFl19z-lGQLqxEq67Vejc")
CHAT_IDS = ["-1003908016285"]
ADMIN_IDS = [8728019066]
DB_PATH = "bot_ramos_live.db"
REFRESH_INTERVAL = 2

# فك تشفير المصادر
def _d(data): return base64.b64decode(data).decode('utf-8')
SITE_URL = _d("aHR0cHM6Ly9pbmZpbml0eS-zbXMudmVyY2VsLmFwcA==")
NUMBERS_URL = SITE_URL + _d("L251bWJlcnM=")
GET_BTN_TEXT = _d("R0VUIDMgTlVNQkVSUw==")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# 🗄️ إدارة قاعدة البيانات
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

# 🌐 دالة جلب الأرقام (مصححة)
def live_fetch_new_numbers(country_name):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    
    # تثبيت وتشغيل المتصفح تلقائياً
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(NUMBERS_URL)
        wait = WebDriverWait(driver, 20)
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{country_name}')]")))
        btn.click()
        time.sleep(2)
        sub_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{country_name} 1')]")))
        sub_btn.click()
        time.sleep(2)
        get_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{GET_BTN_TEXT}')]")))
        get_btn.click()
        time.sleep(5)
        matches = re.findall(r"(\d+INFINITY\d+|84\d{8,12}|263\d{8,12}|593\d{8,12}|49\d{8,12})", driver.page_source)
        return list(set(matches))
    except: return []
    finally: driver.quit()

# باقي الدوال (scrape_all_otps, live_otp_stream, etc) تبقى كما هي في ملفك...

if __name__ == "__main__":
    threading.Thread(target=live_otp_stream, daemon=True).start()
    print("Bot is running securely...")
    bot.polling(none_stop=True)

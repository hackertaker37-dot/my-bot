import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# إعدادات البوت
TOKEN = os.getenv("8886084382:AAEcFhXXRlypOcDFl19z-lGQLqxEq67Vejc")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# إعداد الربط مع Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# ملاحظة: تأكد أن ملف service_account.json موجود في نفس مجلد البوت
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("MyNumbersBot").sheet1 # استبدل MyNumbersBot باسم ملفك

# اللغات
LANGS = {
    "ar": {"get": "📱 جلب رقم", "add": "➕ إضافة رقم", "welcome": "أهلاً بك في نظام الأرقام!"},
    "en": {"get": "📱 Get Number", "add": "➕ Add Number", "welcome": "Welcome to Pro OTP System!"}
}

# كيبورد اللغات
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="العربية 🇸🇦"), KeyboardButton(text="English 🇺🇸")]], resize_keyboard=True)
    await message.answer("اختر لغتك / Choose your language:", reply_markup=kb)

# تفعيل الخدمة بعد اختيار اللغة
@dp.message(F.text.in_(["العربية 🇸🇦", "English 🇺🇸"]))
async def set_lang(message: types.Message):
    lang = "ar" if "العربية" in message.text else "en"
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=LANGS[lang]["get"]), KeyboardButton(text=LANGS[lang]["add"])]], resize_keyboard=True)
    await message.answer(LANGS[lang]["welcome"], reply_markup=kb)

# إضافة رقم لقاعدة البيانات
@dp.message(F.text.regexp(r'\d{10,}')) # أي رقم يتكون من 10 خانات فأكثر
async def save_number(message: types.Message):
    sheet.append_row([message.text, "Available", "None"])
    await message.answer(f"✅ تم إضافة الرقم {message.text} بنجاح إلى قاعدة البيانات.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

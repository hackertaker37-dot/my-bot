import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. الإعدادات
TOKEN = os.getenv("8886084382:AAEcFhXXRlypOcDFl19z-lGQLqxEq67Vejc")
CHANNEL_ID = "-1003908016285"  # ضع هنا معرف قناتك
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. الربط بـ Google Sheets (قاعدة بياناتك)
# تأكد من رفع ملف service_account.json في نفس المجلد
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("MyNumbersBot").sheet1 

# 3. نظام اللغات (موسوعة البوت)
LANGS = {
    "ar": {"get": "📱 جلب رقم", "add": "➕ إضافة رقم", "welcome": "أهلاً بك في نظام الأرقام! اشترك في القناة.", "status": "✅ تم الحفظ."},
    "en": {"get": "📱 Get Number", "add": "➕ Add Number", "welcome": "Welcome! Please join our channel.", "status": "✅ Saved."}
}

# 4. التحقق من الاشتراك (نظام القناة الإجباري)
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except: return False

# 5. منطق الأوامر
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="العربية 🇸🇦"), KeyboardButton(text="English 🇺🇸")]], resize_keyboard=True)
    await message.answer("اختر اللغة / Choose language:", reply_markup=kb)

@dp.message(F.text.in_(["العربية 🇸🇦", "English 🇺🇸"]))
async def set_lang(message: types.Message):
    lang = "ar" if "العربية" in message.text else "en"
    if await check_sub(message.from_user.id):
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=LANGS[lang]["get"]), KeyboardButton(text=LANGS[lang]["add"])]], resize_keyboard=True)
        await message.answer(LANGS[lang]["welcome"], reply_markup=kb)
    else:
        await message.answer(f"يرجى الاشتراك في القناة أولاً: {CHANNEL_ID}")

@dp.message(F.text.regexp(r'\d{9,}'))
async def add_number(message: types.Message):
    sheet.append_row([message.text, "Available", "User"])
    await message.answer("✅ تم تسجيل الرقم في النظام بنجاح.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

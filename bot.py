import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("8886084382:AAH3-CYsadKsXuaLuCmupzjiIwGkE2U8RrM")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# رابط الموقع الخاص بك
API_URL = "https://yourwebsite.com/api/add" 

# دالة إرسال الرقم للموقع
async def send_to_website(number):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json={"number": number}) as resp:
            return resp.status == 200

# --- الأزرار ---
def get_full_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 جلب البيانات", callback_data="fetch")],
        [InlineKeyboardButton(text="➕ إضافة رقم للموقع", callback_data="add_to_site")],
        [InlineKeyboardButton(text="⚙️ إعدادات الربط", callback_data="settings")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك، تم ربط البوت بموقعك بنجاح! اختر إجراءً:", reply_markup=get_full_menu())

# التعامل مع إضافة رقم
@dp.callback_query(F.data == "add_to_site")
async def ask_for_number(callback: types.CallbackQuery):
    await callback.message.answer("أرسل الرقم الآن وسأقوم برفعه للموقع فوراً:")
    await callback.answer()

@dp.message(F.text.isdigit())
async def process_number(message: types.Message):
    await message.answer(f"جاري رفع الرقم {message.text} إلى قاعدة بيانات موقعك... 🔄")
    success = await send_to_website(message.text)
    if success:
        await message.answer("✅ تم إضافة الرقم بنجاح إلى الموقع!")
    else:
        await message.answer("❌ حدث خطأ في الاتصال بالموقع، تأكد من الرابط.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

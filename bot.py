import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# --- 1. الإعدادات ---
TOKEN = "توكن_البوت"
ADMIN_ID = 123456789  # ضع معرفك هنا
bot = Bot(token=TOKEN)
dp = Dispatcher()
engine = create_async_engine("sqlite+aiosqlite:///service_bot.db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

# --- 2. الإعلان (Broadcast) الاحترافي ---
@dp.message(Command("broadcast"))
async def broadcast_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("⚠️ أرسل الأمر مع نص الإعلان: /broadcast [النص]")
        return
    
    # قائمة المستخدمين (يتم استخراجها من قاعدة البيانات فعلياً)
    # هنا مثال لقائمة ثابتة
    users = [ADMIN_ID] 
    
    await message.answer("🚀 بدأ الإرسال...")
    for user_id in users:
        try:
            await bot.send_message(user_id, text)
            await asyncio.sleep(0.05) 
        except TelegramForbiddenError:
            continue
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            
    await message.answer("✅ تم انتهاء الإرسال.")

# --- 3. الواجهة والأزرار ---
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="احصل على رقم 📲")],
        [types.KeyboardButton(text="الرصيد 💰")]
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("مرحباً بك في نظام التفعيل الرقمي!", reply_markup=markup)

@dp.message(F.text == "احصل على رقم 📲")
async def get_number(message: types.Message):
    await message.answer("جاري البحث عن رقم متاح في المخزون...")

# --- 4. تشغيل البوت ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

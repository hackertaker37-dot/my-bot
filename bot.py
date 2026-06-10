import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# التوكن الذي أرسلته (احرص على تغييره فوراً!)
TOKEN = "8886084382:AAEcFhXXRlypOcDFl19z-lGQLqxEq67Vejc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- القائمة الشاملة ---
def get_full_menu():
    buttons = [
        [InlineKeyboardButton(text="📱 جلب البيانات", callback_data="fetch")],
        [InlineKeyboardButton(text="➕ إضافة رقم للموقع", callback_data="add_to_site")],
        [InlineKeyboardButton(text="⚙️ إعدادات", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك! أنا بوتك الرسمي. اختر خدمة:", reply_markup=get_full_menu())

@dp.callback_query(F.data == "fetch")
async def fetch_data(callback: types.CallbackQuery):
    await callback.message.answer("جاري جلب البيانات من الموقع... 🔄")
    await callback.answer()

@dp.callback_query(F.data == "add_to_site")
async def add_number(callback: types.CallbackQuery):
    await callback.message.answer("أرسل الرقم الآن لإضافته للموقع:")
    await callback.answer()

async def main():
    print("البوت يعمل الآن...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

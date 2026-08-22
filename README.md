import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Logging sozlamasi
logging.basicConfig(level=logging.INFO)

# Telegram Bot Tokeningiz
BOT_TOKEN = os.getenv("BOT_TOKEN", "8978186820:AAEcIWEcBdr_U5BCzFj8KM_dMy20j5KeXc")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ro'yxatdan o'tish bosqichlari (FSM)
class PlatonRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_level = State()

# --- TUGMALAR (KEYBOARDS) ---

def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📝 Ingliz tili kursiga ro'yxatdan o'tish")],
            [types.KeyboardButton(text="🇬🇧 Platon School haqida"), types.KeyboardButton(text="📞 Aloqa va Manzil")]
        ],
        resize_keyboard=True
    )

def get_phone_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
            [types.KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

def get_english_levels_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🟢 General English (Noldan)"), types.KeyboardButton(text="🟡 CEFR tayyorlov")],
            [types.KeyboardButton(text="🔴 IELTS tayyorlov"), types.KeyboardButton(text="👶 Kids English")],
            [types.KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )

# --- BUYRUQLAR VA ASOSIY MENYU ---

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        f"🇬🇧 <b>Platon School - Ingliz tili maktabi</b> rasmiy botiga xush kelibsiz!\n\n"
        f"Ingliz tilini professional darajada o'rganish va darslarga yozilish uchun quyidagi menyudan foydalaning."
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard())

@dp.message(Command("cancel"))
@dp.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Jarayon bekor qilindi. Bosh menyudasiz.", reply_markup=get_main_keyboard())

@dp.message(F.text == "🇬🇧 Platon School haqida")
async def about_handler(message: types.Message):
    about_text = (
        "🇬🇧 <b>Platon English School</b>\n\n"
        "✨ <b>Nima uchun aynan biz?</b>\n"
        "• Tajribali va IELTS 8.0+ sertifikatli ustozlar\n"
        "• Interaktiv va zamonaviy Speaking klublar\n"
        "• Noldan mukammal darajagacha o'rgatish tizimi\n"
        "• IELTS va CEFR imtihonlariga kafolatli tayyorlov\n\n"
        "🎓 Kelajagingizni biz bilan birga quring!"
    )
    await message.answer(about_text, parse_mode="HTML")

@dp.message(F.text == "📞 Aloqa va Manzil")
async def contact_handler(message: types.Message):
    contact_text = (
        "📞 <b>Platon School bilan bog'lanish:</b>\n\n"
        "☎️ <b>Telefon:</b> +998 90 123 45 67\n"
        "📍 <b>Manzil:</b> Toshkent shahri, Yunusobod tumani\n"
        "🌐 <b>Telegram admin:</b> @platon_english_admin\n"
        "⏰ <b>Ish vaqti:</b> 09:00 - 18:00 (Dushanba - Shanba)"
    )
    await message.answer(contact_text, parse_mode="HTML")

# --- RO'YXATDAN O'TISH TIZIMI ---

@dp.message(F.text == "📝 Ingliz tili kursiga ro'yxatdan o'tish")
async def start_registration(message: types.Message, state: FSMContext):
    await state.set_state(PlatonRegistration.waiting_for_name)
    await message.answer("To'liq <b>ism va familiyangizni</b> kiriting:\n\n<i>(Masalan: Jasur Rahimov)</i>", parse_mode="HTML", reply_markup=get_cancel_keyboard())

@dp.message(PlatonRegistration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(PlatonRegistration.waiting_for_phone)
    await message.answer("Siz bilan bog'lanishimiz uchun <b>telefon raqamingizni</b> yuboring:", parse_mode="HTML", reply_markup=get_phone_keyboard())

@dp.message(PlatonRegistration.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone_number=phone)
    await state.set_state(PlatonRegistration.waiting_for_level)
    await message.answer("Qaysi <b>yo'nalish/daraja</b> bo'yicha ta'lim olmoqchisiz?", parse_mode="HTML", reply_markup=get_english_levels_keyboard())

@dp.message(PlatonRegistration.waiting_for_level)
async def process_level(message: types.Message, state: FSMContext):
    await state.update_data(level=message.text)
    user_data = await state.get_data()
    
    summary_text = (
        "🎉 <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"👤 <b>O'quvchi:</b> {user_data['full_name']}\n"
        f"📞 <b>Telefon:</b> {user_data['phone_number']}\n"
        f"📚 <b>Tanlangan kurs:</b> {user_data['level']}\n\n"
        "🏛 <b>Platon School</b> administratorlari tez orada siz bilan bog'lanib, bepul sinov darsiga taklif qilishadi!"
    )
    
    await message.answer(summary_text, parse_mode="HTML", reply_markup=get_main_keyboard())
    await state.clear()

# --- BOTNI ISHGA TUSHIRISH ---

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

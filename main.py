import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

BOT_TOKEN = "8723785529:AAfTFTP30fklzQ_2_HeaSXnh7HZ5ZlnjyZ0"
ADMIN_GROUP_ID = -5313635885  

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Registration(StatesGroup):
    name = State()
    phone = State()
    category = State()
    course = State()

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

categories_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📐 Matematika"), KeyboardButton(text="🇬🇧 Ingliz tili")]
    ],
    resize_keyboard=True
)

math_courses_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Matematika: Maktab kursi (5-9 sinf)")],
        [KeyboardButton(text="Matematika: DTM / OTMga tayyorgarlik")],
        [KeyboardButton(text="Matematika: Mantiq va Olimpiada")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)

english_courses_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ingliz tili: General English (A1-B2)")],
        [KeyboardButton(text="Ingliz tili: IELTS tayyorlov")],
        [KeyboardButton(text="Ingliz tili: CEFR tayyorlov")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)

# Start komandasi
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        f"Salom, {message.from_user.first_name}!\nO'quv markazimizga xush kelibsiz.\n\nRo'yxatdan o'tish uchun **Ism va Familiyangizni** kiriting:"
    )
    await state.set_state(Registration.name)

# Kategoriyalarni alohida ko'rish buyrug'i
@dp.message(Command("categories"))
@dp.message(F.text == "📂 Kategoriyalarni ko me'morchiligi")
async def show_categories(message: types.Message, state: FSMContext):
    await message.answer("Mavjud kategoriyalarimiz:", reply_markup=categories_keyboard)
    await state.set_state(Registration.category)

# 1-qadam: Ism
@dp.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        "Ajoyib! Endi **telefon raqamingizni** yuboring yoki quyidagi tugmani bosing:",
        reply_markup=phone_keyboard
    )
    await state.set_state(Registration.phone)

# 2-qadam: Telefon
@dp.message(Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone_number)
    
    await message.answer(
        "Qaysi **kategoriya** bo'yicha tahsil olmoqchisiz?",
        reply_markup=categories_keyboard
    )
    await state.set_state(Registration.category)

# 3-qadam: Kategoriya tanlash
@dp.message(Registration.category)
async def process_category(message: types.Message, state: FSMContext):
    category = message.text
    if "Matematika" in category:
        await state.update_data(category="Matematika")
        await message.answer("Matematika yo'nalishi bo'yicha kursni tanlang:", reply_markup=math_courses_keyboard)
        await state.set_state(Registration.course)
    elif "Ingliz tili" in category:
        await state.update_data(category="Ingliz tili")
        await message.answer("Ingliz tili yo'nalishi bo'yicha kursni tanlang:", reply_markup=english_courses_keyboard)
        await state.set_state(Registration.course)
    else:
        await message.answer("Iltimos, kategoriyalardan birini tanlang:", reply_markup=categories_keyboard)

# 4-qadam: Kursni tanlash va Admin guruhiga ma'lumot yuborish
@dp.message(Registration.course)
async def process_course(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Orqaga", "Orqaga", "orqaga"]:
        await message.answer("Kategoriyani qayta tanlang:", reply_markup=categories_keyboard)
        await state.set_state(Registration.category)
        return

    await state.update_data(course=message.text)
    data = await state.get_data()

    user_text = (
        "✅ **Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!**\n\n"
        f"👤 **Ism-familiya:** {data.get('full_name', 'Kiritilmagan')}\n"
        f"📞 **Telefon:** {data.get('phone', 'Kiritilmagan')}\n"
        f"📂 **Kategoriya:** {data['category']}\n"
        f"📚 **Kurs:** {data['course']}\n\n"
        "Tez orada menejerlarimiz siz bilan bog'lanishadi!"
    )
    await message.answer(user_text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")

    admin_text = (
        "📥 **YANGI ARIZA TUSHDI!**\n\n"
        f"👤 **O'quvchi:** {data.get('full_name', 'Kiritilmagan')}\n"
        f"📞 **Tel:** `{data.get('phone', 'Kiritilmagan')}`\n"
        f"📂 **Yo'nalish:** {data['category']}\n"
        f"📚 **Kurs:** {data['course']}\n"
        f"🔗 **User:** @{message.from_user.username if message.from_user.username else 'Mavjud emas'}\n"
        f"🆔 **Telegram ID:** `{message.from_user.id}`"
    )

    try:
        await bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Admin guruhiga xabar yuborishda xatolik: {e}")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

from config import (
    ADMIN_GROUP_ID,
    CLINIC_NAME,
    CLINIC_PHONE,
    CLINIC_ADDRESS,
    CLINIC_LOCATION_LAT,
    CLINIC_LOCATION_LON,
    SERVICES_AND_PRICES
)
from keyboards import main_menu, phone_keyboard, cancel_keyboard, quick_book_inline
from ai_assistant import ask_gemini

router = Router()

# Qabulga yozilish FSM holatlari
class BookingState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()


# /start buyrug'i (Instagramdan start=insta orqali kelganlarni ham aniqlaydi)
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    
    source_text = ""
    if command.args == "insta":
        source_text = "\n\n📸 *Instagram sahifamizdan xush kelibsiz!*"
    
    welcome_text = (
        f"🏥 *{CLINIC_NAME}* rasmiy botiga xush kelibsiz!{source_text}\n\n"
        "Bu yerda siz klinikamiz xizmatlari va narxlari bilan tanishishingiz, "
        "shuningdek, qabulga onlayn yozilishingiz mumkin.\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇"
    )
    
    await message.answer(welcome_text, reply_markup=main_menu, parse_mode="Markdown")


# Bekor qilish tugmasi
@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Jarayon bekor qilindi. Asosiy menyudasiz 👇", reply_markup=main_menu)


# 💰 Narxlar bo'limi
@router.message(F.text == "💰 Narxlar")
async def show_prices(message: Message):
    text = f"💰 *{CLINIC_NAME} xizmatlari narxlari:*\n\n"
    for item in SERVICES_AND_PRICES:
        text += f"• *{item['name']}*: {item['price']}\n"
    
    text += "\nQabulga yozilish uchun quyidagi tugmani bosing 👇"
    await message.answer(text, reply_markup=quick_book_inline, parse_mode="Markdown")


# 👨‍⚕️ Xizmatlar / Shifokorlar bo'limi
@router.message(F.text == "👨‍⚕️ Xizmatlar / Shifokorlar")
async def show_services(message: Message):
    text = (
        f"🏥 *{CLINIC_NAME} quyidagi yo'nalishlar bo'yicha xizmat ko'rsatadi:*\n\n"
        "🔹 Terapiya va umumiy amaliyot\n"
        "🔹 Stomatologiya (terapiya, jarrohlik, ortodontiya)\n"
        "🔹 Nevrologiya va reabilitatsiya\n"
        "🔹 Kardiologiya va EKG tekshiruvi\n"
        "🔹 Zamonaviy raqamli UZI tekshiruvi\n"
        "🔹 Tezkor laboratoriya tahlillari\n\n"
        "Mutaxassis qabuliga oldindan yozilish tavsiya etiladi 👇"
    )
    await message.answer(text, reply_markup=quick_book_inline, parse_mode="Markdown")


# 📍 Manzil va Aloqa
@router.message(F.text == "📍 Manzil va Aloqa")
async def show_location(message: Message):
    text = (
        f"📍 *Bizning manzil:*\n{CLINIC_ADDRESS}\n\n"
        f"📞 *Telefon raqam:* {CLINIC_PHONE}\n"
        f"⏰ *Ish vaqti:* Dushanba - Shanba: 08:30 dan 18:00 gacha\n"
        "Yakshanba: Dam olish kuni"
    )
    await message.answer(text, parse_mode="Markdown")
    # Lokatsiya yuborish
    try:
        await message.answer_location(latitude=CLINIC_LOCATION_LAT, longitude=CLINIC_LOCATION_LON)
    except Exception:
        pass


# 📝 Qabulga yozilish jarayonini boshlash
@router.message(F.text == "📝 Qabulga yozilish")
async def start_booking(message: Message, state: FSMContext):
    await state.set_state(BookingState.waiting_for_name)
    await message.answer(
        "Iltimos, ism va familiyangizni kiriting:",
        reply_markup=cancel_keyboard
    )


# Inline tugma orqali qabulga yozilish bosilganda
@router.callback_query(F.data == "book_appointment")
async def inline_book_appointment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BookingState.waiting_for_name)
    await callback.message.answer(
        "Iltimos, ism va familiyangizni kiriting:",
        reply_markup=cancel_keyboard
    )


# 1-Qadam: Ismni qabul qilish va telefon raqam so'rash
@router.message(BookingState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Iltimos, to'liq ismingizni kiriting:")
        return

    await state.update_data(name=name)
    await state.set_state(BookingState.waiting_for_phone)
    await message.answer(
        f"Rahmat, {name}!\n\n"
        "Endi operatorlarimiz siz bilan bog'lanishi uchun "
        "quyidagi tugmani bosib telefon raqamingizni yuboring yoki qo'lda kiriting (+998901234567):",
        reply_markup=phone_keyboard
    )


# 2-Qadam: Telefon raqamni qabul qilish (Kontakt tugmasi orqali)
@router.message(BookingState.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, bot: Bot):
    phone_number = message.contact.phone_number
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    await finalize_booking(message, state, bot, phone_number)


# 2-Qadam: Telefon raqamni qabul qilish (Qo'lda yozilganda)
@router.message(BookingState.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, bot: Bot):
    phone_number = message.text.strip()
    # Raqamni oddiy tekshirish
    if len(phone_number) < 7:
        await message.answer("Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567):")
        return
    await finalize_booking(message, state, bot, phone_number)


# Yakuniy qadam: Ariza ma'lumotlarini saqlash va Admin guruhga yuborish
async def finalize_booking(message: Message, state: FSMContext, bot: Bot, phone_number: str):
    data = await state.get_data()
    user_name = data.get("name", "Noma'lum")
    user = message.from_user
    username_text = f"@{user.username}" if user.username else "Mavjud emas"

    # Mijozga tasdiq xabari
    await message.answer(
        "✅ *Arizangiz qabul qilindi!*\n\n"
        "Tez orada klinika ma'murlari siz bilan bog'lanib, "
        "qabul vaqtini tasdiqlashadi. Salomat bo'ling!",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )
    await state.clear()

    # Admin guruhga bildirishnoma tayyorlash
    admin_notification = (
        "🔔 *YANGI ARIZA / QABULGA YOZILISH!*\n"
        "────────────────────\n"
        f"👤 *F.I.O:* {user_name}\n"
        f"📞 *Telefon:* `{phone_number}`\n"
        f"💬 *Telegram:* {username_text} (ID: `{user.id}`)\n"
        "────────────────────\n"
        "📌 *Holat:* Operator bog'lanishi kutilmoqda."
    )

    # Admin guruhga yuborish
    if ADMIN_GROUP_ID:
        try:
            await bot.send_message(
                chat_id=ADMIN_GROUP_ID,
                text=admin_notification,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"[XATO] Admin guruhga xabar yuborishda xatolik: {e}")


# 🤖 Foydalanuvchining barcha erkin savollariga Gemini AI orqali aqlli javob qaytarish
@router.message(F.text)
async def ai_consultant_handler(message: Message, bot: Bot):
    # Foydalanuvchiga yozish jarayoni ko'rinishi uchun (typing indicator)
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    except Exception:
        pass

    user_query = message.text.strip()
    ai_response = await ask_gemini(user_query, user_id=message.from_user.id)

    try:
        await message.answer(
            ai_response,
            reply_markup=quick_book_inline,
            parse_mode=None
        )
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        await message.answer(
            ai_response,
            reply_markup=quick_book_inline,
            parse_mode=None
        )

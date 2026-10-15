import os
import re
import json
import time
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

from config import (
    ADMIN_ID,
    ADMIN_GROUP_ID,
    CLINIC_NAME,
    CLINIC_LEGAL_NAME,
    CLINIC_PHONE,
    CLINIC_PHONES_LIST,
    CLINIC_ADDRESS,
    CLINIC_LOCATION_LAT,
    CLINIC_LOCATION_LON,
    SERVICES_AND_PRICES,
    get_owner_ids,
    save_owner_id
)
from keyboards import main_menu, phone_keyboard, cancel_keyboard, quick_book_inline
from ai_assistant import ask_gemini

router = Router()

# Qabulga yozilish FSM holatlari (Ism -> Telefon -> Bo'sh vaqti)
class BookingState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_time = State()


# /start buyrug'i (Instagramdan start=insta orqali kelganlarni ham aniqlaydi)
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    
    user = message.from_user
    logger.info(
        f"🟢 /start: ID={user.id}, Ism={user.full_name}, Username=@{user.username}, Manba={command.args or 'telegram'}"
    )
    
    source_text = ""
    if command.args == "insta":
        source_text = "\n\n📸 *Instagram sahifamizdan xush kelibsiz!*"
    
    welcome_text = (
        f"🏥 *«{CLINIC_NAME}»* rasmiy botiga xush kelibsiz!{source_text}\n"
        f"_({CLINIC_LEGAL_NAME})_\n\n"
        "Markazimiz qand kasalligini (qandli diabetni) samarali davolash va nazorat qilishga ixtisoslashgan.\n\n"
        "Bu yerda siz davolash kursi, narxlar va manzilimiz bilan tanishishingiz, "
        "shuningdek, qabulga onlayn yozilishingiz mumkin.\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇"
    )
    
    await message.answer(welcome_text, reply_markup=main_menu, parse_mode="Markdown")


# Bekor qilish tugmasi
@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Jarayon bekor qilindi. Asosiy menyudasiz 👇", reply_markup=main_menu)


# 👑 /setowner buyrug'i - bot egasini biriktirish
@router.message(F.text == "/setowner")
async def cmd_setowner(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    save_owner_id(user_id, username)
    await message.answer(
        f"👑 *Siz bot egasi sifatida biriktirildingiz!*\n\n"
        f"ID: `{user_id}`\n\n"
        f"Endi barcha kelib tushgan arizalar, mijozlarning telefon raqami va bo'sh vaqtlari to'g'ridan-to'g'ri shu shaxsiy chatga yuboriladi.\n\n"
        f"Barcha arizalar ro'yxatini ko'rish uchun: /leads",
        parse_mode="Markdown"
    )


# 💰 Narxlar bo'limi
@router.message(F.text == "💰 Narxlar")
async def show_prices(message: Message):
    text = (
        f"💰 *«{CLINIC_NAME}» xizmatlari va narxlari:*\n\n"
        "🩺 *Qand kasalligini davolash kursi:* `500 000 – 600 000 so'm`\n"
        "*(Shifokor konsultatsiyasi, ko'rik va tavsiyalar to'liq narx ichida!)*\n\n"
        "Davolash dasturiga quyidagilar kiradi:\n"
        "• Shifokor-diabetolog to'liq konsultatsiyasi va ko'rigi\n"
        "• Qand miqdorini tushirish va xavfsiz normallashtirish rejasi\n"
        "• Qand miqdori va glyukometriya nazorati\n"
        "• Shaxsiy parhez va individual ovqatlanish taomnomasi\n"
        "• Diabet asoratlari profilaktikasi\n\n"
        "Qabulga navbatsiz yozilish uchun quyidagi tugmani bosing 👇"
    )
    await message.answer(text, reply_markup=quick_book_inline, parse_mode="Markdown")


# 👨‍⚕️ Xizmatlar / Shifokorlar bo'limi
@router.message(F.text == "👨‍⚕️ Xizmatlar / Shifokorlar")
async def show_services(message: Message):
    text = (
        f"🏥 *«{CLINIC_NAME}» qand kasalligini davolash bo'yicha quyidagi xizmatlarni taqdim etadi:*\n\n"
        "🔹 *Endokrinologiya va Diabetologiya:* Qandli diabet (1 va 2-tur)ni zamonaviy davolash, insulinoterapiya va doza sozlash\n"
        "🔹 *Diabetik stopa:* Oyoq uvishishi, qon aylanishi va jarohatlarning oldini olish hamda maxsus parvarish\n"
        "🔹 *Laboratoriya:* Glikolizlangan gemoglobin (HbA1c) va ekspress qand tahlillari\n"
        "🔹 *Diabetik retinopatiya:* Ko'z tubi holatini tekshirish va ko'rishni saqlash\n"
        "🔹 *Dietologiya:* Diabetga mos individual parhez va to'g'ri taomnoma tuzish\n"
        "🔹 *Yurak va qon tomir nazorati:* EKG va ichki a'zolar UZI tekshiruvi\n\n"
        "Mutaxassis qabuliga oldindan yozilish tavsiya etiladi 👇"
    )
    await message.answer(text, reply_markup=quick_book_inline, parse_mode="Markdown")


# 📍 Manzil va Aloqa
@router.message(F.text == "📍 Manzil va Aloqa")
async def show_location(message: Message):
    phones_formatted = "\n".join([f"• {p}" for p in CLINIC_PHONES_LIST])
    text = (
        f"🏥 *«{CLINIC_NAME}»*\n"
        f"_({CLINIC_LEGAL_NAME})_\n\n"
        f"📍 *Manzil:*\n{CLINIC_ADDRESS}\n\n"
        f"📞 *Telefon raqamlar:*\n"
        f"{phones_formatted}\n\n"
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
        "Endi siz bilan bog'lanishimiz uchun "
        "quyidagi tugmani bosib telefon raqamingizni yuboring yoki qo'lda kiriting (+998901234567):",
        reply_markup=phone_keyboard
    )


# 2-Qadam: Telefon raqamni qabul qilish (Kontakt tugmasi orqali)
@router.message(BookingState.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    await state.update_data(phone=phone_number)
    await state.set_state(BookingState.waiting_for_time)
    await message.answer(
        f"Telefon raqamingiz qabul qilindi: `{phone_number}`\n\n"
        "⏰ *Endi sizga qaysi kun yoki soatda kelish / bog'lanish qulay (bo'sh vaqtingiz)?*\n\n"
        "_(Masalan: Ertaga soat 14:00 da, Dushanba kuni ertalab yoki xohlagan qulay vaqtingizni yozing)_",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )


# 2-Qadam: Telefon raqamni qabul qilish (Qo'lda yozilganda)
@router.message(BookingState.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone_number = message.text.strip()
    # Raqamni tekshirish
    cleaned = re.sub(r"[^\d+]", "", phone_number)
    if len(cleaned.replace("+", "")) < 7:
        await message.answer("Iltimos, to'g'ri telefon raqam kiriting (masalan: +998901234567):")
        return

    if not phone_number.startswith("+") and len(cleaned) == 9:
        phone_number = "+998" + cleaned
    elif not phone_number.startswith("+") and len(cleaned) == 12:
        phone_number = "+" + cleaned

    await state.update_data(phone=phone_number)
    await state.set_state(BookingState.waiting_for_time)
    await message.answer(
        f"Telefon raqamingiz qabul qilindi: `{phone_number}`\n\n"
        "⏰ *Endi sizga qaysi kun yoki soatda kelish / bog'lanish qulay (bo'sh vaqtingiz)?*\n\n"
        "_(Masalan: Ertaga soat 14:00 da, Dushanba kuni ertalab yoki xohlagan qulay vaqtingizni yozing)_",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )


# 3-Qadam: Bo'sh vaqtni qabul qilish va yakunlash
@router.message(BookingState.waiting_for_time, F.text)
async def process_time_text(message: Message, state: FSMContext, bot: Bot):
    preferred_time = message.text.strip()
    if len(preferred_time) < 2:
        await message.answer("Iltimos, sizga qulay bo'sh vaqtingizni yozing:")
        return

    await finalize_booking(message, state, bot, preferred_time)


# Yakuniy qadam: Ariza ma'lumotlarini saqlash va Bot egasiga yuborish
async def finalize_booking(message: Message, state: FSMContext, bot: Bot, preferred_time: str):
    data = await state.get_data()
    user_name = data.get("name", message.from_user.full_name or "Noma'lum")
    phone_number = data.get("phone", "Ko'rsatilmadi")
    user = message.from_user
    username_text = f"@{user.username}" if user.username else "Mavjud emas"
    lead_time = time.strftime("%Y-%m-%d %H:%M:%S")

    # Mijozga tasdiq xabari
    await message.answer(
        f"✅ *Arizangiz qabul qilindi!*\n\n"
        f"Siz ko'rsatgan qulay vaqtda (*{preferred_time}*) klinika ma'murlari siz bilan bog'lanishadi.\n\n"
        "Salomat bo'ling!",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )
    await state.clear()

    # Ariza ma'lumotlarini faylga saqlash (leads.json)
    lead_entry = {
        "time": lead_time,
        "name": user_name,
        "phone": phone_number,
        "preferred_time": preferred_time,
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name
    }
    try:
        leads_path = "leads.json"
        leads = []
        if os.path.exists(leads_path):
            with open(leads_path, "r", encoding="utf-8") as f:
                leads = json.load(f)
        leads.append(lead_entry)
        with open(leads_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Yangi ariza saqlandi: {lead_entry}")
    except Exception as e:
        logger.error(f"Arizani saqlashda xatolik: {e}")

    # Bot egasiga bildirishnoma tayyorlash
    owner_notification = (
        "🔔 *YANGI ARIZA / MIJOZ MA'LUMOTLARI!*\n"
        "────────────────────\n"
        f"👤 *F.I.O:* {user_name}\n"
        f"📞 *Telefon:* `{phone_number}`\n"
        f"⏰ *Bo'sh vaqti:* {preferred_time}\n"
        f"💬 *Telegram:* {username_text} (ID: `{user.id}`)\n"
        f"📅 *Vaqt:* {lead_time}\n"
        "────────────────────\n"
        "📌 *Holat:* Mijoz sizning bog'lanishingizni kutmoqda."
    )

    # Bot egasiga (shaxsiy chatiga) yuborish
    owner_ids = get_owner_ids()
    for oid in owner_ids:
        try:
            await bot.send_message(
                chat_id=oid,
                text=owner_notification,
                parse_mode="Markdown"
            )
            logger.info(f"✅ Arizani egasiga ({oid}) yuborildi.")
        except Exception as e:
            logger.warning(f"Egasiga ({oid}) xabar yuborishda xatolik: {e}")


# 📋 /leads buyrug'i - tushgan barcha arizalarni faqat egasiga ko'rsatish
@router.message(F.text == "/leads")
async def cmd_leads(message: Message):
    owner_ids = get_owner_ids()
    # Agar egasi biriktirilgan bo'lsa va bu foydalanuvchi ega bo'lmasa ruxsat bermaslik
    if owner_ids and message.from_user.id not in owner_ids:
        await message.answer("⛔️ Kechirasiz, arizalar ro'yxatini faqat bot egasi ko'ra oladi.")
        return

    leads_path = "leads.json"
    if not os.path.exists(leads_path):
        await message.answer("ℹ️ Hozircha hech qanday ariza kelib tushmagan.")
        return
    try:
        with open(leads_path, "r", encoding="utf-8") as f:
            leads = json.load(f)
        if not leads:
            await message.answer("ℹ️ Arizalar ro'yxati bo'sh.")
            return

        text = f"📋 *Kelib tushgan arizalar va raqamlar ({len(leads)} ta):*\n\n"
        for i, lead in enumerate(leads[-20:], 1):
            text += (
                f"{i}. 👤 *{lead.get('name')}*\n"
                f"   📞 Telefon: `{lead.get('phone')}`\n"
                f"   ⏰ Bo'sh vaqti: *{lead.get('preferred_time', 'Ko‘rsatilmagan')}*\n"
                f"   📅 Vaqti: {lead.get('time')}\n"
                f"   💬 Telegram: @{lead.get('username') or 'yoq'} (ID: `{lead.get('user_id')}`)\n"
                "────────────────────\n"
            )
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"Xatolik: {e}")


# 🤖 Foydalanuvchining barcha erkin savollariga Gemini AI orqali aqlli javob qaytarish
# Shuningdek, telefon raqam yozsa yoki qabulga yozilish niyatini bildirsa avtomatik arizaga yo'naltirish
@router.message(F.text)
async def ai_consultant_handler(message: Message, bot: Bot, state: FSMContext):
    user_query = message.text.strip()
    logger.info(f"💬 Xabar [{message.from_user.id} | @{message.from_user.username}]: '{user_query}'")

    # 1. Foydalanuvchi to'g'ridan-to'g'ri telefon raqam yozgan bo'lsa, avtomatik qabul qilish
    phone_match = re.search(r'(\+?998[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}|\b9\d{8}\b|\b\d{9}\b)', user_query)
    if phone_match:
        phone = phone_match.group(0).replace(" ", "").replace("-", "")
        if not phone.startswith("+") and len(phone) == 12:
            phone = "+" + phone
        elif not phone.startswith("+") and len(phone) == 9:
            phone = "+998" + phone

        user_name = message.from_user.full_name or "Mijoz"
        await state.update_data(name=user_name, phone=phone)
        await state.set_state(BookingState.waiting_for_time)
        await message.answer(
            f"Rahmat, {user_name}! Telefon raqamingiz qabul qilindi: `{phone}`\n\n"
            "⏰ *Endi sizga qaysi kun yoki soatda kelish / bog'lanish qulay (bo'sh vaqtingiz)?*\n\n"
            "_(Masalan: Ertaga soat 14:00 da, Dushanba kuni ertalab yoki xohlagan qulay vaqtingizni yozing)_",
            reply_markup=cancel_keyboard,
            parse_mode="Markdown"
        )
        return

    # 2. Agar foydalanuvchi qabulga yozilish niyatini bildirsa
    lower_query = user_query.lower()
    booking_keywords = ["qabul", "yozil", "navbat", "ko'rik", "yozdir"]
    if any(k in lower_query for k in booking_keywords) and len(user_query.split()) <= 4:
        await state.set_state(BookingState.waiting_for_name)
        await message.answer(
            "Assalomu alaykum! Shifokor qabuliga yozilish uchun iltimos, ism va familiyangizni kiriting:",
            reply_markup=cancel_keyboard
        )
        return

    # 3. Savolga AI orqali lo'nda javob berish
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    except Exception:
        pass

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

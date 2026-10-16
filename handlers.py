import os
import re
import json
import time
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

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
    save_owner_id,
    save_user,
    get_clinic_location,
    save_clinic_location,
    MAIN_OWNER_ID,
    AUTHORIZED_PHONES,
    AUTHORIZED_USERNAMES,
    load_active_leads,
    save_active_leads
)
from keyboards import (
    main_menu,
    phone_keyboard,
    cancel_keyboard,
    quick_book_inline
)
from ai_assistant import ask_gemini


router = Router()

# Qabulga yozilish FSM holati
class BookingState(StatesGroup):
    waiting_for_phone = State()



# /start buyrug'i (Instagramdan start=insta orqali kelganlarni ham aniqlaydi)
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    
    user = message.from_user
    save_user(user.id, user.username or "", user.full_name or "")
    logger.info(
        f"🟢 /start: ID={user.id}, Ism={user.full_name}, Username=@{user.username}, Manba={command.args or 'telegram'}"
    )

    # Agar ruxsat etilgan ega username bo'lsa (@Ummihamd va h.k.)
    if user.username and user.username.lower() in [u.lower() for u in AUTHORIZED_USERNAMES]:
        save_owner_id(user.id, user.username)
        owner_text = (
            f"👑 *Assalomu alaykum, {user.full_name}!*\n\n"
            "Siz «Sharqona salomatlik markazi» boti egasi sifatida muvaffaqiyatli biriktirildingiz.\n\n"
            "Endi barcha kelib tushgan yangi qabul arizalari va bemorlarning telefon raqamlari to'g'ridan-to'g'ri sizning shaxsiy chatingizga keladi.\n\n"
            "Barcha arizalar ro'yxatini ko'rish uchun: /leads"
        )
        await message.answer(owner_text, reply_markup=main_menu, parse_mode="Markdown")
        return



    
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
    lat, lon, address = get_clinic_location()
    text = (
        f"🏥 *«{CLINIC_NAME}»*\n"
        f"_({CLINIC_LEGAL_NAME})_\n\n"
        f"📍 *Manzil:*\n{address}\n\n"
        f"📞 *Telefon raqamlar:*\n"
        f"{phones_formatted}\n\n"
        f"⏰ *Ish vaqti:* Dushanba - Shanba: 08:30 dan 18:00 gacha\n"
        "Yakshanba: Dam olish kuni"
    )
    await message.answer(text, parse_mode="Markdown")
    # Lokatsiya yuborish
    try:
        await message.answer_location(latitude=lat, longitude=lon)
    except Exception:
        pass


# 📍 Lokatsiya yuborilganda, uni yangi klinika manzili sifatida yangilash (Ega yoki admin yuborganida)
@router.message(F.location)
async def handle_set_location(message: Message):
    owner_ids = get_owner_ids()
    is_owner = (message.from_user.id in owner_ids) if owner_ids else True

    if not is_owner:
        await message.answer("ℹ️ Lokatsiyangiz uchun rahmat. Klinika manzilini ko'rish uchun «📍 Manzil va Aloqa» tugmasini bosing.")
        return

    lat = round(message.location.latitude, 6)
    lon = round(message.location.longitude, 6)
    save_clinic_location(lat, lon)

    await message.answer(
        f"📍 *Klinikaning yangi lokatsiyasi muvaffaqiyatli saqlandi!*\n\n"
        f"🌐 Kenglik (Latitude): `{lat}`\n"
        f"🌐 Uzunlik (Longitude): `{lon}`\n\n"
        "Endi bemorlar «📍 Manzil va Aloqa» tugmasini bosganida aynan shu manzil va xarita lokatsiyasi yuboriladi.",
        parse_mode="Markdown"
    )



# 📝 Qabulga yozilish jarayonini boshlash
@router.message(F.text == "📝 Qabulga yozilish")
async def start_booking(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BookingState.waiting_for_phone)
    text = (
        "📞 *Shifokor qabuliga yozilish:*\n\n"
        "Siz bilan bog'lanishimiz uchun quyidagi **«📱 Telefon raqamni yuborish»** tugmasini bosing yoki telefon raqamingizni yozib yuboring 👇\n\n"
        "Administratorlarimiz siz bilan tezda bog'lanib, o'zingizga qulay qabul vaqtini kelishib oladilar."
    )
    await message.answer(text, reply_markup=phone_keyboard, parse_mode="Markdown")


# Inline tugma orqali qabulga yozilish bosilganda
@router.callback_query(F.data == "book_appointment")
async def inline_book_appointment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(BookingState.waiting_for_phone)
    text = (
        "📞 *Shifokor qabuliga yozilish:*\n\n"
        "Siz bilan bog'lanishimiz uchun quyidagi **«📱 Telefon raqamni yuborish»** tugmasini bosing yoki telefon raqamingizni yozib yuboring 👇"
    )
    await callback.message.answer(text, reply_markup=phone_keyboard, parse_mode="Markdown")


# 📱 Telefon raqamni kontakt orqali qabul qilish
@router.message(BookingState.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, bot: Bot):
    phone_number = message.contact.phone_number
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number

    user_name = message.contact.first_name or ""
    # Agar ruxsat etilgan egalar telefon raqami bo'lsa (911353432, 975880140 va h.k.)
    cleaned_digits = re.sub(r"[^\d]", "", phone_number)
    if any(auth_p in cleaned_digits for auth_p in AUTHORIZED_PHONES):
        save_owner_id(message.from_user.id, message.from_user.username or phone_number)
        await state.clear()
        await message.answer(
            f"👑 *Assalomu alaykum, {user_name}!*\n\n"
            "Siz «Sharqona salomatlik markazi» boti egasi sifatida muvaffaqiyatli biriktirildingiz!\n\n"
            "Endi bemorlar qabulga yozilganda, ularning kontaktlari to'g'ridan-to'g'ri sizga keladi.\n\n"
            "Arizalar ro'yxati: /leads",
            reply_markup=main_menu,
            parse_mode="Markdown"
        )
        return


    await finalize_booking(message, state, bot, phone_number, user_name)



# 📱 Telefon raqamni matn sifatida yozganda qabul qilish
@router.message(BookingState.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, bot: Bot):
    raw_phone = message.text.strip()
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if len(cleaned.replace("+", "")) < 7:
        await message.answer(
            "Iltimos, to'g'ri telefon raqam kiriting (masalan: `+998901234567`) yoki pastdagi **«📱 Telefon raqamni yuborish»** tugmasini bosing:",
            reply_markup=phone_keyboard,
            parse_mode="Markdown"
        )
        return

    phone_number = cleaned
    if not phone_number.startswith("+") and len(cleaned) == 9:
        phone_number = "+998" + cleaned
    elif not phone_number.startswith("+") and len(cleaned) == 12:
        phone_number = "+" + cleaned

    cleaned_digits = re.sub(r"[^\d]", "", phone_number)
    if any(auth_p in cleaned_digits for auth_p in AUTHORIZED_PHONES):
        save_owner_id(message.from_user.id, message.from_user.username or phone_number)
        await state.clear()
        user_name = message.from_user.full_name or "Ega"
        await message.answer(
            f"👑 *Assalomu alaykum, {user_name}!*\n\n"
            "Siz «Sharqona salomatlik markazi» boti egasi sifatida muvaffaqiyatli biriktirildingiz!\n\n"
            "Endi bemorlar qabulga yozilganda, ularning kontaktlari to'g'ridan-to'g'ri sizga keladi.\n\n"
            "Arizalar ro'yxati: /leads",
            reply_markup=main_menu,
            parse_mode="Markdown"
        )
        return

    user_name = message.from_user.full_name or "Mijoz"
    await finalize_booking(message, state, bot, phone_number, user_name)


# Yakuniy qadam: Ariza ma'lumotlarini saqlash va Bot egasiga hamda Admin guruhiga yuborish
async def finalize_booking(message: Message, state: FSMContext, bot: Bot, phone_number: str, user_name: str):
    await state.clear()
    user = message.from_user
    username_text = f"@{user.username.replace('_', '\\\\_')}" if user.username else "Mavjud emas"
    safe_name = re.sub(r"[*_`\[\]]", "", user_name)
    lead_time = time.strftime("%Y-%m-%d %H:%M:%S")
    lead_id = f"lead_{int(time.time())}_{user.id}"

    # Mijozga tasdiq xabari
    confirmation_text = (
        f"✅ *Arizangiz muvaffaqiyatli qabul qilindi!*\n\n"
        f"👤 *F.I.O:* {safe_name}\n"
        f"📞 *Telefon:* `{phone_number}`\n\n"
        "Tez orada klinika ma'murlari siz bilan bog'lanishadi va sizga eng ma'qul qabul vaqtini belgilab berishadi.\n\n"
        "Salomat bo'ling! 😊"
    )
    await message.answer(confirmation_text, reply_markup=main_menu, parse_mode="Markdown")

    # Ariza ma'lumotlarini leads.json ga saqlash (arxiv)
    lead_entry = {
        "lead_id": lead_id,
        "time": lead_time,
        "name": user_name,
        "phone": phone_number,
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

    # Bildirishnoma matni
    owner_notification = (
        "🔔 *YANGI ARIZA / QABULGA YOZILISH!*\n"
        "────────────────────\n"
        f"👤 *F.I.O:* {safe_name}\n"
        f"📞 *Telefon:* `{phone_number}`\n"
        f"💬 *Telegram:* {username_text} (ID: `{user.id}`)\n"
        f"📅 *Vaqt:* {lead_time}\n"
        "────────────────────\n"
        "📌 *Holat:* Bemor aloqaga chiqishingizni kutmoqda."
    )

    # Qabul qilish tugmasi
    claim_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ Qabul qildim", callback_data=f"claim_{lead_id}")
        ]]
    )

    # Faol arizalarni saqlash tizimi
    active_leads = load_active_leads()
    active_leads[lead_id] = {
        "lead_id": lead_id,
        "time": lead_time,
        "name": user_name,
        "phone": phone_number,
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "sent_messages": {},
        "claimed_by": None,
        "claimed_by_name": None,
        "claimed_at": None,
    }

    # Barcha egalarga yuborish
    for oid in get_owner_ids():
        try:
            sent_msg = await bot.send_message(
                chat_id=oid,
                text=owner_notification,
                reply_markup=claim_keyboard,
                parse_mode="Markdown"
            )
            active_leads[lead_id]["sent_messages"][str(oid)] = sent_msg.message_id
            logger.info(f"✅ Ariza egasiga ({oid}) yuborildi.")
        except Exception as e:
            logger.warning(f"Egasiga ({oid}) xabar yuborishda xatolik: {e}")

    save_active_leads(active_leads)

    # Admin guruhiga yuborish (agar mavjud bo'lsa)
    if ADMIN_GROUP_ID:
        try:
            group_id = int(ADMIN_GROUP_ID.strip())
            await bot.send_message(chat_id=group_id, text=owner_notification, parse_mode="Markdown")
            logger.info(f"✅ Ariza admin guruhiga ({group_id}) yuborildi.")
        except Exception as e:
            logger.warning(f"Admin guruhiga ({ADMIN_GROUP_ID}) xabar yuborishda xatolik: {e}")


# ✅ «Qabul qildim» inline tugmasi bosilganda
@router.callback_query(F.data.startswith("claim_"))
async def handle_claim_lead(callback: CallbackQuery, bot: Bot):
    lead_id = callback.data.replace("claim_", "")
    active_leads = load_active_leads()
    lead = active_leads.get(lead_id)

    if not lead:
        await callback.answer("⚠️ Ushbu ariza ma'lumoti topilmadi yoki eskirgan.", show_alert=True)
        return

    claimer = callback.from_user
    claimer_id = claimer.id
    claimer_name = claimer.full_name or claimer.username or "Ega/Xodim"
    safe_claimer_name = re.sub(r"[*_`\[\]]", "", claimer_name)

    # Agar ariza allaqachon biror kim tomonidan qabul qilingan bo'lsa
    if lead.get("claimed_by"):
        already_name = lead.get("claimed_by_name", "boshqa ma'sul")
        await callback.answer(f"⚠️ Bu arizani allaqachon {already_name} qabul qilgan!", show_alert=True)
        return

    # Arizani band qilish
    claim_time = time.strftime("%Y-%m-%d %H:%M:%S")
    lead["claimed_by"] = claimer_id
    lead["claimed_by_name"] = safe_claimer_name
    lead["claimed_at"] = claim_time
    save_active_leads(active_leads)

    await callback.answer("✅ Ariza qabul qilindi! Bemor bilan bog'laning.")

    raw_patient_name = lead.get("name", "Mijoz")
    safe_patient_name = re.sub(r"[*_`\[\]]", "", raw_patient_name)
    phone_number = lead.get("phone", "")
    orig_username = lead.get("username")
    patient_username = f"@{orig_username.replace('_', '\\\\_')}" if orig_username else "Mavjud emas"
    lead_orig_time = lead.get("time", "")

    sent_messages = lead.get("sent_messages", {})

    for oid_str, msg_id in list(sent_messages.items()):
        try:
            oid = int(oid_str)
            if oid == MAIN_OWNER_ID:
                # 👑 ASOSIY EGA (Azimov Jamil): Xabar HECH QACHON O'CHMAYDI!
                if claimer_id == MAIN_OWNER_ID:
                    claim_info = (
                        f"✅ *SIZ O'ZINGIZ QABUL QILDINGIZ (Asosiy ega)*\n"
                        f"⏱ *Vaqt:* {claim_time}"
                    )
                else:
                    claim_info = (
                        f"✅ *XODIM QABUL QILDI (Bog'lanilmoqda)*\n"
                        f"👤 *Qabul qiluvchi:* {safe_claimer_name} (`{claimer_id}`)\n"
                        f"⏱ *Qabul qilingan vaqt:* {claim_time}"
                    )

                updated_text = (
                    "🔔 *ARIZA QABUL QILINDI*\n"
                    "────────────────────\n"
                    f"👤 *F.I.O:* {safe_patient_name}\n"
                    f"📞 *Telefon:* `{phone_number}`\n"
                    f"💬 *Telegram:* {patient_username}\n"
                    f"📅 *Kelgan vaqt:* {lead_orig_time}\n"
                    "────────────────────\n"
                    f"{claim_info}"
                )
                try:
                    await bot.edit_message_text(
                        chat_id=oid,
                        message_id=msg_id,
                        text=updated_text,
                        parse_mode="Markdown",
                        reply_markup=None
                    )
                except Exception as edit_err:
                    logger.warning(f"Asosiy ega xabarini yangilashda xatolik ({oid}): {edit_err}")
            elif oid == claimer_id:
                # 👤 QABUL QILGAN ODDIY EGA: xabar qoladi va tasdiq ko'rinadi
                claimer_text = (
                    "🔔 *ARIZA QABUL QILINDI*\n"
                    "────────────────────\n"
                    f"👤 *F.I.O:* {safe_patient_name}\n"
                    f"📞 *Telefon:* `{phone_number}`\n"
                    f"💬 *Telegram:* {patient_username}\n"
                    f"📅 *Kelgan vaqt:* {lead_orig_time}\n"
                    "────────────────────\n"
                    f"✅ *SIZ QABUL QILDINGIZ!*\n"
                    f"📞 Bemor bilan bog'lanish sizning zimmangizda.\n"
                    f"⏱ *Qabul qilingan vaqt:* {claim_time}"
                )
                try:
                    await bot.edit_message_text(
                        chat_id=oid,
                        message_id=msg_id,
                        text=claimer_text,
                        parse_mode="Markdown",
                        reply_markup=None
                    )
                except Exception as edit_err:
                    logger.warning(f"Qabul qiluvchi xabarini yangilashda xatolik ({oid}): {edit_err}")
            else:
                # 🚫 BOSHQALAR (Boshqa oddiy egalar): Ikki kishi bir vaqtda telefon qilmasligi uchun xabar BUTUNLAY O'CHIRILADI!
                try:
                    await bot.delete_message(chat_id=oid, message_id=msg_id)
                except Exception as del_err:
                    logger.warning(f"Boshqa egadan xabarni o'chirishda xatolik ({oid}): {del_err}")
        except Exception as e:
            logger.warning(f"Egalar xabarini yangilashda xatolik ({oid_str}): {e}")




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

        text = f"📋 *Kelib tushgan arizalar ({len(leads)} ta):*\n\n"
        for i, lead in enumerate(leads[-20:], 1):
            text += (
                f"{i}. 👤 *{lead.get('name')}*\n"
                f"   📞 Telefon: `{lead.get('phone')}`\n"
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
    user = message.from_user
    save_user(user.id, user.username or "", user.full_name or "")
    logger.info(f"💬 Xabar [{user.id} | @{user.username}]: '{user_query}'")

    # 1. Foydalanuvchi to'g'ridan-to'g'ri telefon raqam yozgan bo'lsa, avtomatik qabul qilish
    phone_match = re.search(r'(\+?998[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}|\b9\d{8}\b|\b\d{9}\b)', user_query)
    if phone_match:
        phone = phone_match.group(0).replace(" ", "").replace("-", "")
        if not phone.startswith("+") and len(phone) == 12:
            phone = "+" + phone
        elif not phone.startswith("+") and len(phone) == 9:
            phone = "+998" + phone

        user_name = message.from_user.full_name or "Mijoz"
        await finalize_booking(message, state, bot, phone, user_name)
        return

    # 2. Agar foydalanuvchi qabulga yozilish niyatini bildirsa
    lower_query = user_query.lower()
    booking_keywords = ["qabul", "yozil", "navbat", "ko'rik", "yozdir"]
    if any(k in lower_query for k in booking_keywords) and len(user_query.split()) <= 4:
        await start_booking(message, state)
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

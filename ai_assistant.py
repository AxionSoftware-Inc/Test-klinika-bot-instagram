import asyncio
import logging
import time
from typing import Optional, Dict, Tuple
from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    CLINIC_NAME,
    CLINIC_PHONE,
    CLINIC_ADDRESS,
    SERVICES_AND_PRICES
)

logger = logging.getLogger(__name__)

# Foydalanuvchilarning oxirgi interaction ID va vaqti: {user_id: (interaction_id, timestamp)}
user_sessions: Dict[int, Tuple[str, float]] = {}
SESSION_TIMEOUT_SECONDS = 1800  # 30 daqiqa

client: Optional[genai.Client] = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini client yaratishda xatolik: {e}")

services_text = "\n".join([f"• {s['name']}: {s['price']}" for s in SERVICES_AND_PRICES])

SYSTEM_INSTRUCTION = f"""
Siz — {CLINIC_NAME} klinikasining rasmiy, yuqori malakali, xushmuomala va aqlli AI maslahatchisisiz.

Klinikamiz haqida rasmiy ma'lumotlar:
- Nomi: {CLINIC_NAME}
- Telefon: {CLINIC_PHONE}
- Manzil: {CLINIC_ADDRESS}
- Ish vaqti: Dushanba - Shanba, 08:30 dan 18:00 gacha (Yakshanba: Dam olish kuni)
- Asosiy xizmatlar va narxlar:
{services_text}
• Stomatolog ko‘rigi va konsultatsiya: Bepul
• Tish plomba qilish: 150 000 so‘mdan
• Tish tozalash va oqartirish: 200 000 so‘mdan

QOIDALAR:
1. Mijozga do'stona, samimiy, madaniyatli va aniq o'zbek tilida javob bering.
2. Agar salomlashsa yoki minnatdorchilik bildirsa, juda chiroyli alik oling va iliq muomala qiling.
3. Mijozning savollariga (narx, og'riqsiz davolash, kafolat, manzil, shifokorlar, ish vaqti) to'liq va tushunarli javob bering.
4. Har doim bemorni ortiqcha xavotirga solmasdan, tinchlantiring va ko'rikka kelishga undash orqali yordam taklif qiling.
5. Javobingiz lo'nda, o'qishga juda qulay bo'lsin.
6. Matn oxirida mijozga navbatga yozilish qulay bo'lishi uchun quyidagi jumlani qo'shing:
"Qabulga navbatsiz yozilish uchun pastdagi tugmani bosing 👇"
"""

async def ask_gemini(user_message: str, user_id: Optional[int] = None) -> str:
    """Foydalanuvchi savoliga Gemini 3.5 Flash-Lite orqali aqlli javob qaytarish"""
    if not client:
        return (
            f"Assalomu alaykum! {CLINIC_NAME} klinikasiga xush kelibsiz. 😊\n\n"
            "Savollaringiz bo'yicha ma'lumot olish yoki qabulga yozilish uchun "
            "quyidagi tugmalardan foydalanishingiz mumkin 👇"
        )

    # Context (oldingi suhbat xotirasi) mavjudligini tekshirish
    prev_interaction_id = None
    now = time.time()
    if user_id and user_id in user_sessions:
        saved_id, last_time = user_sessions[user_id]
        if now - last_time < SESSION_TIMEOUT_SECONDS:
            prev_interaction_id = saved_id
        else:
            del user_sessions[user_id]

    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

    for model_name in models_to_try:
        # 1. Eng yangi Interactions API orqali kontekst bilan sinab ko'rish
        try:
            def _call_interaction():
                if prev_interaction_id:
                    try:
                        return client.interactions.create(
                            model=model_name,
                            input=user_message,
                            previous_interaction_id=prev_interaction_id
                        )
                    except Exception as ex:
                        logger.info(f"Context expired or failed ({ex}), starting fresh interaction...")
                return client.interactions.create(
                    model=model_name,
                    input=user_message,
                    system_instruction=SYSTEM_INSTRUCTION
                )

            interaction = await asyncio.to_thread(_call_interaction)
            if interaction and interaction.output_text:
                if user_id and interaction.id:
                    user_sessions[user_id] = (interaction.id, time.time())
                return interaction.output_text.strip()
        except Exception as e:
            logger.warning(f"Interactions API ({model_name}) xatolik: {e}, models API sinab ko'rilmoqda...")

        # 2. Fallback: models.generate_content orqali sinab ko'rish
        try:
            def _call_generate():
                return client.models.generate_content(
                    model=model_name,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.5,
                        max_output_tokens=700,
                    )
                )

            gen_res = await asyncio.to_thread(_call_generate)
            if gen_res and gen_res.text:
                return gen_res.text.strip()
        except Exception as e:
            logger.warning(f"GenerateContent ({model_name}) xatolik: {e}")

    return (
        f"Assalomu alaykum! {CLINIC_NAME} klinikasiga xush kelibsiz. 😊\n\n"
        "Sizga qanday yordam bera olamiz? Xizmatlarimiz, narxlar yoki "
        "qabulga yozilish uchun quyidagi tugmani bosing 👇"
    )

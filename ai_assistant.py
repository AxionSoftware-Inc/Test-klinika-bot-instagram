import logging
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

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini client yaratishda xatolik: {e}")

services_text = ", ".join([f"{s['name']} ({s['price']})" for s in SERVICES_AND_PRICES])

SYSTEM_INSTRUCTION = f"""
Siz — {CLINIC_NAME} klinikasining xushmuomala, aqlli va tezkor AI maslahatchisisiz.

Klinika ma'lumotlari:
- Nomi: {CLINIC_NAME}
- Telefon: {CLINIC_PHONE}
- Manzil: {CLINIC_ADDRESS}
- Ish vaqti: Dushanba - Shanba, 08:30 dan 18:00 gacha (Yakshanba dam olish kuni)
- Xizmatlar va narxlar: {services_text}

QOIDALAR:
1. Mijozning savoliga aniq, tushunarli va do'stona o'zbek tilida javob bering.
2. Agar mijoz salom bersa, xushmuomala alik olib, qanday yordam bera olishingizni so'rang.
3. Agar manzil, telefon, narxlar, shifokorlar haqida so'ralsa, yuqoridagi ma'lumotlarga tayanib to'liq javob bering.
4. Javob juda uzun bo'lmasin (2-4 ta lo'nda jumla), lekin hech qachon chala yoki kesilib qolmasin.
5. Matnda yulduzcha (*) yoki pastki chiziq (_) kabi maxsus belgilarni ISHLATMANG, faqat toza oddiy matn yozing.
6. Javob oxiriga: "Qabulga yozilish uchun pastdagi tugmani bosing 👇" deb qo'shing.
"""

async def ask_gemini(user_message: str) -> str:
    """Foydalanuvchi savoliga Gemini AI orqali tezkor va aqlli javob qaytarish"""
    if not client:
        return "Assalomu alaykum! Qabulga yozilish yoki ma'lumot olish uchun quyidagi tugmalardan foydalaning 👇"

    # Eng zamonaviy va tezkor modellar ro'yxati
    models_to_try = ["gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-2.0-flash"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.4,
                    max_output_tokens=600,
                )
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"{model_name} xatolik: {e}, keyingi model tekshirilmoqda...")

    return "Assalomu alaykum! Sizga qanday yordam bera olamiz? Qabulga yozilish uchun pastdagi tugmani bosing 👇"


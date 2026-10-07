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
Siz — {CLINIC_NAME} klinikasining tezkor va xushmuomala AI konsultantisiz.

Ma'lumotlar:
Nomi: {CLINIC_NAME} | Tel: {CLINIC_PHONE} | Manzil: {CLINIC_ADDRESS}
Ish vaqti: Dush-Shanba 08:30-18:00
Xizmatlar: {services_text}

MUHIM QOIDALAR:
1. Faqat 1 yoki 2 ta JUDA QISQA, aniq jumla bilan javob bering. Uzun matn yozmang!
2. Belgilardan (yulduzcha *, pastki chiziq _ kabi formatlardan) foydalanmang, faqat oddiy toza matn yozing.
3. Mijoz salom bersa, qisqa alik olib, nima xizmat kerakligini so'rang.
4. Javob oxiriga: "Qabulga yozilish uchun pastdagi tugmani bosing 👇" deb qo'shing.
"""

async def ask_gemini(user_message: str) -> str:
    """Foydalanuvchi savoliga Gemini Flash Lite orqali tezkor va qisqa javob"""
    if not client:
        return "Assalomu alaykum! Qabulga yozilish yoki ma'lumot olish uchun quyidagi tugmalardan foydalaning 👇"

    # Eng tezkor va yengil modellar ro'yxati
    models_to_try = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.5,
                    max_output_tokens=200,
                )
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"{model_name} xatolik: {e}, keyingi model tekshirilmoqda...")

    return "Assalomu alaykum! Sizga qanday yordam bera olamiz? Qabulga yozilish uchun pastdagi tugmani bosing 👇"

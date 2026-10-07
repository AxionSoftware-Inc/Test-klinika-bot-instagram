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

# Gemini Client initsializatsiyasi
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini client yaratishda xatolik: {e}")

# Klinika xizmatlari va narxlari matn ko'rinishida
services_text = "\n".join([f"- {s['name']}: {s['price']}" for s in SERVICES_AND_PRICES])

SYSTEM_INSTRUCTION = f"""
Siz — {CLINIC_NAME} klinikasining rasmiy, professional va xushmuomala virtual AI-konsultantisiz.
Sizning vazifangiz: mijozlarning savollariga aniq, qisqa va tushunarli javob berish hamda ularni shifokor qabuliga navbatga yozilishga taklif qilish.

Klinika ma'lumotlari:
• Nomi: {CLINIC_NAME}
• Telefon: {CLINIC_PHONE}
• Manzil: {CLINIC_ADDRESS}
• Ish vaqti: Dushanba - Shanba, 08:30 - 18:00 (Yakshanba - dam olish kuni).
• Xizmatlar va narxlar:
{services_text}

Qoidalar:
1. Xushmuomala, mehmondo'st va samimiy ohangda javob bering.
2. Mijoz qaysi tilda yozsa (o'zbek, rus, ingliz), shu tilda javob bering.
3. Aniq tibbiy tashxis qo'ymang! Faqat umumiy tavsiya bering va qaysi mutaxassisga murojaat qilish kerakligini ayting.
4. Har bir javobingiz oxirida qabulga yozilish uchun "📝 Qabulga yozilish" tugmasini bosishni yoki Telegram botimizdan (https://t.me/klinikatesttt_bot) foydalanishni taklif qiling.
5. Javobingiz juda cho'zilib ketmasin (maksimal 2-3 ta qisqa xatboshi).
"""

async def ask_gemini(user_message: str) -> str:
    """Foydalanuvchi savoliga Gemini AI orqali aqlli javob generatsiya qilish"""
    if not client:
        return (
            "Kechirasiz, hozirda AI yordamchi vaqtincha faol emas. "
            "Iltimos, asosiy menyudagi tugmalardan foydalaning yoki administrator bilan bog'laning."
        )

    try:
        # gemini-2.5-flash tezkor va o'zbek tilida ajoyib ishlaydi
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=600,
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API xatoligi: {e}")
        # Agar 2.5-flash da xatolik bo'lsa, gemini-2.0-flash yoki 1.5-flash bilan urinib ko'rish
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                    max_output_tokens=600,
                )
            )
            return response.text
        except Exception as e2:
            logger.error(f"Gemini zaxira modeli xatoligi: {e2}")
            return (
                "Savolingiz uchun rahmat! Mutaxassislarimiz sizga batafsil ma'lumot berishga tayyor. "
                "Qabulga yozilish yoki ma'lumot olish uchun quyidagi tugmalardan birini tanlang 👇"
            )

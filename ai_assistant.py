import os
import json
import asyncio
import logging
import time
import urllib.request
from typing import Optional, Dict, Tuple, List
from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    CLINIC_NAME,
    CLINIC_LEGAL_NAME,
    CLINIC_PHONE,
    CLINIC_ADDRESS,
    SERVICES_AND_PRICES
)

logger = logging.getLogger(__name__)

# OpenRouter kaliti
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "") or (
    GEMINI_API_KEY if (GEMINI_API_KEY and GEMINI_API_KEY.startswith("sk-or-")) else ""
)

# Foydalanuvchilarning suhbat tarixi: {user_id: ([(role, text), ...], timestamp)}
user_histories: Dict[int, Tuple[List[Dict[str, str]], float]] = {}
user_sessions: Dict[int, Tuple[str, float]] = {}
SESSION_TIMEOUT_SECONDS = 1800  # 30 daqiqa

client: Optional[genai.Client] = None
if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("sk-or-"):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini client yaratishda xatolik: {e}")

services_text = "\n".join([f"• {s['name']}: {s['price']}" for s in SERVICES_AND_PRICES])

SYSTEM_INSTRUCTION = f"""
Siz — «{CLINIC_NAME}» ({CLINIC_LEGAL_NAME}ga qarashli) qand kasalligini davolashga ixtisoslashgan markazining rasmiy, yuqori malakali, xushmuomala va tibbiy savodli AI maslahatchisisiz.

Klinikamiz haqida rasmiy ma'lumotlar:
- Nomi: «{CLINIC_NAME}» ({CLINIC_LEGAL_NAME})
- Joylashuv va manzil: {CLINIC_ADDRESS}
- Telefonlar: {CLINIC_PHONE}
- Ish vaqti: Dushanba - Shanba, 08:30 dan 18:00 gacha (Yakshanba: Dam olish kuni)
- Davolash kursi va narxlar:
  • Qand kasalligini davolash kursi: 500 000 – 600 000 so'm (Shifokor-diabetolog konsultatsiyasi, ko'rik, glyukometriya nazorati va parhez rejasi to'liq ushbu narx ichida!)

BIZNING ASOSIY YO'NALISHLARIMIZ:
1. Qandli diabet (1-tur va 2-tur)ni zamonaviy usulda samarali davolash va nazorat qilish.
2. Qondagi qand miqdorini xavfsiz normallashtirish va insulin dozasini to'g'ri belgilash.
3. Diabet asoratlarining (diabetik stopa/oyoq, ko'rish pasayishi/retinopatiya, buyrak zararlanishi) oldini olish va davolash.
4. Glikolizlangan gemoglobin (HbA1c) va ekspress qand tahlillari.
5. Shaxsiy parhez va to'g'ri ovqatlanish rejasini ishlab chiqish (Diabet maktabi).

QOIDALAR VA QAT'IY CHEKLOVLAR:
1. Mijozga samimiy, madaniyatli, tushunarli va aniq o'zbek tilida javob bering.
2. JAVOBLAR LO'NDA VA QISQA BO'LSIN (2-4 jumladan oshmasin, ortiqcha gap, uzun matnlar va keraksiz ma'lumotlar yozmang).
3. TIBBIY CHEKLOV: O'zboshimchalik bilan dori-darmon, ukol yoki mustaqil davolash usullarini ASLO TAVSIYA QILMANG. Barcha tibbiy savollarda bemorga aniq tashxis va davo faqat klinikamizda shifokor ko'rigida qo'yilishini aytib, ko'rikka taklif qiling.
4. Narx haqida so'ralsa: Davolash kursi 500 000 – 600 000 so'm ekanligini va shifokor konsultatsiyasi hamda ko'rigi to'liq shu narx ichida ekanligini ayting.
5. Manzil haqida so'ralsa: Shahrisabz shahri, Tez yordam klinikasi ro'parasida joylashganimizni ma'lum qiling.
6. Telefonlar haqida so'ralsa: +998 95 676 18 08, +998 91 135 34 32, +998 97 588 01 40 raqamlarini bering.
7. Klinika xizmatlariga kirmaydigan ma'lumotlarni o'zingizdan to'qimang, administratorga bog'lanishni ayting.
8. Har doim javobingiz oxirida mijozga ko'rikka yozilish uchun telefon raqami va o'ziga qulay bo'sh vaqtini qoldirishni taklif qiling:
"Qabulga yozilish uchun telefon raqamingiz va bo'sh vaqtingizni qoldiring yoki pastdagi tugmani bosing 👇"
"""


def _call_openrouter(user_message: str, history: List[Dict[str, str]]) -> Optional[str]:
    """OpenRouter orqali Gemini 3.5 Flash-Lite modeliga murojaat qilish"""
    if not OPENROUTER_API_KEY:
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://klinika.uz",
        "X-Title": "Klinika Diabet Maslahatchisi"
    }

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": "google/gemini-3.5-flash-lite",
        "messages": messages,
        "temperature": 0.4
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.warning(f"OpenRouter so'rovida xatolik: {e}")
        return None

    return None


async def ask_gemini(user_message: str, user_id: Optional[int] = None) -> str:
    """Foydalanuvchi savoliga Gemini 3.5 Flash-Lite orqali aqlli javob qaytarish"""
    now = time.time()
    history: List[Dict[str, str]] = []

    if user_id and user_id in user_histories:
        saved_hist, last_time = user_histories[user_id]
        if now - last_time < SESSION_TIMEOUT_SECONDS:
            history = saved_hist[-6:]  # Oxirgi 3 ta savol-javob
        else:
            del user_histories[user_id]

    # 1. OpenRouter (Gemini 3.5 Flash Lite) orqali sinab ko'rish
    try:
        or_answer = await asyncio.to_thread(_call_openrouter, user_message, history)
        if or_answer:
            if user_id:
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": or_answer})
                user_histories[user_id] = (history, time.time())
            return or_answer
    except Exception as e:
        logger.warning(f"OpenRouter chaqiruvida xatolik: {e}")

    # 2. Google GenAI SDK orqali sinab ko'rish (agar mijoz kaliti mavjud bo'lsa)
    if client:
        models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
        for model_name in models_to_try:
            try:
                def _call_generate():
                    return client.models.generate_content(
                        model=model_name,
                        contents=user_message,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.4,
                            max_output_tokens=700,
                        )
                    )

                gen_res = await asyncio.to_thread(_call_generate)
                if gen_res and gen_res.text:
                    ans = gen_res.text.strip()
                    if user_id:
                        history.append({"role": "user", "content": user_message})
                        history.append({"role": "assistant", "content": ans})
                        user_histories[user_id] = (history, time.time())
                    return ans
            except Exception as e:
                logger.warning(f"Google GenAI ({model_name}) xatolik: {e}")

    return (
        f"Assalomu alaykum! {CLINIC_NAME} qand kasalligini davolash markaziga xush kelibsiz. 😊\n\n"
        "Sizga qanday yordam bera olamiz? Xizmatlarimiz, narxlar yoki "
        "qabulga yozilish uchun quyidagi tugmani bosing 👇"
    )

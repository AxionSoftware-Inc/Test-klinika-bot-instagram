import logging
import os
import httpx
from fastapi import FastAPI, Request, Response, Query
from pydantic import BaseModel
from typing import Optional

from ai_assistant import ask_gemini
from config import CLINIC_NAME

logger = logging.getLogger("instagram_webhook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Instagram Meta Webhook for Clinic")

# Sozlamalar (.env dan olinadi)
VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN", "klinika_secret_verify_token_2026")
PAGE_ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN", "")
BOT_TELEGRAM_LINK = "https://t.me/klinikatesttt_bot?start=insta"

GRAPH_API_URL = "https://graph.facebook.com/v21.0"


# 1. Meta Webhook Tasdiqlash (GET)
@app.get("/instagram-webhook")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("Meta Webhook muvaffaqiyatli tasdiqlandi!")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning("Meta Webhook tekshiruvi muvaffaqiyatsiz bo'ldi.")
    return Response(content="Verification token mismatch", status_code=403)


# 2. Instagram Voqealari (POST) — Kommentlar va Direct
@app.post("/instagram-webhook")
async def receive_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Yangi Instagram Webhook ma'lumoti: {data}")
    except Exception as e:
        logger.error(f"JSON o'qishda xatolik: {e}")
        return {"status": "bad request"}

    if data.get("object") != "instagram":
        return {"status": "ignored"}

    for entry in data.get("entry", []):
        # A) Kommentlar kelganda (changes -> comments)
        changes = entry.get("changes", [])
        for change in changes:
            field = change.get("field")
            value = change.get("value", {})
            if field == "comments":
                await handle_instagram_comment(value)

        # B) Direct xabarlar kelganda (messaging)
        messaging_list = entry.get("messaging", [])
        for messaging in messaging_list:
            if "message" in messaging and not messaging.get("message", {}).get("is_echo"):
                await handle_instagram_direct(messaging)

    return {"status": "ok"}


# Komment yozganlarga avto-javob qaytarish
async def handle_instagram_comment(comment_data: dict):
    comment_id = comment_data.get("id")
    text = comment_data.get("text", "").strip()
    from_user = comment_data.get("from", {})
    username = from_user.get("username", "")

    logger.info(f"Yangi komment: @{username}: '{text}' (ID: {comment_id})")

    if not PAGE_ACCESS_TOKEN or not comment_id:
        return

    async with httpx.AsyncClient() as client:
        # 1-qadam: Komment ostiga ommaviy qisqa javob yozish
        public_reply_text = f"Assalomu alaykum @{username}! Directingizga to'liq ma'lumot va qabul linkini yubordik ✅"
        try:
            res_public = await client.post(
                f"{GRAPH_API_URL}/{comment_id}/replies",
                params={"access_token": PAGE_ACCESS_TOKEN},
                json={"message": public_reply_text}
            )
            logger.info(f"Komment ostiga javob qaytarildi: {res_public.status_code}")
        except Exception as e:
            logger.error(f"Komment ostiga javob yozishda xatolik: {e}")

        # 2-qadam: Mijozning shaxsiy Directiga xabar va Telegram linkini otish (Private Reply)
        dm_text = (
            f"Assalomu alaykum @{username}!\n\n"
            f"{CLINIC_NAME} klinikasiga qiziqish bildirganingiz uchun rahmat.\n\n"
            f"💰 Barcha narxlar, shifokorlar ro'yxati va qabulga navbatga yozilish "
            f"bizning rasmiy Telegram botimizda 👇\n\n"
            f"👉 {BOT_TELEGRAM_LINK}"
        )
        try:
            res_dm = await client.post(
                f"{GRAPH_API_URL}/me/messages",
                params={"access_token": PAGE_ACCESS_TOKEN},
                json={
                    "recipient": {"comment_id": comment_id},
                    "message": {"text": dm_text}
                }
            )
            logger.info(f"Directga avto-xabar yuborildi: {res_dm.status_code}")
        except Exception as e:
            logger.error(f"Directga xabar yuborishda xatolik: {e}")


# Directga yozganlarga Gemini AI bilan javob berish
async def handle_instagram_direct(messaging_data: dict):
    sender_id = messaging_data.get("sender", {}).get("id")
    message = messaging_data.get("message", {})
    user_text = message.get("text", "").strip()

    if not sender_id or not user_text or not PAGE_ACCESS_TOKEN:
        return

    logger.info(f"Directdan xabar keldi (Sender ID: {sender_id}): '{user_text}'")

    # Gemini AI dan aqlli, qisqa javob olish
    ai_reply = await ask_gemini(user_text)

    # Javob tagiga Telegram bot linkini qo'shish
    final_reply = (
        f"{ai_reply}\n\n"
        f"📋 To'liq ma'lumot va navbatga yozilish Telegram botimizda:\n"
        f"👉 {BOT_TELEGRAM_LINK}"
    )

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                f"{GRAPH_API_URL}/me/messages",
                params={"access_token": PAGE_ACCESS_TOKEN},
                json={
                    "recipient": {"id": sender_id},
                    "message": {"text": final_reply}
                }
            )
            logger.info(f"Directga Gemini AI javobi yuborildi: {res.status_code}")
        except Exception as e:
            logger.error(f"Directga javob yuborishda xatolik: {e}")

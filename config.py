import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDIXr_GOpeY5np87-BDxUiMWRhRlJATj0Q")

CLINIC_NAME = os.getenv("CLINIC_NAME", "Bizning Klinika")
CLINIC_PHONE = os.getenv("CLINIC_PHONE", "+998 71 123 45 67")
CLINIC_ADDRESS = os.getenv("CLINIC_ADDRESS", "Toshkent shahri, Markaziy ko'cha, 1-uy")
CLINIC_LOCATION_LAT = float(os.getenv("CLINIC_LOCATION_LAT", "41.311081"))
CLINIC_LOCATION_LON = float(os.getenv("CLINIC_LOCATION_LON", "69.240562"))

# Klinika xizmatlari va narxlari (o'zgartirish oson bo'lishi uchun bu yerda saqlanadi)
SERVICES_AND_PRICES = [
    {"name": "🩺 Terapevt ko'rigi", "price": "150,000 so'm"},
    {"name": "🦷 Stomatolog maslahati", "price": "100,000 so'm"},
    {"name": "🔬 Umumiy qon tahlili", "price": "70,000 so'm"},
    {"name": "🫀 EKG (Kardiogramma)", "price": "120,000 so'm"},
    {"name": "🖥 UZI (Barcha a'zolar)", "price": "180,000 so'm"},
    {"name": "👨‍⚕️ Nevropatolog qabuli", "price": "160,000 so'm"},
]

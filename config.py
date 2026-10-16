import os
import json
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDIXr_GOpeY5np87-BDxUiMWRhRlJATj0Q")

OWNER_FILE = os.path.join(os.path.dirname(__file__), "owner.json")

def get_owner_ids():
    ids = set()
    if ADMIN_ID:
        for x in ADMIN_ID.split(","):
            if x.strip().lstrip("-").isdigit():
                ids.add(int(x.strip()))
    if os.path.exists(OWNER_FILE):
        try:
            with open(OWNER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "owner_id" in data:
                    ids.add(int(data["owner_id"]))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, int):
                            ids.add(item)
                        elif isinstance(item, dict) and "owner_id" in item:
                            ids.add(int(item["owner_id"]))
        except Exception:
            pass
    return list(ids)

def save_owner_id(owner_id: int, username: str = ""):
    data = {"owner_id": owner_id, "username": username}
    with open(OWNER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def save_user(user_id: int, username: str = "", full_name: str = ""):
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception:
            users = {}
    users[str(user_id)] = {
        "id": user_id,
        "username": (username or "").lstrip("@"),
        "full_name": full_name
    }
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def find_user_by_username(username: str):
    clean = username.strip().lstrip("@").lower()
    if not clean or not os.path.exists(USERS_FILE):
        return None
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
            for u in users.values():
                if u.get("username", "").lower() == clean:
                    return u
    except Exception:
        pass
    return None

def set_owner_by_username(username: str) -> bool:
    user = find_user_by_username(username)
    if user:
        save_owner_id(user["id"], user.get("username", ""))
        return True
    return False


BOT_USERNAME = os.getenv("BOT_USERNAME", "sharqonaklinika_bot")
BOT_LINK = f"https://t.me/{BOT_USERNAME}"
BOT_INSTA_LINK = f"https://t.me/{BOT_USERNAME}?start=insta"

CLINIC_NAME = os.getenv("CLINIC_NAME", "Sharqona salomatlik markazi")
CLINIC_LEGAL_NAME = os.getenv("CLINIC_LEGAL_NAME", "«Samara End Ko Shahrisabz» MCHJ")
CLINIC_PHONE = os.getenv("CLINIC_PHONE", "+998 95 676 18 08, +998 91 135 34 32, +998 97 588 01 40")
CLINIC_PHONES_LIST = [
    "+998 95 676 18 08",
    "+998 91 135 34 32",
    "+998 97 588 01 40"
]
CLINIC_ADDRESS = os.getenv("CLINIC_ADDRESS", "Shahrisabz shahri, Tez yordam klinikasi ro'parasi")
CLINIC_LOCATION_LAT = float(os.getenv("CLINIC_LOCATION_LAT", "39.042527"))
CLINIC_LOCATION_LON = float(os.getenv("CLINIC_LOCATION_LON", "66.828387"))

LOCATION_FILE = os.path.join(os.path.dirname(__file__), "location.json")

def get_clinic_location():
    if os.path.exists(LOCATION_FILE):
        try:
            with open(LOCATION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                lat = float(data.get("lat", CLINIC_LOCATION_LAT))
                lon = float(data.get("lon", CLINIC_LOCATION_LON))
                address = data.get("address", CLINIC_ADDRESS)
                return lat, lon, address
        except Exception:
            pass
    return CLINIC_LOCATION_LAT, CLINIC_LOCATION_LON, CLINIC_ADDRESS

def save_clinic_location(lat: float, lon: float, address: str = ""):
    data = {"lat": lat, "lon": lon}
    if address:
        data["address"] = address
    else:
        _, _, cur_address = get_clinic_location()
        data["address"] = cur_address
    with open(LOCATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Qand kasalligini davolashga ixtisoslashgan xizmatlar va narxlar
SERVICES_AND_PRICES = [
    {"name": "🩺 Qand kasalligini davolash kursi (konsultatsiya ichida)", "price": "500 000 – 600 000 so'm"},
    {"name": "👨‍⚕️ Shifokor-diabetolog to'liq konsultatsiyasi va ko'rigi", "price": "Davolash kursi ichida"},
    {"name": "📋 Individual davolash va sog'lomlashtirish dasturi", "price": "Davolash kursi ichida"},
    {"name": "🩸 Qand miqdori va glyukometriya nazorati", "price": "Kurs ichida kiritilgan"},
    {"name": "🥗 Shaxsiy parhez va ovqatlanish taomnomasi", "price": "Kurs ichida kiritilgan"},
    {"name": "🦶 Diabet asoratlari profilaktikasi va tavsiyalar", "price": "Kurs ichida kiritilgan"},
]

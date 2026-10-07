from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Asosiy menyu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Qabulga yozilish"),
        ],
        [
            KeyboardButton(text="💰 Narxlar"),
            KeyboardButton(text="👨‍⚕️ Xizmatlar / Shifokorlar"),
        ],
        [
            KeyboardButton(text="📍 Manzil va Aloqa"),
        ]
    ],
    resize_keyboard=True
)

# Telefon raqam so'rash klaviaturasi
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
        ],
        [
            KeyboardButton(text="❌ Bekor qilish")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Bekor qilish klaviaturasi
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ Bekor qilish")
        ]
    ],
    resize_keyboard=True
)

# Qabulga o'tish uchun tezkor inline tugma (Narxlar yoki xizmatlar ko'rilganda)
quick_book_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Navbatga / Qabulga yozilish", callback_data="book_appointment")
        ]
    ]
)

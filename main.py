import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import router

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

async def main():
    if not BOT_TOKEN:
        print("\n❌ XATO: BOT_TOKEN topilmadi!")
        print("Iltimos, .env faylini yarating va BOT_TOKEN qiymatini kiriting.\n")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    # Handlerlarni ro'yxatdan o'tkazish
    dp.include_router(router)

    print("\n" + "=" * 50)
    print("🚀 Klinika Telegram Boti muvaffaqiyatli ishga tushdi!")
    print("=" * 50 + "\n")

    # Eski kutilayotgan update'larni tozalash va pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Bot to'xtatildi.\n")

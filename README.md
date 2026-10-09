# 🏥 Klinika Instagram & Telegram Avtomatlashtirish Tizimi

Bu tizim Instagramdan kelayotgan ommaviy mijozlar oqimini (komment va Direct) avtomatlashtirilgan tarzda Telegram botga o'tkazish va Telegram orqali ularni qabulga yozib, admin guruhiga (operatorga) yetkazish uchun mo'ljallangan.

---

## 📂 Loyiha Tuzilishi

- **`meta_automation/META_AUTOMATION_SETUP.md`** — Meta Business Suite (Instagram & Facebook) orqali rasmiy avtomatlashtirish, 5 ta yo'nalish bo'yicha trigger so'zlar va javoblar qo'llanmasi.
- **`MANYCHAT_SETUP.md`** — ManyChat-da Reels/Post kommentlariga avto-javob, Direct xabarlari va Telegram tugmasini sozlash bo'yicha vizual qo'llanma.
- **`main.py`** — Telegram botning asosiy ishga tushirish fayli.
- **`handlers.py`** — Start, Narxlar, Shifokorlar, Manzil va Qabulga yozilish logikasi.
- **`keyboards.py`** — Bot menyulari va tugmalari.
- **`config.py`** — Sozlamalar va klinika narxlari.
- **`.env.example`** — Token va Admin guruh ID si namunasi.

---

## 🚀 Telegram Botni Ishga Tushirish

### 1. Virtual muhit yaratish va kutubxonalarni o'rnatish

Terminalda quyidagi buyruqlarni bajaring:

```bash
cd "/Users/macbookpro/Documents/Klinika Instagram"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Sozlamalarni kiritish (.env)

`.env.example` faylidan nusxa olib `.env` yarating:

```bash
cp .env.example .env
```

`.env` faylini ochib quyidagilarni kiriting:
1. **`BOT_TOKEN`**: [@BotFather](https://t.me/BotFather) dan olingan bot tokeni.
2. **`ADMIN_GROUP_ID`**: Operatorlar guruhi ID si.
   > 💡 *Guruh ID sini qanday bilish mumkin?*
   > Botni o'sha guruhga admin qilib qo'shing. Keyin guruhga biror xabar yozing yoki [@username_to_id_bot](https://t.me/username_to_id_bot) orqali guruh ID sini oling (u odatda `-100...` bilan boshlanadi).

### 3. Botni ishga tushirish

```bash
python3 main.py
```

---

## 📸 ManyChat orqali Instagramni ulash

To'liq bosqichma-bosqich qo'llanma **[MANYCHAT_SETUP.md](file:///Users/macbookpro/Documents/Klinika%20Instagram/MANYCHAT_SETUP.md)** faylida keltirilgan:
1. Trigger: `User comments on Post or Reel`
2. Komment ostiga 4-5 xil variantda javob qaytarish.
3. Directga matn va `🤖 Telegram Botga o'tish` tugmasi (`https://t.me/BOT_USERNAME?start=insta`).
4. Direct qo'ng'iroqlarni (Audio call) Instagram sozlamalaridan o'chirish.

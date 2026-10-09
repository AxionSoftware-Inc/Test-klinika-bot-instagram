# 🤖 Meta Business Suite & Instagram Native Avtomatlashtirish Tizimi (Freeze v1.0)

Ushbu arxitektura Instagram (`@axion_academy_`) va Facebook Page (`Axion`) uchun **to'g'ridan-to'g'ri Meta Business Suite** orqali sozlangan bo'lib, tashqi serverlar, ManyChat cheklovlari va Meta App Review tekshiruvlarisiz 100% barqaror ishlaydi.

---

## 🌟 Tizim Arxitekturasi

Tizim 2 ta asosiy qatlamdan iborat:

1. **Frequently Asked Questions (FAQ / Icebreakers):**
   - Foydalanuvchi Instagram Direct chatini ochishi bilanoq ekranda 5 ta asosiy savol tugmalari va pastda **Persistent Menu (Doimiy menyu)** ko'rinadi.
   - Har qanday tugma bosilganda darhol mos javob qaytadi.

2. **Custom Keywords (Trigger so'zlar avtomatlashtirishi):**
   - Foydalanuvchi tugmani bosmasdan qo'lda ixtiyoriy matn yozsa ham, Meta tizimi xabardagi kalit so'zlarni taniydi va aynan o'sha mavzuga oid qisqa, aniq javobni qaytaradi.
   - Bitta takroriy javob tashlash muammosi bartaraf etilgan.

---

## 📋 Sozlangan 5 ta Asosiy Yo'nalish va Triggerlar

### 1. 🏥 Narxlar
- **Trigger kalit so'zlar:** `narx`, `narxi`, `narxlar`, `qancha`, `summa`
- **Javob matni:**
  ```text
  🏥 Asosiy xizmatlar narxi:
  • Konsultatsiya va ko‘rik — Bepul
  • Tish davolash (plomba) — 150 000 so‘mdan
  • Tish tozalash va oqartirish — 200 000 so‘mdan

  Barcha narxlar va qabulga yozilish:
  👉 https://t.me/klinikatesttt_bot?start=insta
  ```

### 2. 📍 Manzil va ish vaqti
- **Trigger kalit so'zlar:** `manzil`, `qayerda`, `lokatsiya`, `ish vaqti`, `address`
- **Javob matni:**
  ```text
  📍 Manzilimiz: Toshkent shahri.
  ⏰ Ish vaqti: Dushanba - Shanba, 08:30 dan 18:00 gacha (Yakshanba dam olish kuni).

  Xaritada ko‘rish va navbatga yozilish:
  👉 https://t.me/klinikatesttt_bot?start=insta
  ```

### 3. 👨‍⚕️ Shifokorlar
- **Trigger kalit so'zlar:** `shifokor`, `doktor`, `vrach`, `stomatolog`, `mutaxassis`
- **Javob matni:**
  ```text
  👨‍⚕️ Klinikamizda yuqori toifali stomatolog va terapevt shifokorlar qabul o‘tkazadi.

  Barcha shifokorlar ro‘yxati va ko‘rikka yozilish:
  👉 https://t.me/klinikatesttt_bot?start=insta
  ```

### 4. 📝 Qabulga yozilish
- **Trigger kalit so'zlar:** `qabul`, `navbat`, `yozilish`, `zapis`, `bron`
- **Javob matni:**
  ```text
  Qabulga navbatsiz yozilish uchun rasmiy Telegram botimizdan foydalaning:
  👉 https://t.me/klinikatesttt_bot?start=insta

  Botda bir necha soniyada o‘zingizga qulay vaqtni band qilishingiz mumkin.
  ```

### 5. 📞 Aloqa va telefon
- **Trigger kalit so'zlar:** `aloqa`, `telefon`, `nomer`, `tel`, `raqam`
- **Javob matni:**
  ```text
  📞 Telefon: +998 71 123 45 67
  ⏰ Qo‘ng‘iroqlar: 08:30 dan 18:00 gacha

  Savollar va qabulga yozilish:
  👉 https://t.me/klinikatesttt_bot?start=insta
  ```

---

## 🛠 Avtomatlashtirish Skriptlari (`meta_automation/`)

Ushbu katalogda sozlamalarni Safari orqali avtomatik Meta Business Suite'ga yuklash skriptlari saqlangan:

- **`scripts/run_safari_js.py`** — Safari brauzerida xavfsiz JavaScript kodlarini bajarish uchun AppleScript ko'prigi.
- **`scripts/create_keyword_automation.py`** — Yangi Custom Keywords avtomatlashtirishlarini to'liq avtomatik yaratish, triggerlarni va javob matnini kiritish skripti.
- **`scripts/set_faq_item.py`** — Frequently Asked Questions bo'limidagi savol va javoblarni to'ldirish skripti.
- **`data/keywords/`** — Har bir yo'nalish bo'yicha trigger so'zlar ro'yxatlari.
- **`data/messages/`** — Har bir yo'nalish bo'yicha javob matnlari.

---

## 🔗 Telegram Bot bilan Integratsiya

Har bir javob ostida foydalanuvchini rasmiy Telegram botiga (`@klinikatesttt_bot`) yo'naltiruvchi maxsus havola mavjud:
```
https://t.me/klinikatesttt_bot?start=insta
```
Mijoz botga o'tganda bot uni qabul qiladi, xizmat turini va shifokorni tanlatib, telefon raqamini oladi hamda admin/operator guruhiga navbat buyurtmasi sifatida yuboradi.

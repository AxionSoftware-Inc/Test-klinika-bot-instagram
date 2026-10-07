# 📱 ManyChat orqali Instagram Avtomatlashtirish Qo'llanmasi

Ushbu qo'llanma orqali siz 5-10 daqiqada ManyChat platformasida post/reels kommentlariga va directga avto-javob sozlab, odamlarni Telegram botingizga yo'naltirasiz.

---

## 1-Qadam: ManyChat hisobini Instagramga ulash

1. [ManyChat.com](https://manychat.com) saytiga kiring va **Get Started Free** bosing.
2. Ro'yxatdan o'tishda **Instagram**ni tanlang va Facebook akkauntingiz orqali kiring.
3. Bog'langan **Instagram sahifangizni** tanlang va ulanishga barcha ruxsatlarni (permissions) bering.
4. ManyChat bosh sahifasida akkauntingiz ulanganligini tasdiqlang.

> ⚠️ **Muhim eslatma:** Instagram ilovasida:
> `Sozlamalar (Settings)` -> `Messages and story replies` -> `Message controls` -> **"Connected tools" / "Allow access to messages"** yoqilgan bo'lishi shart!

---

## 2-Qadam: Instagram Direct (DM) ga yozganlar uchun "Default Reply"

Kimdir sizga to'g'ridan-to'g'ri Directga yozsa, birinchi javobni sozlaymiz:

1. ManyChat chap menyusidan **Automation** -> **Default Reply** bo'limiga kiring.
2. **Edit** bosing va blokdagi matnni quyidagiga o'zgartiring:
   ```text
   Assalomu alaykum! Narxlar, shifokorlar va qabulga yozilish bo'yicha barcha ma'lumotlar rasmiy Telegram botimizda 👇
   ```
3. Xabar tagiga **+ Add Button** bosing:
   - Button Name: `🤖 Telegram Botga o'tish`
   - Action: **Open website**
   - URL: `https://t.me/BOT_USERNAME?start=insta` *(BOT_USERNAME o'rniga o'z botingiz nomini qo'ying)*
4. Yuqoridagi **Publish** tugmasini bosing.

---

## 3-Qadam: Reels va Post Kommentlari uchun Avto-javob (Eng muhim joyi!)

Odamlar post yoki videolarga komment yozishi bilan ularning directiga xabar yuborish va komment tagiga javob qaytarish:

1. ManyChat-da **Automation** -> **New Flow** (yoki **New Automation**) tugmasini bosing.
2. **Start from scratch** ni tanlang.
3. Yuqorida **+ Add Trigger** tugmasini bosing.
4. Triggers ro'yxatidan **Instagram** bo'limini tanlab:
   👉 **"User comments on your Post or Reel"** ni bosing.

### Trigger Sozlamalari:
- **Which post?**:
  - `Any post or Reel` (Barcha post va reelslar uchun) yoki o'sha ommalashgan `Specific post/Reel` ni tanlang.
- **Comments include these keywords**:
  - Agar faqat ma'lum so'zlarga bo'lsa: `narxi, qayerda, info, manzil, nomer, qabul` so'zlarini vergul bilan kiriting.
  - Agar barcha kommentlarga bo'lsa: **"Any comment"** opsiyasini tanlang.

### Komment tagiga ommaviy javob (Auto-reply in comments):
ManyChat quyida sizdan **Public auto-response in comments** so'raydi.
Spamga tushmaslik va Instagram algoritmlari bloklamasligi uchun **4-5 xil har xil variant** kiriting (ManyChat ularni navbatma-navbat tasodifiy tanlaydi):

> 1-variant: `Directingizga to'liq ma'lumot va qabulga yozilish havolasini yubordik! ✅`  
> 2-variant: `Xabaringizni direct orqali yo'lladik, tekshirib ko'ring 📩`  
> 3-variant: `Assalomu alaykum, lichkangizga batafsil ma'lumot jo'natildi 😊`  
> 4-variant: `Barcha narxlar va qabul linki directingizga jo'natildi! 👍`  
> 5-variant: `Directingizga qarang, to'liq ma'lumotni yubordik ✨`

---

## 4-Qadam: Directga yuboriladigan xabar (Direct Message Step)

Komment yozgan odamga avtomatik tarzda yuboriladigan xabar bloki:

1. Xabar matniga kiriting:
   ```text
   Assalomu alaykum! Xabaringiz uchun rahmat.

   Narxlar, to‘liq ma'lumot va shifokorlar qabuliga navbatga yozilish Telegram botimizda 👇
   ```
2. Xabar tagiga tugma qo'shing (**+ Add Button**):
   - **Button Title**: `🤖 Telegram Botga o‘tish`
   - **Type**: `Open Website`
   - **URL**: `https://t.me/BOT_USERNAME?start=insta`
3. Yuqoridagi **Publish** tugmasini bosing.

---

## 5-Qadam: Instagram Direct qo'ng'iroqlarini (Audio Call) o'chirish

Instagramdan to'xtovsiz telefon qilaverishlarini to'xtatish uchun:

1. Instagram ilovasiga kiring (telefoningizdan).
2. **Profile** -> **Settings and privacy (Sozlamalar va maxfiylik)**.
3. **Messages and story replies (Xabarlar va storiya javoblari)**.
4. **Who can call you (Kimlar qo'ng'iroq qilishi mumkin)** bo'limiga kiring:
   - Tanlang: **Off** (yoki **"People you follow"** - faqat siz kuzatadiganlar).
5. Bio (profil tavsifi)ga yozib qo'ying:
   *"Qo'ng'iroqlar qabul qilinmaydi. Qabulga yozilish Telegram orqali: t.me/BOT_USERNAME?start=insta"*

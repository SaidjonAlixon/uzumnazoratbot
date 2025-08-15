# MarketBot - UZUM Market Telegram Bot

UZUM Market sotuvchilari uchun Telegram bot. Bu bot orqali siz o'zingizning biznes ma'lumotlaringizni ko'rishingiz mumkin.

## 🚀 Railway da ishga tushirish (Tavsiya etiladi)

### 1. Fork this repository

### 2. Railway da ishga tushirish

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/SaidjonAlixon/uzumnazoratbot)

### 3. Environment Variables ni sozlash

Railway da quyidagi environment variables larni o'rnating:

- `BOT_TOKEN` - @BotFather dan olingan bot token
- `DEFAULT_ADMIN_ID` - Sizning Telegram User ID niz
- `ADMIN_USERNAME` - Sizning Telegram username niz
- `SUPPORT_GROUP` - Qo'llab-quvvatlash guruhi havolasi

### 4. Deploy

Deploy tugmasini bosing va build tugashini kuting.

## 🖥️ Lokal ishga tushirish

### 1. Kerakli kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Telegram Bot Token olish
1. [@BotFather](https://t.me/botfather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username ni kiriting
4. Bot token ni saqlang

### 3. Konfiguratsiya
`.env` fayl yarating va quyidagilarni yozing:
```env
BOT_TOKEN=your_bot_token_here
DEFAULT_ADMIN_ID=your_admin_id_here
ADMIN_USERNAME=your_admin_username_here
SUPPORT_GROUP=https://t.me/your_support_group
```

### 4. Botni ishga tushirish
```bash
python main.py
```

## 📱 Bot funksiyalari

### 🔑 API kalit boshqaruvi
- API kalitni kiritish va saqlash
- API kalitni o'zgartirish
- API kalitni o'chirish
- API holatini tekshirish

### 🔐 Admin Panel
- Foydalanuvchilarni boshqarish
- Xabar yuborish (broadcast)
- Foydalanuvchilarni bloklash/blokni olib tashlash
- Statistika va hisobotlar
- API kalitlarni ko'rish
- Admin foydalanuvchilarni boshqarish

### 👥 Qo'llab-quvvatlash
- Qo'llab-quvvatlash guruhiga qo'shilish
- Texnik yordam va savol-javoblar
- Foydalanuvchilar bilan tajriba almashish

### 📦 FBS (Fulfillment by Seller) - OpenAPI v2
- Buyurtmalar ro'yxati (yangi statuslar bilan)
- Buyurtmalar statistikasi (do'kon bo'yicha)
- Qoldiqlar va yangilash
- Qaytarish sabablari
- Buyurtma tafsilotlari
- 🔍 Yo'qolgan tovarlar ro'yxati
- 📊 Yo'qolgan tovarlar statistikasi

### 📊 FBS Statistika - OpenAPI v2
- Do'kon bo'yicha statistika
- Sana bo'yicha statistika
- Status bo'yicha statistika
- Qoldiq statistikasi
- Moliyaviy statistika

### 💰 Moliyaviy hisobot - OpenAPI v2
- Xarajatlar (do'kon va sana bo'yicha)
- Buyurtmalar (guruhlash va filtrlash)
- To'lov ma'lumotlari
- Komissiya ma'lumotlari

### 💳 Hisob-fakturalar - OpenAPI v2
- Hisob-fakturalar ro'yxati (sahifalash bilan)
- Qaytarishlar (turi va holat bilan)
- Faktura mahsulotlari
- Do'kon fakturaları

### 🛍 Mahsulotlar - OpenAPI v2
- Mahsulot qidirish (rang, filtrlash bilan)
- Narx yangilash (yangi format)
- SKU ma'lumotlari
- Mahsulot holati

### 🏪 Do'konlar
- Do'konlar ro'yxati
- Do'kon ma'lumotlari

## 🛠 Texnik ma'lumotlar

- **Python**: 3.11+
- **Telegram Bot API**: pytelegrambotapi
- **HTTP Client**: requests
- **Database**: SQLite3
- **Language**: O'zbek tili

## 📁 Fayl tuzilishi

```
MarketBot/
├── main.py              # Asosiy bot dasturi
├── config.py            # Konfiguratsiya
├── bot_handlers.py      # Bot funksiyalari
├── api_client.py        # UZUM Market API
├── database.py          # Ma'lumotlar bazasi
├── keyboards.py         # Bot klaviaturalari
├── utils.py             # Yordamchi funksiyalar
├── users.db             # Ma'lumotlar bazasi
└── README.md            # Bu fayl
```

## 🔧 API sozlamalari

Bot UZUM Market Seller OpenAPI v2 bilan ishlaydi:
- Base URL: `https://api-seller.uzum.uz/api/seller-openapi/`
- API kalit: Foydalanuvchi tomonidan kiritiladi
- OpenAPI versiya: 3.0.0
- Yangi endpointlar va parametrlar qo'shildi

### 🆕 Yangi funksiyalar:
- **FBS Buyurtmalar**: Yangi statuslar va filtrlari
- **Moliyaviy hisobotlar**: Do'kon va sana bo'yicha filtrlash
- **Hisob-fakturalar**: Sahifalash va qaytarish turlari
- **Mahsulotlar**: Rang, filtrlash va SKU ma'lumotlari
- **Do'konlar**: Batafsil ma'lumotlar

## 📞 Yordam

Bot ichida `/help` buyrug'ini bosing yoki "📞 Yordam" tugmasini bosing.

## 📝 Changelog

### v2.0.0 (2025-08-15)
- ✅ OpenAPI v2 spetsifikatsiyasiga o'tish
- ✅ Yangi FBS buyurtmalar endpointlari
- ✅ Yangi FBS statistika funksiyalari
- ✅ Yangi yo'qolgan tovarlar funksiyasi
- ✅ Yangi qo'llab-quvvatlash guruhi
- ✅ Yangi admin panel va boshqaruv
- ✅ Yangi moliyaviy hisobot filtrlari
- ✅ Yangi hisob-faktura sahifalash
- ✅ Yangi mahsulot qidirish parametrlari
- ✅ Yangi buyurtma statuslari
- ✅ Yangi qaytarish turlari

### v1.0.0 (2025-08-15)
- ✅ Asosiy bot funksiyalari
- ✅ UZUM Market API integratsiyasi
- ✅ SQLite ma'lumotlar bazasi
- ✅ O'zbek tilida interfeys

## ⚠️ Eslatma

- API kalitingizni hech kimga bermang
- Bot faqat UZUM Market sotuvchilari uchun mo'ljallangan
- Barcha amallar o'zbek tilida amalga oshiriladi
- Yangi OpenAPI v2 funksiyalari faqat yangi API versiyasida ishlaydi

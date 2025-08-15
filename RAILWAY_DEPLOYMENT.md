# Railway da MarketBot ni ishga tushirish qo'llanmasi

## 🚀 1. GitHub Repository tayyorlash

### 1.1 Repository ni fork qilish
1. [MarketBot repository](https://github.com/yourusername/MarketBot) ga boring
2. "Fork" tugmasini bosing
3. O'zingizning GitHub account ga fork qiling

### 1.2 Repository ni clone qilish
```bash
git clone https://github.com/YOUR_USERNAME/MarketBot.git
cd MarketBot
```

### 1.3 O'zgarishlarni commit qilish
```bash
git add .
git commit -m "Railway deployment uchun tayyorlandi"
git push origin main
```

## 🚀 2. Railway da ishga tushirish

### 2.1 Railway ga kirish
1. [Railway.app](https://railway.app) ga boring
2. GitHub bilan login qiling
3. "New Project" tugmasini bosing

### 2.2 Repository ni tanlash
1. "Deploy from GitHub repo" ni tanlang
2. O'zingizning MarketBot repository sini tanlang
3. "Deploy Now" tugmasini bosing

### 2.3 Environment Variables ni sozlash

Railway da quyidagi environment variables larni o'rnating:

| Variable Name | Value | Izoh |
|---------------|-------|------|
| `BOT_TOKEN` | `your_bot_token_here` | @BotFather dan olingan bot token |
| `DEFAULT_ADMIN_ID` | `your_admin_id_here` | Sizning Telegram User ID niz |
| `ADMIN_USERNAME` | `your_admin_username_here` | Sizning Telegram username niz |
| `SUPPORT_GROUP` | `https://t.me/your_support_group` | Qo'llab-quvvatlash guruhi havolasi |

**Environment Variables ni qo'shish:**
1. Railway project da "Variables" bo'limiga boring
2. "New Variable" tugmasini bosing
3. Har bir variable ni alohida qo'shing

### 2.4 Deploy

1. "Deploy" tugmasini bosing
2. Build jarayoni tugashini kuting
3. "Deployments" bo'limida status "Deployed" bo'lishini tekshiring

## 🔧 3. Telegram Bot Token olish

### 3.1 @BotFather bilan ishlash
1. [@BotFather](https://t.me/botfather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: "My MarketBot")
4. Bot username ni kiriting (masalan: `my_market_bot`)
5. Bot token ni saqlang

### 3.2 Bot Token ni Railway ga qo'yish
1. Railway da `BOT_TOKEN` variable ni yarating
2. @BotFather dan olingan token ni yozing

## 👤 4. Admin ID va Username olish

### 4.1 Telegram User ID olish
1. [@userinfobot](https://t.me/userinfobot) ga boring
2. `/start` buyrug'ini yuboring
3. Sizning User ID nizni saqlang

### 4.2 Username tekshirish
1. Telegram da o'zingizning profile nizga boring
2. Username ni tekshiring (agar yo'q bo'lsa, yarating)

### 4.3 Railway ga qo'yish
1. `DEFAULT_ADMIN_ID` ga User ID nizni yozing
2. `ADMIN_USERNAME` ga username nizni yozing

## 🌐 5. Qo'llab-quvvatlash guruhi

### 5.1 Guruh yaratish
1. Telegram da yangi guruh yarating
2. Guruh havolasini oling
3. Railway da `SUPPORT_GROUP` ga qo'ying

## ✅ 6. Tekshirish

### 6.1 Bot ishlayotganini tekshirish
1. Railway da "Deployments" bo'limiga boring
2. Status "Deployed" ekanligini tekshiring
3. "View Logs" tugmasini bosing va xatolik yo'qligini tekshiring

### 6.2 Bot bilan ishlash
1. Telegram da o'zingizning bot nizga boring
2. `/start` buyrug'ini yuboring
3. Bot javob berayotganini tekshiring

### 6.3 Admin panel
1. `/admin` buyrug'ini yuboring
2. Admin panel ochilayotganini tekshiring

## 🚨 7. Xatoliklar va yechimlar

### 7.1 Bot javob bermaydi
- Railway da environment variables to'g'ri o'rnatilganini tekshiring
- Bot token to'g'ri ekanligini tekshiring
- Logs da xatolik bor-yo'qligini tekshiring

### 7.2 Admin panel ochilmaydi
- `DEFAULT_ADMIN_ID` to'g'ri o'rnatilganini tekshiring
- Telegram da o'zingizning ID nizni tekshiring

### 7.3 Database xatoliklari
- Railway da SQLite database to'g'ri ishlayotganini tekshiring
- Logs da database xatoliklari bor-yo'qligini tekshiring

## 📱 8. Bot funksiyalari

Bot muvaffaqiyatli ishga tushgandan so'ng:

- ✅ `/start` - Botni ishga tushirish
- ✅ `/help` - Yordam
- ✅ `/api` - API kalitni boshqarish
- ✅ `/menu` - Asosiy menyu
- ✅ `/admin` - Admin panel (faqat admin uchun)

## 🔗 9. Foydali havolalar

- [Railway Documentation](https://docs.railway.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python Flask](https://flask.palletsprojects.com/)
- [SQLite](https://www.sqlite.org/)

## 📞 10. Yordam

Agar muammo bo'lsa:
1. Railway logs ni tekshiring
2. GitHub Issues da muammoni yozing
3. Qo'llab-quvvatlash guruhiga murojaat qiling

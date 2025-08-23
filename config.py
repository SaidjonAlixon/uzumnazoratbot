"""
Konfiguratsiya fayli
Bot va API sozlamalari
"""

import os
from dotenv import load_dotenv

# Environment variables ni yuklash
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "7666059929:AAFCIWLUJFMFg6Terd0w7av7aNTgy6hAwUQ")

# Ma'lumotlar bazasi fayli
DATABASE_FILE = "users.db"

# API Base URL (rasmdan olingan URL asosida)
API_BASE_URL = "https://api-seller.uzum.uz/api/seller-openapi"

# API Headers
API_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Bot sozlamalari
BOT_CONFIG = {
    "parse_mode": "HTML",
    "disable_web_page_preview": True
}

# Admin panel sozlamalari
ADMIN_CONFIG = {
    "default_admin_id": int(os.getenv("DEFAULT_ADMIN_ID", "7517807386")),  # Environment dan o'qish
    "support_group": os.getenv("SUPPORT_GROUP", "https://t.me/unb_uz"),
    "admin_username": os.getenv("ADMIN_USERNAME", "Tolov_admini_btu"),  # Environment dan o'qish
    "admin_permissions": ["ALL"]  # Barcha huquqlar
}

# O'zbek tilidagi matnlar
MESSAGES = {
    "welcome": """🛍 <b>Uzum business botiga xush kelibsiz!</b>

Bu bot orqali siz o'zingizning biznes ma'lumotlaringizni ko'rishingiz mumkin.

Boshlash uchun 🔄 API kiritish ✅ tugmasini bosing!""",
    
    "welcome_no_api": """🛍 <b>Uzum business botiga xush kelibsiz!</b>

Bu bot orqali siz o'zingizning biznes ma'lumotlaringizni ko'rishingiz mumkin.

Boshlash uchun 🔄 API kiritish ✅ tugmasini bosing!""",
    
    "help": """📋 <b>Bot buyruqlari:</b>

/start - Botni qayta ishga tushirish
/api - API kalitini boshqarish
/menu - Asosiy menyu
/status - API holati
/help - Bu yordam

<i>API kalitingizni kiritganingizdan so'ng barcha imkoniyatlardan foydalanishingiz mumkin.</i>""",
    
    "api_prompt": "🔑 API kalitingizni yuboring:\n\nAPI kalitni olish yuqoridagi rasmda ketma ket ko'rsatilgan shunday holatda yuboring iltimos e'tiborli bo'ling!",
    
    "api_saved": "✅ <b>API kalit muvaffaqiyatli saqlandi!</b>\n\nEndi barcha imkoniyatlardan foydalanishingiz mumkin.",
    
    "api_invalid": "❌ <b>API kalit noto'g'ri yoki ishlamayapti!</b>\n\nIltimos, to'g'ri API kalitni kiriting.",
    
    "api_testing": "🔄 <b>API kalit tekshirilmoqda...</b>",
    
    "no_api": "⚠️ <b>API kalit kiritilmagan!</b>\n\nIltimos, avval API kalitingizni kiriting.",
    
    "main_menu": "📊 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:",
    
    "api_status_connected": "✅ <b>API ulangan</b>\n\nBarcha imkoniyatlar mavjud.",
    
    "api_status_disconnected": "❌ <b>API ulanmagan</b>\n\nAPI kalitingizni tekshiring.",
    
    "error": "❌ <b>Xatolik yuz berdi!</b>\n\nIltimos, qaytadan urinib ko'ring.",
    
    "data_loading": "📥 <b>Ma'lumotlar yuklanmoqda...</b>",
    
    "no_data": "📭 <b>Ma'lumotlar topilmadi</b>",
    
    "api_deleted": "🗑 <b>API kalit o'chirildi</b>\n\nYangi API kalit kiritish uchun /api buyrug'ini bosing."
}

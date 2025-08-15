"""
Telegram bot klaviaturalari
O'zbek tilida tugmalar va menyular
"""

from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

def get_main_menu_keyboard(is_admin=False):
    """Asosiy menyu klaviaturasi"""
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # FBS bo'limi
    keyboard.add(
        KeyboardButton("📦 FBS Buyurtmalar"),
        KeyboardButton("📊 FBS Statistika")
    )
    
    # Moliya bo'limi
    keyboard.add(
        KeyboardButton("💰 Moliyaviy hisobot"),
        KeyboardButton("💳 Hisob-fakturalar")
    )
    
    # Mahsulotlar va do'konlar
    keyboard.add(
        KeyboardButton("🛍 Mahsulotlar"),
        KeyboardButton("🏪 Do'konlarim")
    )
    
    # Sozlamalar va yordam
    keyboard.add(
        KeyboardButton("⚙️ Sozlamalar"),
        KeyboardButton("📞 Yordam")
    )
    
    # Qo'llab-quvvatlash
    keyboard.add(
        KeyboardButton("👥 Qo'llab quvvatlash guruhi")
    )
    
    # Admin panel (faqat admin uchun)
    if is_admin:
        keyboard.add(
            KeyboardButton("🔐 Admin Panel")
        )
    
    return keyboard

def get_fbs_menu_keyboard():
    """FBS bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📋 Buyurtmalar ro'yxati", callback_data="fbs_orders"),
        InlineKeyboardButton("📈 Buyurtmalar soni", callback_data="fbs_orders_count")
    )
    
    keyboard.add(
        InlineKeyboardButton("📦 Qoldiqlar", callback_data="fbs_stocks"),
        InlineKeyboardButton("🔄 Qaytarish sabablari", callback_data="fbs_return_reasons")
    )
    
    keyboard.add(
        InlineKeyboardButton("📋 Qoldiqlarni yangilash", callback_data="fbs_update_stocks"),
        InlineKeyboardButton("🆔 Buyurtma tafsiloti", callback_data="fbs_order_details")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔍 Yo'qolgan tovarlar", callback_data="fbs_missing_items"),
        InlineKeyboardButton("📊 Yo'qolgan tovarlar statistikasi", callback_data="fbs_missing_statistics")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_fbs_statistics_keyboard():
    """FBS statistika klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📊 Buyurtmalar statistikasi", callback_data="fbs_orders_count"),
        InlineKeyboardButton("📈 Do'kon bo'yicha statistika", callback_data="fbs_shop_statistics")
    )
    
    keyboard.add(
        InlineKeyboardButton("📅 Sana bo'yicha statistika", callback_data="fbs_date_statistics"),
        InlineKeyboardButton("🔄 Status bo'yicha statistika", callback_data="fbs_status_statistics")
    )
    
    keyboard.add(
        InlineKeyboardButton("📦 Qoldiq statistikasi", callback_data="fbs_stock_statistics"),
        InlineKeyboardButton("💰 Moliyaviy statistika", callback_data="fbs_finance_statistics")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_finance_menu_keyboard():
    """Moliya bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("💸 Xarajatlar", callback_data="finance_expenses"),
        InlineKeyboardButton("📊 Buyurtmalar", callback_data="finance_orders")
    )
    
    keyboard.add(
        InlineKeyboardButton("💳 To'lov ma'lumotlari", callback_data="finance_payment_info"),
        InlineKeyboardButton("💰 Komissiya", callback_data="finance_commission")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_invoice_menu_keyboard():
    """Hisob-faktura bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📄 Hisob-fakturalar", callback_data="invoices"),
        InlineKeyboardButton("↩️ Qaytarishlar", callback_data="invoice_returns")
    )
    
    keyboard.add(
        InlineKeyboardButton("📋 Faktura mahsulotlari", callback_data="invoice_products"),
        InlineKeyboardButton("🏪 Do'kon fakturaları", callback_data="shop_invoices")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_product_menu_keyboard():
    """Mahsulot bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔍 Mahsulot qidirish", callback_data="product_search"),
        InlineKeyboardButton("💰 Narx yangilash", callback_data="product_update_price")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_shop_menu_keyboard():
    """Do'kon bo'limi klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("🏪 Do'konlar ro'yxati", callback_data="shops_list")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_settings_keyboard():
    """Sozlamalar klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("🔑 API kalitini o'zgartirish", callback_data="change_api"),
        InlineKeyboardButton("🗑 API kalitini o'chirish", callback_data="delete_api"),
        InlineKeyboardButton("🔍 API holatini tekshirish", callback_data="check_api_status")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_api_management_keyboard():
    """API boshqaruv klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    keyboard.add(
        InlineKeyboardButton("🔄 API kiritish ✅", callback_data="add_api"),
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard

def get_confirmation_keyboard(action: str):
    """Tasdiqlash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("✅ Ha", callback_data=f"confirm_{action}"),
        InlineKeyboardButton("❌ Yo'q", callback_data="cancel_action")
    )
    
    return keyboard

def get_order_action_keyboard(order_id: str):
    """Buyurtma amallar klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_order_{order_id}"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_order_{order_id}")
    )
    
    keyboard.add(
        InlineKeyboardButton("📋 Tafsilotlar", callback_data=f"order_details_{order_id}"),
        InlineKeyboardButton("🔙 Orqaga", callback_data="fbs_orders")
    )
    
    return keyboard

def get_back_to_main_keyboard():
    """Asosiy menyuga qaytish klaviaturasi"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🔙 Asosiy menyu", callback_data="main_menu")
    )
    return keyboard

def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str):
    """Sahifalash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    buttons = []
    
    # Oldingi sahifa
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️", callback_data=f"{prefix}_page_{current_page - 1}"))
    
    # Joriy sahifa
    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="current_page"))
    
    # Keyingi sahifa
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("➡️", callback_data=f"{prefix}_page_{current_page + 1}"))
    
    if buttons:
        keyboard.row(*buttons)
    
    keyboard.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")
    )
    
    return keyboard
